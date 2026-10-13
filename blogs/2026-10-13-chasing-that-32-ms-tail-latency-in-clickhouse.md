---
title: "Chasing that 32 ms tail latency in ClickHouse"
date: "2026-10-13T08:49:51.685Z"
author: "Kavi Kanagaraj"
category: "Engineering"
excerpt: "A customer saw an extra ~32 ms on simple SELECT queries after idle periods. We traced it to unbatched Native protocol metadata packets overflowing a reset TCP congestion window, reproduced it with network namespaces, and fixed it by batching them."
---

# Chasing that 32 ms tail latency in ClickHouse

TL;DR: In the ClickHouse Native protocol, clients must wait for an `EndOfStream` packet to complete a query. Between the result `Data` packets and `EndOfStream`, ClickHouse sends several metadata packets (`Logs`, `Progress`, `ProfileEvents`). When combined with `TCP_NODELAY` and a reset TCP congestion window (`cwnd`) after an idle period, these unbatched packets can exceed the window, forcing an additional round trip. We reproduced this deterministically using Linux network namespaces and reduced tail latency by batching those metadata packets at the application layer.

## The problem {#the_problem}

One of our customers observed an additional \~32 ms of latency on simple `SELECT` queries between the client and the server.

In this customer's setup, the client and server are \~32 ms apart (egress). When a connection sat idle for 2 seconds or longer, the very next query took \~64 ms end to end: 2× the round-trip time (RTT) instead of the expected \~32 ms (1× RTT).

We had to work out what exactly was causing this additional round trip.

The investigation led to some interesting lessons about both the Linux TCP stack and the ClickHouse Native protocol.

## ClickHouse Native protocol 101 {#clickhouse_native_protocol_101}

ClickHouse server supports a wide range of protocols. HTTP and Native TCP are the two primary ways to talk to ClickHouse server. The customer's problem involves the Native TCP protocol, so that is our focus. It's important to know a little bit about how the ClickHouse Native protocol works to understand the customer's problem.

The ClickHouse Native protocol is a stateful protocol built on top of the TCP transport protocol. Client and server exchange different protocol messages in different phases (Handshake, INSERT or SELECT). The [official specification for the TCP native protocol](https://clickhouse.com/docs/reference/interfaces/specs/NativeProtocol) describes how it works in detail.

Here is a simplified version of how SELECT queries work at the protocol level.

1. Client sends `Query` (contains SQL, settings, flags, etc).
2. Server streams `Data` packets containing actual result rows.
3. Server also sends intermediate metadata packets (`ProfileEvents`, `Progress`, `Logs`).
4. Server sends `EndOfStream` (EOS) to mark that particular query is complete.

<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/taillatency_oct2026_video1_native_query_phase_static_flow_3d7dc1687c.mp4" type="video/mp4" />
</video>

What this means for the client is that it has to keep reading from the connection until it receives the `EndOfStream` packet for that particular query, before that query is considered done.

## TCP congestion window 101 {#tcp_congestion_window_101}

TCP is the [well-known transport-level protocol](https://datatracker.ietf.org/doc/html/rfc9293), and how it works is out of scope for this article. Here we focus primarily on two characteristics of the TCP protocol that are needed to understand the customer problem precisely.

1. Congestion window
2. TCP_NODELAY (Nagle's algorithm)

### Congestion window

The congestion window (unlike the receiver window) is neither configured on the client side nor on the server side. It's a value that usually starts small (based on `initcwnd`, the initial congestion window value in Linux) and keeps increasing as long as the network between client and server doesn't face any congestion problems (for example, the server can send that number of TCP packets before waiting for an ACK from the client). This is commonly known as [TCP slow start](https://en.wikipedia.org/wiki/TCP_congestion_control#Slow_start).

Basically, TCP limits the amount of unacknowledged data in flight using this congestion window (`cwnd`).

The `initcwnd` value is usually 10 MSS (Maximum Segment Size), but sometimes differs. In the customer's case it was 8 MSS.

One crucial thing to notice about the congestion window is that it keeps growing, and if the connection is idle for some time (e.g. 2 seconds in the customer's case), the Linux TCP stack resets the current congestion window size back to the `initcwnd` value. This idle time is called the Retransmission Timeout (RTO), and it is calculated dynamically based on the RTT of the network, with lower (200 milliseconds) and upper (120 seconds) bounds in the Linux TCP stack.

<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/taillatency_oct2026_video2_tcp_congestion_window_50039583bc.mp4" type="video/mp4" />
</video>

### TCP_NODELAY (Nagle's algorithm)

Given its age, one of TCP's default behaviors is to batch socket writes before flushing them to the network, to reduce network overhead. This is often called [Nagle's algorithm](https://en.wikipedia.org/wiki/Nagle%27s_algorithm), and it happens inside Linux's TCP stack, where the application has almost no control.

Modern low-latency systems (like ClickHouse) disable this by setting `TCP_NODELAY=1`, instructing the kernel to send socket writes immediately.

<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/taillatency_oct2026_video3_tcp_nodelay_comparison_4565317d79.mp4" type="video/mp4" />
</video>

The catch here is that if `TCP_NODELAY` is enabled and an application issues multiple socket writes for those metadata packets (`ProfileEvents`, `Log`, `Progress`), each of those writes becomes an individual TCP segment on the wire.

If the server issues more small writes than the reduced `cwnd` can hold, the kernel must stop and wait for a client ACK before sending the remaining packets, incurring an extra round-trip penalty.

<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/taillatency_oct2026_video4_tcp_nodelay_window_example_cc37733e24.mp4" type="video/mp4" />
</video>

## Reproducing the exact customer problem {#reproducing_the_exact_customer_problem}

Reproducing the customer problem requires simulating the same network RTT between the client and the server (\~32 ms) to make the problem visible. For simplicity, we run all the queries (with an idle period of 2 seconds) on a single TCP connection over the Native protocol between the client and the server.

Two pieces are involved here:

1. A [Go program](https://gist.github.com/kavirajk/62dfcc661ba004cb09f5f59ea5d52750) that runs actual queries to observe the problem the customer faced (additional \~32 ms tail latency)
2. A ClickHouse server within a network namespace with the customer's network conditions applied to it (simulating \~32 ms network egress delay).

### Network setup

We could have used Docker or Podman to create the network namespace. However, we deliberately set it up manually using `netns` to make the network simulation easier to understand.

We then used `tc` (traffic control) to simulate a 32 ms WAN delay between the client and the server. We also configured the initial TCP congestion window to 8 MSS (`initcwnd 8`).

1. Have a ClickHouse binary (< 26.9) (the one we use to reproduce the issue)

<pre><code type='click-ui' language='bash'>
mkdir -p ~/chbin && cd ~/chbin
wget https://builds.clickhouse.com/26.8/amd64/clickhouse && chmod +x ./clickhouse
</code></pre>

2. Create a network to simulate the customer infrastructure (client and server \~32 ms apart).

<pre><code type='click-ui' language='bash'>
# Create a dedicated network namespace for ClickHouse
sudo ip netns add chsrv

# Create a virtual ethernet pair
sudo ip link add veth-host type veth peer name veth-ch
sudo ip link set veth-ch netns chsrv

# Assign IP addresses
sudo ip addr add 10.99.0.1/24 dev veth-host
sudo ip link set veth-host up
sudo ip netns exec chsrv ip addr add 10.99.0.2/24 dev veth-ch
sudo ip netns exec chsrv ip link set veth-ch up
sudo ip netns exec chsrv ip link set lo up

# Add a 32ms egress delay and set initial cwnd to 8
sudo ip netns exec chsrv tc qdisc add dev veth-ch root netem delay 32ms
sudo ip netns exec chsrv ip route change 10.99.0.0/24 dev veth-ch \
    proto kernel scope link src 10.99.0.2 initcwnd 8
</code></pre>

3. Verify the simulated network (you should see \~32 ms)

<pre><code type='click-ui' language='bash'>
ping -c 5 10.99.0.2
</code></pre>

```shell
PING 10.99.0.2 (10.99.0.2) 56(84) bytes of data.
64 bytes from 10.99.0.2: icmp_seq=1 ttl=64 time=32.0 ms
64 bytes from 10.99.0.2: icmp_seq=2 ttl=64 time=32.1 ms
64 bytes from 10.99.0.2: icmp_seq=3 ttl=64 time=32.0 ms
64 bytes from 10.99.0.2: icmp_seq=4 ttl=64 time=32.0 ms
64 bytes from 10.99.0.2: icmp_seq=5 ttl=64 time=32.1 ms
```

### Client program

This [Go program](https://gist.github.com/kavirajk/62dfcc661ba004cb09f5f59ea5d52750) runs simple queries over an established connection with a 2-second idle period between the queries. We also separate overall query latency and tail latency (the time between the last `Data` packet and the `EndOfStream` packet) to observe the tail latency (both before and after the patch) more clearly.

The Go program runs N identical `SELECT max(id)` queries on one reused connection and splits each query's latency into:

1. `first_row` (the query result itself) and
2. `tail` (first row → end of stream).

**`tail` is the key here: healthy ≈ 0 ms; stalled = exactly 1× RTT.**

### Run the test

1. Run the server inside the simulated network

<pre><code type='click-ui' language='bash'>
mkdir -p /tmp/chdata
cd ~/chbin
sudo ip netns exec chsrv sudo -u "$USER" \
    ./clickhouse server -- --listen_host=0.0.0.0 --path=/tmp/chdata/
</code></pre>

2. Create a table and rows for the experiments

<pre><code type='click-ui' language='bash'>
cd ~/chbin
./clickhouse client --host 10.99.0.2 -q \
  "CREATE TABLE IF NOT EXISTS benchmark_test (id UInt64) ENGINE=MergeTree ORDER BY id"
./clickhouse client --host 10.99.0.2 -q \
  "INSERT INTO benchmark_test SELECT number FROM numbers(939)"
</code></pre>

3. Run the [Go program](https://gist.github.com/kavirajk/62dfcc661ba004cb09f5f59ea5d52750) to see the issue in action

<pre><code type='click-ui' language='bash'>
go run issue.go
</code></pre>

You should see results similar to the following:

```shell
addr=10.99.0.2:9000  sleep=2s  profile_events=true
query: SELECT max(id) FROM benchmark_test

query  1: first_row=  33.17ms  eos=  65.31ms  tail=  32.13ms  (rows=1)
query  2: first_row=  33.65ms  eos=  65.19ms  tail=  31.54ms  (rows=1)
query  3: first_row=  33.44ms  eos=  65.02ms  tail=  31.57ms  (rows=1)
query  4: first_row=  33.30ms  eos=  65.10ms  tail=  31.80ms  (rows=1)
query  5: first_row=  33.19ms  eos=  65.11ms  tail=  31.92ms  (rows=1)
```

**Observation:** The first row arrived in \~33 ms (1× RTT), but the connection stalled for another **\~32 ms (tail latency)** waiting for the `EndOfStream` packet train.

## Root cause {#root_cause}

The additional RTT (\~32 ms) comes from the fact that once the congestion window is reset (from a large value to `initcwnd`, which was 8 in the customer's case) after a 2-second idle period, the server cannot send all the remaining packets (Data + those metadata packets) in a single round trip.

The server sent 8 TCP segments, ran out of `cwnd` space and paused until the client ACKed the first batch, costing an additional 32 ms full round trip.

## Patch and the results {#patch_and_the_results}

There are some workarounds to make this problem less likely to happen:

1. Disable `ProfileEvents` on [the server side](https://clickhouse.com/docs/reference/settings/session-settings/send#send_profile_events) (`ProfileEvents` packets are one of the causes of the large number of TCP packets on the wire)
2. Disable resetting the connection's congestion window (`cwnd`) to its initial value (`initcwnd`) after an idle period (`tcp_slow_start_after_idle=0`) on the server node (GKE in the customer's case; it's also [recommended for high-performance TCP by Google Cloud](https://docs.cloud.google.com/compute/docs/networking/tcp-optimization-for-network-performance-in-gcp-and-hybrid#disable-slow-start))
3. Increase `initcwnd` (default is 10, the customer's case is 8) on the server node
4. Improve the ClickHouse Native protocol to create fewer TCP packets with application-level batching.
5. Use the `TCP_CORK` option instead of `TCP_NODELAY`

Unfortunately, in this case the customer had little control over workarounds (1), (2) and (3), so the only viable options were (4) and (5). Option 5 (`TCP_CORK`) [sounded interesting](https://catonmat.net/tcp-cork), but it has a few drawbacks:

- The kernel TCP stack still has full control over filling those TCP segments
- It is specific to the Linux kernel

Option (4) also sounded like a nice improvement on the server side anyway. So we decided to make the ClickHouse Native protocol create fewer TCP packets with application-level batching at the end of the query.

[The patch is simple](https://github.com/ClickHouse/ClickHouse/pull/111034): we group these metadata packets at the application level into a single socket write (hence potentially fewer TCP packets), which can then be sent in the minimum number of round trips even when the congestion window is reset.

There is one catch: we cannot blindly group all the metadata packets, as some packets like `Progress` are time-sensitive and have to be delivered to the client immediately (imagine the client wants to know the real progress of the query, and server-side batching delays it, communicating the wrong progress state).

<video autoplay="1" muted="1" loop="1" controls="0">
  <source src="https://clickhouse.com/uploads/taillatency_oct2026_video5_native_metadata_batching_b3c73969fb.mp4" type="video/mp4" />
</video>

We can validate that our batching is working by looking at the captured TCP packets: the total number of TCP packets the server creates for the same query is almost halved. That removes the \~32 ms of additional tail latency we originally observed.

### Validation

Assuming ClickHouse server runs on port 9000.

#### Before the patch

If you run the same Go script while capturing the TCP PUSH packets (`PSH`, the ones where actual application data gets transferred) via `tshark`:

<pre><code type='click-ui' language='bash'>
tshark -i veth-host -f 'tcp port 9000 and greater 60 and tcp[tcpflags] & tcp-push != 0' -w capture.pcap
</code></pre>

```shell
Capturing on 'veth-host'
50
```

Even before looking at the captured pcap files, we can see it captured a total of 50 such TCP packets from server to client.

Also notice the many tiny TCP segments:

<pre><code type='click-ui' language='bash'>
tshark -r capture.pcap -Y 'tcp.flags.push == 1 && tcp.len &gt; 0' -T fields -e tcp.len |
 sort -n | uniq -c | awk 'BEGIN {print "COUNT\tTCP_PACKET_SIZE_BYTES"} {print $1 "\t" $2}'
</code></pre>

```shell
COUNT	TCP_PACKET_SIZE_BYTES
7	1
5	8
6	9
4	10
5	12
5	28
6	36
1	62
5	164
1	475
1	2261
2	2328
1	2357
1	2896
```

#### After the patch

The same Go script, capturing on the patched server with batching:

<pre><code type='click-ui' language='bash'>
tshark -i veth-host -f 'tcp port 9000 and greater 60 and tcp[tcpflags] & tcp-push != 0' -w patched-capture.pcap
</code></pre>

```shell
Capturing on 'veth-host'
25
```

You can clearly see the number of TCP packets transferred is half what it was before.

Looking at the captured packets clearly shows the `PSH` packets are much more "filled" compared to the many tiny packets before.

<pre><code type='click-ui' language='bash'>
tshark -r patched-capture.pcap -Y 'tcp.flags.push == 1 && tcp.len &gt; 0' -T fields -e tcp.len | sort -n | uniq -c | awk 'BEGIN {print "COUNT\tTCP_PACKET_SIZE_BYTES"} {print $1 "\t" $2}'
</code></pre>

```shell
COUNT	TCP_PACKET_SIZE_BYTES
3	1
1	36
1	62
5	164
2	2363
2	2417
1	2516
```

### Verify the tail latency disappears in the same customer setup

Running the same script with exactly the same setup as described in [reproducing the exact customer problem](#reproducing_the_exact_customer_problem) shows how the \~32 ms tail latency disappeared:

```shell
query  1: first_row=  34.53ms  eos=  35.65ms  tail=   1.12ms  (rows=1)
query  2: first_row=  34.79ms  eos=  35.58ms  tail=   0.79ms  (rows=1)
query  3: first_row=  35.23ms  eos=  36.12ms  tail=   0.90ms  (rows=1)
query  4: first_row=  34.72ms  eos=  35.95ms  tail=   1.23ms  (rows=1)
query  5: first_row=  34.98ms  eos=  36.26ms  tail=   1.27ms  (rows=1)
```

Note that no additional round trip is needed for the server to send `EndOfStream` (eos) to the client.

## Summary {#summary}

High tail latency isn't always caused by slow database engines or long-running queries; sometimes the culprit is hidden in the interaction between application-level flushes and kernel-level TCP behavior.

- **Idle TCP connections reset:** After an RTO idle period, the Linux TCP stack shrinks `cwnd` back to `initcwnd`, restricting how many unacknowledged packets can fit into a single round trip.
- **`TCP_NODELAY` has a trade-off:** Disabling Nagle's algorithm makes individual writes fast, but issuing multiple small `write()` calls can create an unexpected number of TCP segments that can quickly exhaust a small congestion window.
- **Batch at the application layer:** Grouping metadata packets (`ProfileEvents`, `Logs`, `Progress`) into a single buffer write before flushing drastically reduces the TCP segment count, keeping tail latency predictable even on idle, high-RTT connections.

---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-2580-get-started-today-sign-up&utm_blogctaid=2580)

---