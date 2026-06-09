# Big Data Storage Architecture: CSV vs Parquet

## PFE-M 2026 Big Data — Sujet 1: L’Architecte du Stockage

### Objective
This project demonstrates the differences in storage engineering between row-based formats (CSV) and columnar formats (Apache Parquet). It proves that choosing a storage format is a strategic decision for national data infrastructure, impacting disk I/O, network bandwidth on HDFS, and query execution times. 

It uses **Apache Spark** to ingest the NYC Yellow Taxi dataset and compares:
- CSV
- Parquet (Snappy Compression)
- Parquet (Gzip Compression)
- Parquet (Uncompressed)

### Requirements
- Docker and Docker Compose
- Python 3.9+
- Bash/WSL (if running on Windows)

### How to use

1. **Install Python dependencies locally (optional, for charts/report generation)**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start the Cluster**
   ```bash
   chmod +x scripts/*.sh
   ./scripts/00_start_cluster.sh
   ```
   This starts the Hadoop HDFS cluster and Spark Master/Worker nodes via Docker. Wait a few minutes for NameNode and ResourceManager to be healthy.

3. **Provide Dataset**
   Place the NYC Taxi dataset CSV file(s) into `data/`. See `data/README_DATASET.md` for instructions.

4. **Upload Dataset to HDFS**
   ```bash
   hdfs dfs -put yellow_tripdata_2021-01.csv /taxi/
   ```

5. **Run the Benchmark**
   ```bash
   spark-submit --master yarn scripts/02_run_storage_benchmark.py
   ```
   This executes the Spark PySpark job inside the spark-master container, performing transformations, saving to HDFS, querying, and extracting physical execution plans.

6. **Run HDFS Skew Analysis**
   ```bash
   spark-submit --master yarn scripts/03_hdfs_skew_analysis.py
   ```

7. **Collect Results and Generate Report**
   ```bash
   ./scripts/04_collect_results.sh
   ```
   This generates the Markdown report in `outputs/final_report.md` along with PNG charts in `outputs/charts/`.

8. **Stop the Cluster**
   ```bash
   ./scripts/05_stop_cluster.sh
   ```
   *(Note: Add `-v` manually to your docker-compose down if you want to wipe HDFS data completely).*

### Expected Outputs
- `outputs/metrics/*.csv` files containing execution times and HDFS sizes.
- `outputs/explain_plans/*.txt` physical plans proving Parquet column pruning.
- `outputs/charts/*.png` visualizations.
- `outputs/final_report.md` a comprehensive academic report analyzing the benchmarks.
