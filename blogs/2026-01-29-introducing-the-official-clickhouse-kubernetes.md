---
title: "Introducing the Official ClickHouse Kubernetes Operator: Seamless Analytics at Scale"
date: "2026-01-29T08:11:33.495Z"
category: "Product"
excerpt: "Introducing the Official ClickHouse Kubernetes Operator, open source under Apache 2.0 and free. Deploy production ClickHouse clusters on Kubernetes with sharding, replication, and ClickHouse Keeper. Scale up or out, update configuration and versions safel"
---

# Introducing the Official ClickHouse Kubernetes Operator: Seamless Analytics at Scale

At ClickHouse, our mission has always been to make real-time analytics accessible and lightning-fast. As more of our community moves toward cloud-native architectures, the need for a robust, automated way to manage Open Source ClickHouse distribution on Kubernetes has become clear.

Today, we are thrilled to announce the release of the Official ClickHouse Kubernetes Operator - available now, open-source (under Apache-2.0 licence), and free for everyone.


## **Why a Kubernetes Operator?**

Running a stateful, high-performance database like ClickHouse on Kubernetes presents unique challenges: horizontal and vertical scaling, ensuring data persistence during pod restarts, and executing seamless upgrades.

The ClickHouse Operator simplifies these tasks by extending the Kubernetes API. It allows you to manage complex ClickHouse clusters using convenient Custom Resource Definitions (CRDs). Instead of manually configuring Pods and Services, you simply describe your desired state, and the Operator handles the rest.


## **Key Features**



* **Automated Cluster Provisioning:** Deploy a production-ready, multi-node cluster with sharding and replication in minutes.
* **ClickHouse Keeper Support:** Deploy and manage ClickHouse Keeper.
* **Vertical & Horizontal Scaling:** Easily adjust CPU / Memory resources or add new shards to your cluster with minimal downtime.
* **Configuration Management:** Safely update your configuration and ClickHouse version in a single manifest change. The Operator manages the sequence, ensuring that new configuration parameters are rolled out only to updated pods, eliminating the risk of service disruptions caused by version-config mismatches.
* **Seamless Upgrades:** Perform rolling updates to new ClickHouse versions without dropping queries.


## **Design choices**

When implementing the operator, we wanted to reuse the ClickHouse Cloud production experience and build on bulletproof, reliable features. That's why we: 



* We rely on ClickHouse Keeper for coordination — it’s built in, so you don’t need to run ZooKeeper separately, and there’s no “Keeper-less” mode to worry about. This [post](https://clickhouse.com/blog/clickhouse-keeper-a-zookeeper-alternative-written-in-cpp) covers the benefits. 
* Make the Replicated a default database engine. DatabaseReplicated has been powering ClickHouse Cloud since the beginning of our business and has proved its reliability and convenience. That’s why it was an obvious choice for us to use it in the Operator as well. It eliminates the need to write the ON CLUSTER clause in every DDL query you issue to the database.
* Have a StatefulSet per replica. This key decision allows us to implement different upgrade strategies and have fine-grained control over each replica (e.g., the version they run, their configuration, etc.).
* TLS/SSL encryption for ClickHouse &lt;-> Keeper and Client &lt;-> ClickHouse communication. 
* Configuration overrides for both ClickHouse and Keeper.

In general, our key principle is keeping things simple. If something can be implemented on the ClickHouse side in C++, it has to be there. That made the Operator a very thin layer on top of what ClickHouse already can do. 

 :::global-blog-cta::: 

## **Getting Started: Your First Cluster**

Getting up and running is as simple as applying a few YAML files.

**1. Install the cert-manager**

The operator uses defaulting and validating webhooks to ensure the validity of Custom Resource (CR) objects. It requires cert-manager to issue a certificate.

<pre><code type='click-ui' language='bash'>
# Using kubectl
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.19.2/cert-manager.yaml
</code></pre>


<pre><code type='click-ui' language='bash'>
# Or using helmchart
helm install cert-manager --create-namespace --namespace cert-manager oci://quay.io/jetstack/charts/cert-manager --set crds.enabled=true --version v1.19.2
</code></pre>

**2. Install the Operator**

<pre><code type='click-ui' language='bash'>
# Using kubectl
kubectl apply -f https://github.com/ClickHouse/clickhouse-operator/releases/download/latest/clickhouse-operator.yaml
</code></pre>


<pre><code type='click-ui' language='bash'>
# Or our helmchart
helm install clickhouse-operator --create-namespace -n clickhouse-operator-system oci://ghcr.io/clickhouse/clickhouse-operator-helm
</code></pre>     


**3. Deploy a Simple Cluster** Below is a basic example of a Custom Resource (CR) to deploy a two-node cluster:

YAML CR

<pre><code type='click-ui' language='yaml'>
apiVersion: clickhouse.com/v1alpha1
kind: KeeperCluster
metadata:
  name: sample
spec:
  replicas: 3
  dataVolumeClaimSpec:
    accessModes:
      - ReadWriteOnce
    resources:
      requests:
        storage: 10Gi
---
apiVersion: clickhouse.com/v1alpha1
kind: ClickHouseCluster
metadata:
  name: sample
spec:
  replicas: 2
  dataVolumeClaimSpec:
    accessModes:
      - ReadWriteOnce
    resources:
      requests:
        storage: 10Gi
  keeperClusterRef:
    name: sample
</code></pre>


## **Our Commitment to Open Source**

We believe that the tools used to manage ClickHouse should be as open as the database itself. This Operator is free to use. We invite the community to contribute, report bugs, and help us shape the roadmap for cloud-native ClickHouse.


## **Join the Conversation**

We’d love to hear your feedback!



* **Submit feature requests to GitHub issues:** [https://github.com/ClickHouse/clickhouse-operator/issues](https://github.com/ClickHouse/clickhouse-operator/issues)
* **Slack:** Join the operator slack channel [https://clickhousedb.slack.com/archives/C0ABN03GJA1](https://clickhousedb.slack.com/archives/C0ABN03GJA1)
* **Documentation:** [https://clickhouse.com/docs/clickhouse-operator/overview](https://clickhouse.com/docs/clickhouse-operator/overview)
* **Mailing list:** <span style="text-decoration:underline;">operator@clickhouse.com</span>

Happy scaling!
