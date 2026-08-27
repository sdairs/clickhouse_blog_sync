---
title: "What's new in the ClickHouse .NET Driver: the road from 1.0 to 1.3"
date: "2026-08-27T13:26:14.734Z"
author: "Alex Soffronow Pagonidis"
category: "Engineering"
excerpt: "Discover how ClickHouse .NET Driver 1.1–1.3 adds type-safe POCO workflows, extensible serialization, broader type support, performance improvements, and official ecosystem integrations."
---

# What's new in the ClickHouse .NET Driver: the road from 1.0 to 1.3

Back in February this year, we [released the first stable version of our .NET driver](https://clickhouse.com/blog/clickhouse-driver-1_0_0-official-dotnet-client). That release focused on broadening type support, packaging, configuration, observability, and it introduced a brand new primary API separate from the legacy ADO.NET API.

Since then, we’ve been steadily releasing improvements across three new minor versions, improving the user experience, making the client more extensible and configurable, and expanding type coverage. We have also been building a number of integrations in the .NET ecosystem. And we couldn’t have done it without the contributions from the community. We’d like to thank everyone who filed an issue, reproduced a bug or sent a pull request this cycle, including Daniel Bunting, Vyacheslav Brevnov, Minh Vu, Ozan Hanedan, and Musa Musaev.

If you last looked at this driver at 1.0, the insert path, the read path and the parameter path have all changed. Here's what happened.

## Type-safe workflows with POCOs {#type_safe_workflows_with_pocos}

The single biggest ergonomic change. In 1.0 the standard path was `object[]`. Now it's your own classes, in both directions:

### Before (1.0): hand-marshalled `object[]`

```c#
using var client = new ClickHouseClient("Host=localhost");

// You own the column list, the ordering, and the boxing.
await client.InsertBinaryAsync(
    "sensors",
    new[] { "Id", "SensorName", "Value", "RecordedAt" },
    readings.Select(r => new object[] { r.Id, r.SensorName, r.Value, r.RecordedAt }));
```

Every insert restates the schema. Reorder two columns in the `string[]` and you end up with a runtime serialization error, or even silently transposed data.

### After (1.3): register once, insert and read your type

```c#
public class SensorReading
{
    public ulong Id { get; set; }
    public string SensorName { get; set; }
    public double Value { get; set; }
    public DateTime RecordedAt { get; set; }
}

using var client = new ClickHouseClient("Host=localhost");
client.RegisterPocoType<SensorReading>();   // sets up insert + read, validates both up front

// Write
long rows = await client.InsertBinaryAsync("sensors", readings);   // IEnumerable<SensorReading>

// Read
await foreach (var r in client.QueryAsync<SensorReading>(
                   "SELECT * FROM sensors WHERE Value > 20;"))
{
    Console.WriteLine($"{r.SensorName}: {r.Value:F2}");
}
```

Registration happens up front: it validates the class and surfaces any mapping issues eagerly. Getters and setters are pre-compiled, so there's no extra cost at query time. `QueryAsync<T>` returns `IAsyncEnumerable<T>`, and rows are materialized lazily. The reader is disposed when enumeration completes, faults, or you `break` early.
A few matching rules worth knowing about:
- Column matching is case-sensitive (`StringComparer.Ordinal`).
- Result columns with no matching property are ignored.
- Properties with no matching result column are left at their default value.
- Types need a public parameterless constructor and at least one public property with a public non-`init` setter. `required` properties are supported.

**Mapping properties**

You can also control the column and type mapping of each property using attributes:

```c#
public class AuditEvent
{
    [ClickHouseColumn(Name = "event_id")]
    public ulong Id { get; set; }

    [ClickHouseColumn(Name = "event_type", Type = "LowCardinality(String)")]
    public required string Type { get; set; }

    [ClickHouseNotMapped]
    public string InternalCorrelationTag { get; set; }
}
```

The driver does not do any silent conversions. When there is a mismatch, you get an `InvalidOperationException` naming the POCO type, the property, the column, and the CLR type actually returned, so fixing issues is easy.
To help with debugging, the mapper also emits detailed logs. With a `LoggerFactory` configured, registration emits a `Debug`-level log (category `ClickHouse.Driver.Client`) listing which properties mapped to which columns, and which were skipped and why. That log answers most mapping questions faster than reading the rules above.

### POCOs into JSON columns

The same idea extends to ClickHouse's `JSON` type. You can write POCOs with full type fidelity directly into JSON columns with `RegisterJsonSerializationType<T>()` plus `[ClickHouseJsonPath("...")]` / `[ClickHouseJsonIgnore]` (note that JsonWriteMode must be set to Binary):

```c#
public class SensorAttributes
{
    [ClickHouseJsonPath("device.id")]
    public required string DeviceId { get; set; }

    public decimal Temperature { get; set; }

    [ClickHouseJsonIgnore]
    public string LocalDebugTag { get; set; }
}

using var client = new ClickHouseClient("Host=localhost;JsonWriteMode=Binary");
client.RegisterJsonSerializationType<SensorAttributes>();

// attributes JSON(`device.id` String, Temperature Decimal64(4))
await client.InsertBinaryAsync("readings", ["id", "attributes"],
    [[1UL, new SensorAttributes { DeviceId = "sensor-7", Temperature = 21.4375m }]]);
```

That row lands as `{"Temperature":"21.4375","device":{"id":"sensor-7"}}`.

## Customize the pipeline end-to-end {#customize_the_pipeline_end_to_end}

The second theme is control. A driver has to pick sensible defaults, but one size doesn’t fit every use case. In order to give users more control over how the client behaves, we have added three extension points covering type resolution, parameter serialization, and value conversion for reads. These are optional and there is zero overhead when they are not used.

| Interface | Stage | Since |
| --- | --- | --- |
| `IParameterTypeResolver` | CLR type → ClickHouse type | 1.2 |
| `IParameterFormatter` | value → wire representation | 1.3 |
| `IReadValueConverter` | wire value → CLR value on the way back | 1.3 |

All three are settable on `ClickHouseClientSettings` (client-wide) or `QueryOptions` (per-query).

### 1. `IParameterTypeResolver`: control type inference

ClickHouse expects server-bound parameters in the form `{name:Type}`, for example `SELECT count() FROM sensor_readings WHERE id = {id:Int64};`. However, the driver also accepts untyped ADO.NET-style parameters (`WHERE id = @id`), which is what ORMs like Dapper emit. In that case the ClickHouse type has to be inferred from the CLR value.
The built-in inference is deliberately conservative: `decimal` becomes `Decimal128(scale)` and `DateTime` becomes `DateTime('UTC')`, because those lose the least information. But if your schema is `Decimal64(4)` and `DateTime64(3)` throughout, conservative means wrong, and you'd be annotating every `@`-style parameter in your codebase to say so.
`IParameterTypeResolver` lets you state the convention once. For the common case there's a built-in dictionary implementation:

```c#
var settings = new ClickHouseClientSettings("Host=localhost")
{
    ParameterTypeResolver = new DictionaryParameterTypeResolver(new Dictionary<Type, string>
    {
        [typeof(decimal)]  = "Decimal64(4)",
        [typeof(DateTime)] = "DateTime64(3)",
    }),
};
```

For value-aware or name-aware logic, implement the interface directly. This example picks the narrowest decimal that fits, per value:

```c#
private class SmartDecimalResolver : IParameterTypeResolver
{
    public string ResolveType(Type clrType, object value, string parameterName)
    {
        if (clrType != typeof(decimal))
            return null; // let everything else use default inference

        var scale = (decimal.GetBits((decimal)value)[3] >> 16) & 0x7F;
        return scale <= 4 ? $"Decimal64({scale})" : $"Decimal128({scale})";
    }
}
```

Returning `null` falls through to the default inference, so a resolver only has to handle the cases it cares about.

### 2. `IParameterFormatter`: control the wire representation

Resolving the *type* isn't always enough, sometimes the type is right but the *rendering* is wrong. HTTP parameters go to the server as text, and the driver has to decide how to write each value out. That's usually uncontroversial, but not always: a column declared `DateTime` will happily accept a value with sub-second precision and throw the remainder away, and you may prefer to make that truncation explicit and local rather than a server-side surprise.

```c#
var settings = new ClickHouseClientSettings("Host=localhost")
{
    ParameterFormatter = new DictionaryParameterFormatter(new Dictionary<Type, Func<object, string>>
    {
        // e.g. clamp to whole seconds regardless of the column's declared precision
        [typeof(DateTime)] = v => ((DateTime)v).ToString("yyyy-MM-dd HH:mm:ss",
                                                          CultureInfo.InvariantCulture),
    }),
};
```

Two points worth highlighting:
- The formatter is invoked for the top-level value and for every element inside composite values (`Array`, `Tuple`, `Map`, `Nested`).
- Transparent wrappers (`Nullable`, `LowCardinality`, `Variant`) are unwrapped first, so your formatter sees the underlying concrete type exactly once and doesn't need to know about them. And it is never consulted for `null`/`DBNull`, those always serialize as the ClickHouse null sentinel.

### 3. `IReadValueConverter`: normalize on the way out

The third one covers the return trip. Suppose you have ClickHouse `DateTime` columns without an explicit time zone. Those come back as `Kind = Unspecified`. If your application invariant is "all timestamps are UTC," you can convert them before they leave the client so you can stop sprinkling `DateTime.SpecifyKind` across your codebase:

```c#
var settings = new ClickHouseClientSettings("Host=localhost")
{
    ReadValueConverter = new DictionaryReadValueConverter()
        .For<DateTime>(dt => DateTime.SpecifyKind(dt, DateTimeKind.Utc))
        .For<string>(s => s.Trim()),
};
```

The converter intercepts `GetValue()` and `GetFieldValue<T>()`, and is applied during POCO materialization, so `QueryAsync<T>()` sees converted values too.
One caveat: `DictionaryReadValueConverter` dispatches on the **CLR** type only, and both `DateTime` and `DateTime('UTC')` columns surface as `System.DateTime`, so the snippet above also stamps `Kind = Utc` onto columns that already carried a zone. When the distinction matters, implement the interface directly and switch on the ClickHouse type name (or the value), which arrives exactly as the server reported it:

```c#
private class UtcOnlyForNoTzDateTimeConverter : IReadValueConverter
{
    public object ConvertValue(object value, string columnName, string clickHouseType)
        => value is DateTime dt && clickHouseType == "DateTime"
            ? DateTime.SpecifyKind(dt, DateTimeKind.Utc)
            : value;

    public T ConvertValue<T>(T value, string columnName, string clickHouseType)
        => typeof(T) == typeof(DateTime) && value is DateTime dt && clickHouseType == "DateTime"
            ? (T)(object)DateTime.SpecifyKind(dt, DateTimeKind.Utc)
            : value;
}
```

There are two constraints to this interface:
- **It must not change the runtime type of a value.** Column metadata (`GetFieldType`, `GetSchemaTable`) is not re-derived from the converter's output. This is not a mapping layer.
- **It does not recurse into composites.** It's invoked once per column per row with the whole deserialized cell: for an `Array(Int32)` column you get the `int[]`, not each `int`.
The generic overload exists so hot paths can stay allocation-free: `typeof(T)` checks plus `Unsafe.As` let you transform value types without boxing.

### Finer-grained knobs

A few smaller additions in the same spirit:
- **Per-query `Accept-Encoding`:** `QueryOptions.AcceptEncoding` (mirrored on `ClickHouseCommand.AcceptEncoding`) replaces the default `gzip, deflate` for a single request. Forces `enable_http_compression=1` so the server honours it.
	- Note that for codecs the BCL can't decode (zstd, lz4) you must configure the `HttpClient` with `AutomaticDecompression = None` and consume the body via `ExecuteRawResultAsync`. `ClickHouseRawResult.ContentEncoding` tells you what you got.
- **`GetFieldValue<T>(string name)`**: column-by-name overload, complementing the ordinal one.
- **`ApplicationInfo`**: a free-form `IReadOnlyDictionary<string, string>` of tags on `ClickHouseClientSettings` (`app`, `ver`, `env`, whatever you like), appended to the HTTP `User-Agent` as a comment token: `(app:MyApp; ver:2.3.1; env:prod)`. This can come in handy if you need to trace where a query came from in the database query log. 

## Richer type support {#richer_type_support}

We have also been improving type support on both the CLR and ClickHouse sides, adding support for multidimensional arrays, ValueTuples, and Identifier parameters.

### Nested & multidimensional arrays

Thanks to [@DanielBunting](https://github.com/DanielBunting), `Array(Array(T))` (and deeper nestings) can now be read or written as a multidimensional array. 
C# has two types of N-dimensional arrays: jagged (`int[][]`, an array of arrays, rows can differ in length) and rectangular (`int[,]`, a single block, all rows equal). ClickHouse's `Array(Array(T))` is structurally jagged, but sometimes you’re handling data that is naturally rectangular, and forcing it through a jagged intermediate means allocating a row array per row.
Both jagged (`T[][]`, `List<List<T>>`) and rectangular (`T[,]`, `T[,,]`, …) CLR shapes are accepted on write now. Reads still default to jagged, but `GetFieldValue<T[,]>` materializes rectangular directly and validates the shape.

```c#
// Write: jagged or rectangular, your choice
int[][] jagged      = [[1, 2], [3], [4, 5, 6]];
int[,]  rectangular = new int[2, 3] { { 1, 2, 3 }, { 4, 5, 6 } };

await client.InsertBinaryAsync("matrices", ["id", "data"],
    [[1UL, jagged], [2UL, rectangular]]);

// Read: GetValue gives you jagged...
var asJagged = (int[][])reader.GetValue(1);

// ...but if you know it's rectangular, ask for that shape directly
var asRect = reader.GetFieldValue<int[,]>(1);   // throws on ragged data
```

### `ValueTuple` on the write path

C# tuple literals just work, in binary inserts, HTTP parameters, and type inference:

```c#
await client.InsertBinaryAsync("t", ["id", "pair"],
    [[1UL, (42, "hello")]]);   // -> Tuple(Int32, String)
```

Tuples with more than 7 elements are correctly flattened out of the compiler-generated `TRest` nesting.

### Server-side `Identifier` parameters

You can now bind a database, table or column name as a parameter instead of concatenating it into SQL:

```c#
var p = new ClickHouseParameterCollection();
p.AddParameter("tbl", "my-table`with`backticks");
await client.ExecuteReaderAsync("SELECT * FROM {tbl:Identifier};", p);
```

The value is now sent verbatim and the server performs the identifier quoting and escaping, so names containing special characters (backticks included) round-trip with no client-side escaping logic at all. Previously this threw `ArgumentException: Unknown type: Identifier`. 

## Correctness {#correctness}

We have also spent a chunk of this cycle working on correctness and fixing bugs in the client.

### Breaking change: DateTime time zone handling

The most important breaking change you need to know about concerns DateTime handling:

```c#
var p = new ClickHouseParameterCollection();
p.AddParameter("ts", DateTime.UtcNow);
await client.ExecuteNonQueryAsync("INSERT INTO events VALUES (@ts);", p);
```

- **Before:** the driver emitted a bare `{ts:DateTime}` hint. The server parsed the wire wall-clock in `session_timezone`, shifting the value by the server's offset. On a UTC server you'd never notice; on `Europe/Amsterdam` you'd be two hours off in summer.
- **After:** inferred types for `DateTime { Kind: Utc or Local }` and `DateTimeOffset` are sent as `DateTime('UTC')`. The instant survives any server time zone.
- Explicit hints are untouched, if the parameter type is `{ts:DateTime}`, you still own the time zone semantics.

There are many smaller correctness improvements throughout the client. Some highlights:

- **`Fixed/UTC±HH:MM:SS` time zones:** ClickHouse's synthetic zone names aren't in the IANA TZDB, so the driver treated them as UTC and returned values shifted by the column's own offset. Now parsed into a proper fixed-offset zone.
- **Composite-type serialization:** `Date`/`DateTime`/`DateTime64` inside `Array`, `Tuple`, `Map`, `Variant` are now quoted correctly over HTTP.
- **Variant NULLs:** reading a NULL from a `Variant` threw `IndexOutOfRangeException` (the `None` discriminator wasn't handled); writing one didn't emit `0xFF` at all. Both fixed.
- **Enum labels with escaped quotes, parentheses, or `=`** now parse correctly.
And plenty more in the [changelog](https://github.com/ClickHouse/clickhouse-cs/blob/main/CHANGELOG.md).

## Fewer round-trips, less GC pressure {#fewer_round_trips_less_gc_pressure}

Two changes in this cycle were about performance rather than capability.

### Insert ergonomics: skip the schema probe

By default every `InsertBinaryAsync` call probes the table schema with a `SELECT ... WHERE 1=0` round-trip. This represents an overhead cost on every insert. There are now two ways to avoid it:

```c#
// Know the schema at compile time? Declare it and skip the probe entirely.
var options = new InsertOptions
{
    ColumnTypes = new Dictionary<string, string>
    {
        ["Id"]         = "UInt64",
        ["SensorName"] = "LowCardinality(String)",
        ["Value"]      = "Float64",
    },
};

// Or probe once and reuse it for the lifetime of the client.
var cached = new InsertOptions { UseSchemaCache = true };
```

`ColumnTypes` takes priority over `UseSchemaCache` and requires an explicit column list. `UseSchemaCache` caches per (database, table) for the lifetime of the client, so it requires care when it comes to any `ALTER TABLE` statements that would break the query.
And if you use a POCO where *all* mapped properties carry `[ClickHouseColumn(Type = ...)]`, the probe is skipped automatically.

### `ReadBufferSize` default lowered 512 KiB → 8 KiB

The response read buffer was fixed at 512 KiB. That's above the 85,000-byte large object heap threshold, which means every single query response allocated on the LOH (a heap that isn't compacted by default, causing memory fragmentation). The allocations also created significant garbage collection pressure. In a benchmark with 1000 small SELECTs, we saw per-query allocation drop by over 80%, gen 2 collections eliminated, and total GC pause time drop by over 90%.
1.3 makes the size configurable via `ClickHouseClientSettings.ReadBufferSize` or the `ReadBufferSize` connection-string key, and lowers the default to 8 KiB. If you stream large responses and would rather have fewer buffer refills, raise it.

## Entity Framework Core {#entity_framework_core}

The most-requested integration in .NET, and now an official one: [`ClickHouse.EntityFrameworkCore`](https://github.com/ClickHouse/ClickHouse.EntityFrameworkCore) supports queries, inserts, table-engine configuration and migrations, with `GROUP BY` aggregates, string methods, math functions and JSON columns all translated to ClickHouse SQL.

**DDL**

Configuration looks like any other EF Core provider:

```c#
public class AnalyticsContext : DbContext
{
    public DbSet<PageView> PageViews { get; set; }

    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
        => optionsBuilder.UseClickHouse("Host=localhost;Port=8123;Database=analytics");
}
```

```c#
modelBuilder.Entity<SensorReading>(b =>
{
    b.HasKey(e => e.Id);
    b.Property(e => e.Temperature).HasCodec("Delta, ZSTD");
    b.Property(e => e.Location).HasColumnComment("Installation site");
    b.HasIndex(e => e.Timestamp)
        .HasSkippingIndexType("minmax")
        .HasGranularity(4);
    b.ToTable("sensor_readings", t => t
        .HasReplacingMergeTreeEngine("Version")
        .WithOrderBy("Id", "Timestamp")
        .WithPartitionBy("toYYYYMM(Timestamp)")
        .WithPrimaryKey("Id")
        .WithTtl("Timestamp + INTERVAL 1 YEAR")
        .WithSetting("index_granularity", "4096"));
});
```

**Query Building**

You can then use LINQ and have everything translated to ClickHouse syntax as you’d expect:

```c#
var topPages = await ctx.PageViews
    .Where(v => v.Date >= new DateOnly(2024, 1, 1))
    .GroupBy(v => v.Path)
    .Select(g => new { Path = g.Key, Views = g.Count() })
    .OrderByDescending(x => x.Views)
    .Take(10)
    .ToListAsync();
```

**Bulk Insert**

And you don’t have to abandon Entity Framework to insert efficiently, as the integration provides a performant `.BulkInsertAsync()` path:

```c#
long rowsInserted = await ctx.BulkInsertAsync(events);

// tune the batch size at configuration time
optionsBuilder.UseClickHouse("Host=localhost", o => o.MaxBatchSize(5000));
```

The integration also offers a table-engine fluent API, with support for a wide variety of table engines, indices, and column-level DDL.

## Growing ecosystem {#growing_ecosystem}

Beyond EF Core, we support three more official integrations:
- [**Serilog:**](https://github.com/ClickHouse/Serilog.Sinks.ClickHouse) `WriteTo.ClickHouse()` with fluent column and cluster configuration. One line for existing Serilog users. Check out our earlier post on [Structured Logging in .NET with Serilog and ClickHouse](https://clickhouse.com/blog/serilog).
- [**Aspire:**](https://github.com/ClickHouse/ClickHouse.Aspire/) `Aspire.Hosting.ClickHouse` adds a ClickHouse container resource to the app model; `Aspire.ClickHouse.Driver` registers `ClickHouseDataSource` in DI with health checks, OpenTelemetry tracing, and configuration binding. We also have a blog post on [Building a .NET API Gateway with ClickHouse and Aspire](https://clickhouse.com/blog/dotnet-api-gateway-aspire).
- [**Semantic Kernel:**](https://github.com/ClickHouse/ClickHouse.SemanticKernel) vector store connector for `Microsoft.Extensions.VectorData`. CRUD, filtered queries, vector similarity, all using ClickHouse as the vector DB behind the standard SK interface. The repo includes a demo project showcasing semantic search over the IMDb dataset.

## Looking ahead {#looking_ahead}

### 1.4: Go Fast

Our next release, version 1.4, is focused on performance improvements, cutting memory allocations and speeding things up. Here’s a small preview of what’s to come:
- **Broad allocation cuts:** eliminating buffers and pooling others for big allocation savings.
- **Pluggable compression:** `IClickHouseCompressor`, with GZip, Brotli, LZ4, and Zstd built in (for both reads and writes).
- **Box-free POCO reads and writes:** the driver will directly read and write using generic interfaces, skipping the intermediate `object` cast and saving a large amount of allocations.
- …and much more!

### 1.5: Native/TCP Client

We are currently working hard on a new client implementing the TCP protocol and Native (columnar) data format, which will unlock even greater performance gains.
Some of the benefits to expect from TCP: 

**Columns stay columns.** Data is transmitted in *blocks*, which use the columnar format the data is stored in inside the database. One benefit is that you will stop paying the RowBinary serialization cost on the server side. Reading a million `Int64`s stops being a million independent decode steps, and becomes a single copy operation.

**The server tells you what it is doing.**  Native interleaves progress updates, profile events and server-side log lines into the response *while the query is still running:* rows read, bytes read, and the server's own running estimate of the total.

**Connections** are also long-lived and stateful, so sessions, temporary tables and per-connection settings stop being something the driver has to emulate via the session id parameter.

## Links {#links}

- Install: `dotnet add package ClickHouse.Driver`
- Docs: [https://clickhouse.com/docs/integrations/csharp](https://clickhouse.com/docs/integrations/csharp)
- Examples: [https://github.com/ClickHouse/clickhouse-cs/tree/main/examples](https://github.com/ClickHouse/clickhouse-cs/tree/main/examples)
- If you have any feedback, please reach out on [GitHub](https://github.com/ClickHouse/clickhouse-cs) or find us in the [community Slack](https://clickhouse.com/slack).


---

## Get started today

Interested in seeing how ClickHouse works on your data? Get started with ClickHouse Cloud in minutes and receive $300 in free credits.

[Sign up](https://console.clickhouse.cloud/signUp?loc=blog-cta-1655-get-started-today-sign-up&utm_blogctaid=1655)

---