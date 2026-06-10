# Big Data Storage Engineering: CSV vs. Parquet Benchmarking

## PFE-M 2026 Big Data — Sujet 1: L’Architecte du Stockage

[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Apache Spark](https://img.shields.io/badge/Apache_Spark-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white)](https://spark.apache.org/)
[![Apache Hadoop](https://img.shields.io/badge/Apache_Hadoop-EEEEEE?style=for-the-badge&logo=apachehadoop&logoColor=black)](https://hadoop.apache.org/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Jupyter](https://img.shields.io/badge/Jupyter-F37626?style=for-the-badge&logo=jupyter&logoColor=white)](https://jupyter.org/)

---

## 🌟 Executive Summary & Objective

This project explores the critical differences in storage architecture between **row-based text formats (CSV)** and **columnar binary formats (Apache Parquet)** within a distributed Big Data ecosystem. 

Selecting the right storage layout is a vital decision for enterprise and national data architectures (such as **SNIM** or **SOMELEC**). Using the NYC Yellow Taxi dataset (comprising over **1.36 million rows** and **18 columns**), this benchmark provides empirical proof of how Parquet optimizes:
* 📉 **Disk Storage Footprint** (via dictionary encoding and block compression)
* 🚀 **Query Performance** (via Column Pruning and Projection Pushdown)
* 🖥️ **Resource Utilization** (reducing Disk I/O, network bandwidth on HDFS, and CPU cycles)

---

## 🏗️ Cluster Architecture & Environment

The workspace deploys a fully-distributed containerized Hadoop & Spark cluster via `docker-compose.yml`.

### Cluster Services Topology
* **Storage Layer (HDFS):**
  * `namenode` (Master node managing filesystem namespace and metadata)
  * `datanode1` & `datanode2` (Slaves storing data blocks with standard replication)
* **Compute Layer (Spark):**
  * `spark-master` (Master scheduler and coordinator)
  * `spark-worker` (Executes compute tasks; configured with 2 Cores and 2GB RAM)
* **Interactive Layer:**
  * `jupyter` (Runs PySpark kernel, pre-configured to mount the project folder at `/work`)

---

## 🚀 Step-by-Step Execution Guide

Follow these exact commands to boot up the cluster, populate HDFS, run the benchmark, and analyze block storage.

### 1. Initialize the Cluster Infrastructure
Spin up the Docker services in the background:
```bash
docker compose up -d
```
*Wait approximately 1-2 minutes for the Hadoop NameNode and Resource Manager to complete health checks.*

### 2. Prepare and Upload the Dataset to HDFS
Since the NYC Taxi CSV file is large, place your `yellow_tripdata_2021-01.csv` inside the local `project/data/` directory.

To copy and upload the dataset into HDFS:
```bash
# Step A: Copy the local CSV into the namenode container's temporary storage
docker cp data/yellow_tripdata_2021-01.csv namenode:/tmp/

# Step B: Create a directory inside HDFS
docker exec -it namenode hdfs dfs -mkdir -p /taxi

# Step C: Put the CSV file from Namenode's local tmp folder to HDFS
docker exec -it namenode hdfs dfs -put /tmp/yellow_tripdata_2021-01.csv /taxi/

# Step D: List HDFS directory to verify successful upload
docker exec -it namenode hdfs dfs -ls /taxi
```

### 3. Run the Analytical Benchmark
You can run the benchmark interactively using Jupyter Notebook:
* Access the Jupyter interface at **`http://localhost:8888`**
* Open and run all cells in **`Sujet_1_Ingenierie_du_Stockage.ipynb`**

---

## 📊 Benchmark Results & Comparative Analysis

The following metrics were captured under identical resource constraints inside the cluster:

### 1. Storage Size & Footprint Reduction
*Original CSV Size on HDFS:* **456.1 MB**

| File Format | Storage Size on HDFS | Footprint Reduction | Effective Compression Ratio |
| :--- | :---: | :---: | :---: |
| **CSV** (Row-Based, Uncompressed) | **456.1 MB** | 0.0% (Baseline) | 1.00x |
| **Parquet** (Columnar, Uncompressed) | **56.0 MB** | 87.72% | **8.14x** |
| **Parquet** (Columnar, Snappy Compression) | **36.0 MB** | 92.11% | **12.67x** |
| **Parquet** (Columnar, Gzip Compression) | **26.0 MB** | **94.30%** | **17.54x** |

### 2. Write Performance Comparison
Times to write the entire DataFrame back to HDFS:

| Format / Compression | Write Time (Seconds) | Performance Rank | Primary Use-Case |
| :--- | :---: | :---: | :--- |
| **Parquet Snappy** | **11.23s** | 🥇 1st (Fastest) | Standard production analytics |
| **Parquet Gzip** | **13.94s** | 🥈 2nd | Cold storage / Archival data |
| **Parquet Uncompressed** | **17.97s** | 🥉 3rd | Benchmark baseline (No CPU overhead) |

> [!TIP]
> **Snappy** is the default Spark compression because it provides a well-balanced compression ratio with extremely low CPU overhead, yielding the fastest write speed. **Gzip** achieves maximum compression at the cost of higher CPU consumption.

### 3. Query Execution Speed
*Analytical Query Run:* `df.filter(df["VendorID"] == 1).select(avg("fare_amount")).collect()`

| Storage Format | Query Execution Time | Speedup Factor |
| :--- | :---: | :---: |
| **CSV** (Row-Based) | **5.23 seconds** | Baseline (1.00x) |
| **Parquet** (Columnar, Snappy) | **1.75 seconds** | 🚀 **2.99x Faster** |

---

## 🔍 Deep-Dive: Why is Parquet Faster?

### 1. Column Pruning Proof
In a row-based format like CSV, the query engine must load the entire row (all 18 columns) from disk into memory, parsing every line to filter and aggregate values. 
In Parquet, the engine selectively reads only the columns required. We verify this via Spark's physical plan using:
```python
parquet_df.select("fare_amount").explain(True)
```

**Physical Plan Output:**
```text
*(1) ColumnarToRow
+- FileScan parquet [fare_amount#366] Batched: true, DataFilters: [], Format: Parquet, Location: InMemoryFileIndex(1 paths)[hdfs://namenode:9000/output/parquet_snappy], PartitionFilters: [], PushedFilters: [], ReadSchema: struct<fare_amount:double>
```
* **ReadSchema Proof:** Notice that `ReadSchema` is explicitly restricted to `struct<fare_amount:double>`. No other columns were read from the storage layer, saving massive disk I/O and network transfer.

---

## ⚙️ HDFS Storage Analysis & Integrity Verification

### 1. Production Scaling (3.0 GB Dataset) Block Calculations
To validate system behavior at a production scale, we evaluate the cluster layout when scaling the raw dataset size to **3.0 GB**.

* **HDFS Block Size:** 128 MB (default).
* **Logical HDFS Block Count:**
  * **Binary Calculation (GiB):** $3 \text{ GiB} = 3 \times 1024 \text{ MiB} = 3072 \text{ MiB}$. Thus, $\frac{3072 \text{ MiB}}{128 \text{ MiB}} =$ **24 Blocks** (exactly).
  * **Decimal Calculation (GB):** $3 \text{ GB} = 3000 \text{ MB}$. Thus, $\frac{3000 \text{ MB}}{128 \text{ MB}} = 23.4375 \text{ Blocks}$, resulting in **23 full blocks of 128 MB** and **1 partial block of 56 MB** (totaling **24 Blocks** on disk).
* **Replication Footprint on a 2-Node Cluster (`datanode1` & `datanode2`):**
  * **HDFS Default Replication (Factor = 3):** Standard HDFS configuration attempts to replicate each block 3 times across unique nodes. For our 24 blocks, this equals **72 physical block replicas**. Since our cluster has only 2 physical DataNodes, HDFS cannot write the third copy to a unique host. The NameNode will dashboard all 24 blocks as **under-replicated**, although the dataset remains fully functional.
  * **Optimized Replication (Factor = 2):** Setting replication to 2 mirrors our physical architecture. Each block is stored on both nodes, giving exactly **48 physical blocks** (24 blocks per DataNode). This achieves maximum fault tolerance with zero under-replication warnings and optimized network/disk space.

### 2. Check Directory Sizes on HDFS
Ensure sizes match our benchmarks:
```bash
docker exec -it namenode hdfs dfs -du -h /taxi
docker exec -it namenode hdfs dfs -du -h /output/parquet_uncompressed
docker exec -it namenode hdfs dfs -du -h /output/parquet_snappy
docker exec -it namenode hdfs dfs -du -h /output/parquet_gzip
```

### HDFS Block Integrity & Skew Analysis
Verify if Parquet files are evenly distributed and that there is no data skew:
```bash
docker exec -it namenode hdfs fsck /output/parquet_snappy -files -blocks -locations
```
* **Balanced Distribution:** HDFS cuts data into blocks (default 128MB) and replicates them across `datanode1` and `datanode2`. This command checks for block distribution uniformity, ensuring parallel compute tasks complete evenly without stragglers.

---

## 💡 Strategic Value for Large Enterprises (e.g., SNIM, SOMELEC)

For national data infrastructure handling continuous measurements, metering, or mining metrics:
1. **Infrastructure Cost Reduction:** Moving from CSV to Parquet Snappy/Gzip saves **over 90% in disk capacity**, cutting storage hardware costs dramatically.
2. **Network Bandwidth Optimization:** Querying Parquet transfers less data across the network, avoiding network congestion bottlenecks.
3. **High-Performance Reporting:** Queries run up to **3x faster**, enabling real-time analytics and dashboards to load instantly.
