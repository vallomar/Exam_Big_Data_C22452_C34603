import json

notebook = {
  "cells": [
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "# BIG DATA PROJECT - SUJET 1 : L'ARCHITECTE DU STOCKAGE\n",
        "\n",
        "## SECTION 1 : PROJECT INTRODUCTION\n",
        "\n",
        "**Objective of the project:**\n",
        "This project explores the fundamental differences between row-based (CSV) and columnar (Parquet) storage formats in a Big Data ecosystem. The objective is to understand how storage choices impact data processing speeds, storage costs, and overall system efficiency using Apache Spark.\n",
        "\n",
        "**Difference between CSV and Parquet:**\n",
        "* **CSV (Comma-Separated Values):** A row-based, human-readable text format. It is easy to use but lacks structure, schema enforcement, and compression efficiency. When querying, the engine must read the entire row even if only one column is needed.\n",
        "* **Parquet:** A columnar, binary storage format designed for Hadoop ecosystems. It stores data column by column, enabling highly efficient data compression and query optimization.\n",
        "\n",
        "**Why columnar storage is important in Big Data:**\n",
        "In Big Data analytics, queries often involve scanning specific columns (e.g., aggregations like average or sum) across massive datasets rather than fetching entire records. Columnar storage allows the query engine to read only the necessary columns, significantly reducing the amount of data processed.\n",
        "\n",
        "**Expected benefits:**\n",
        "* **Reduced storage size:** Columnar data allows for better compression algorithms since all data in a column is of the same type.\n",
        "* **Faster analytics:** Reading only required columns speeds up analytical queries.\n",
        "* **Reduced disk I/O:** Less data read from disk means fewer I/O bottlenecks.\n",
        "* **Better bandwidth usage:** Smaller file sizes and selective reading reduce network traffic when transferring data across a cluster."
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## SECTION 2 : START SPARK SESSION"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": {},
      "outputs": [],
      "source": [
        "from pyspark.sql import SparkSession\n",
        "\n",
        "spark = SparkSession.builder \\\n",
        "    .appName(\"NYC Taxi Storage Optimization\") \\\n",
        "    .master(\"local[*]\") \\\n",
        "    .config(\"spark.hadoop.fs.defaultFS\", \"hdfs://127.0.0.1:9000\") \\\n",
        "    .config(\"spark.hadoop.dfs.client.use.datanode.hostname\", \"true\") \\\n",
        "    .getOrCreate()\n",
        "\n",
        "print(\"Spark version:\", spark.version)\n",
        "print(\"Spark master:\", spark.sparkContext.master)\n",
        "print(\"HDFS defaultFS:\", spark._jsc.hadoopConfiguration().get(\"fs.defaultFS\"))"
      ]
    }
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## SECTION 3 : LOAD DATASET FROM HDFS"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": {},
      "outputs": [],
      "source": [
        "hdfs_csv_path = \"hdfs://127.0.0.1:9000/data/nyc_taxi.csv\"\n",
        "\n",
        "df_csv = spark.read.csv(\n",
        "    hdfs_csv_path,\n",
        "    header=True,\n",
        "    inferSchema=True\n",
        ")\n",
        "\n",
        "df_csv.printSchema()\n",
        "\n",
        "print(f\"Number of rows: {df_csv.count()}\")\n",
        "\n",
        "df_csv.show(5)"
      ]
    }
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## SECTION 4 : BASIC DATA EXPLORATION"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": {},
      "outputs": [],
      "source": [
        "print(f\"Number of columns: {len(df_csv.columns)}\")\n",
        "print(f\"Number of rows: {df_csv.count()}\")\n",
        "\n",
        "df_csv.select(\"VendorID\", \"fare_amount\", \"trip_distance\").show(5)"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## SECTION 5 : SAVE AS PARQUET (UNCOMPRESSED)"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": {},
      "outputs": [],
      "source": [
        "import time\n",
        "\n",
        "start_time = time.time()\n",
        "\n",
        "df_csv.write.mode(\"overwrite\") \\\n",
        "    .option(\"compression\", \"uncompressed\") \\\n",
        "    .parquet(\"hdfs://127.0.0.1:9000/output/parquet_uncompressed\")\n",
        "\n",
        "end_time = time.time()\n",
        "time_uncompressed = end_time - start_time\n",
        "print(f\"Write time for uncompressed Parquet: {time_uncompressed} seconds\")"
      ]
    }
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## SECTION 6 : SAVE AS PARQUET (SNAPPY)"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": {},
      "outputs": [],
      "source": [
        "start_time = time.time()\n",
        "\n",
        "df_csv.write.mode(\"overwrite\") \\\n",
        "    .option(\"compression\", \"snappy\") \\\n",
        "    .parquet(\"hdfs://127.0.0.1:9000/output/parquet_snappy\")\n",
        "\n",
        "end_time = time.time()\n",
        "time_snappy = end_time - start_time\n",
        "print(f\"Write time for Snappy Parquet: {time_snappy} seconds\")"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## SECTION 7 : SAVE AS PARQUET (GZIP)"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": {},
      "outputs": [],
      "source": [
        "start_time = time.time()\n",
        "\n",
        "df_csv.write.mode(\"overwrite\") \\\n",
        "    .option(\"compression\", \"gzip\") \\\n",
        "    .parquet(\"hdfs://127.0.0.1:9000/output/parquet_gzip\")\n",
        "\n",
        "end_time = time.time()\n",
        "time_gzip = end_time - start_time\n",
        "print(f\"Write time for Gzip Parquet: {time_gzip} seconds\")"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## SECTION 8 : SIZE COMPARISON\n",
        "\n",
        "The following commands must be executed manually in the terminal to check the sizes on HDFS:\n",
        "\n",
        "```bash\n",
        "hdfs dfs -du -h /data\n",
        "hdfs dfs -du -h /output/parquet_uncompressed\n",
        "hdfs dfs -du -h /output/parquet_snappy\n",
        "hdfs dfs -du -h /output/parquet_gzip\n",
        "```\n",
        "\n",
        "| Format | Size | Compression Ratio |\n",
        "|---|---|---|\n",
        "| CSV | | |\n",
        "| Parquet Uncompressed | | |\n",
        "| Parquet Snappy | | |\n",
        "| Parquet Gzip | | |"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## SECTION 9 : BENCHMARK QUERY ON CSV"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": {},
      "outputs": [],
      "source": [
        "from pyspark.sql.functions import avg\n",
        "\n",
        "start_time = time.time()\n",
        "\n",
        "csv_result = df_csv.filter(df_csv[\"VendorID\"] == 1).select(avg(\"fare_amount\")).collect()\n",
        "\n",
        "end_time = time.time()\n",
        "csv_query_time = end_time - start_time\n",
        "\n",
        "print(f\"Result: {csv_result[0][0]}\")\n",
        "print(f\"Query time on CSV: {csv_query_time} seconds\")"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## SECTION 10 : BENCHMARK QUERY ON PARQUET\n",
        "\n",
        "| Format | Execution Time |\n",
        "|---|---|\n",
        "| CSV | |\n",
        "| Parquet (Snappy) | |"
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": {},
      "outputs": [],
      "source": [
        "df_parquet = spark.read.parquet(\"hdfs://127.0.0.1:9000/output/parquet_snappy\")\n",
        "\n",
        "start_time = time.time()\n",
        "\n",
        "parquet_result = df_parquet.filter(df_parquet[\"VendorID\"] == 1).select(avg(\"fare_amount\")).collect()\n",
        "\n",
        "end_time = time.time()\n",
        "parquet_query_time = end_time - start_time\n",
        "\n",
        "print(f\"Result: {parquet_result[0][0]}\")\n",
        "print(f\"Query time on Parquet: {parquet_query_time} seconds\")"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## SECTION 11 : COLUMN PRUNING ANALYSIS\n",
        "\n",
        "**Column Pruning:**\n",
        "* Spark reads only the required column from the Parquet file.\n",
        "* Unnecessary columns are skipped during the read operation.\n",
        "* This significantly reduces I/O operations and memory usage."
      ]
    },
    {
      "cell_type": "code",
      "execution_count": None,
      "metadata": {},
      "outputs": [],
      "source": [
        "parquet_df = spark.read.parquet(\"hdfs://127.0.0.1:9000/output/parquet_snappy\")\n",
        "parquet_df.select(\"fare_amount\").explain(True)"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## SECTION 12 : DATA SKEW ANALYSIS\n",
        "\n",
        "**Data Skew:** Data skew happens when data is unevenly distributed across partitions. Some nodes process huge amounts of data while others are idle.\n",
        "\n",
        "You can check the distribution manually using this command in your terminal:\n",
        "```bash\n",
        "hdfs fsck /output/parquet_snappy -files -blocks -locations\n",
        "```\n",
        "\n",
        "* **Balanced distribution:** Blocks are roughly the same size and evenly spread across nodes, leading to optimal parallel processing.\n",
        "* **Unbalanced distribution:** Some blocks are disproportionately large, causing straggler tasks that delay the entire job.\n",
        "* **Possible bottlenecks:** High memory and CPU usage on overloaded nodes, causing network congestion and disk I/O wait times."
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## SECTION 13 : RESULTS SUMMARY\n",
        "\n",
        "### Storage Comparison\n",
        "| Format | Storage Size |\n",
        "|---|---|\n",
        "| CSV | |\n",
        "| Parquet Uncompressed | |\n",
        "| Parquet Snappy | |\n",
        "| Parquet Gzip | |\n",
        "\n",
        "### Speed Comparison (Write)\n",
        "| Format | Write Time |\n",
        "|---|---|\n",
        "| Parquet Uncompressed | |\n",
        "| Parquet Snappy | |\n",
        "| Parquet Gzip | |\n",
        "\n",
        "### Compression Comparison\n",
        "| Format | Compression Ratio |\n",
        "|---|---|\n",
        "| CSV | |\n",
        "| Parquet Uncompressed | |\n",
        "| Parquet Snappy | |\n",
        "| Parquet Gzip | |"
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "## SECTION 14 : CONCLUSION\n",
        "\n",
        "* **CSV vs Parquet:** Parquet is columnar, which makes it much more efficient for analytical queries than CSV (row-based) because it allows for column pruning and better compression.\n",
        "* **Snappy vs Gzip:** Snappy is optimized for speed and is the default for Spark. Gzip offers better compression ratios but is more CPU-intensive and slower.\n",
        "* **Storage savings:** Parquet significantly reduces storage costs by leveraging columnar compression.\n",
        "* **Performance improvement:** Parquet limits I/O by only reading necessary columns, significantly speeding up query times.\n",
        "* **Importance for organizations such as SNIM and SOMELEC:** These organizations generate massive volumes of operational data. Using efficient storage formats like Parquet ensures faster reporting, reduced storage costs, and better scalability for their data lakes.\n",
        "* **Strategic decision:** Choosing the right format impacts performance, infrastructure costs, and the overall agility of a Big Data platform."
      ]
    },
    {
      "cell_type": "markdown",
      "metadata": {},
      "source": [
        "--- \n",
        "## Commands Executed Outside Notebook\n",
        "\n",
        "```bash\n",
        "docker compose up -d\n",
        "hdfs dfs -mkdir -p /data\n",
        "hdfs dfs -put nyc_taxi.csv /data/\n",
        "hdfs dfs -ls /data\n",
        "hdfs dfs -du -h /output/parquet_uncompressed\n",
        "hdfs dfs -du -h /output/parquet_snappy\n",
        "hdfs dfs -du -h /output/parquet_gzip\n",
        "hdfs fsck /output/parquet_snappy -files -blocks -locations\n",
        "```"
      ]
    }
  ],
  "metadata": {
    "kernelspec": {
      "display_name": "Python 3",
      "language": "python",
      "name": "python3"
    },
    "language_info": {
      "codemirror_mode": {
        "name": "ipython",
        "version": 3
      },
      "file_extension": ".py",
      "mimetype": "text/x-python",
      "name": "python",
      "nbconvert_exporter": "python",
      "pygments_lexer": "ipython3",
      "version": "3.8.0"
    }
  },
  "nbformat": 4,
  "nbformat_minor": 4
}

with open(r"c:\Users\user\Desktop\M2\big data\project\Sujet_1_Ingenierie_du_Stockage.ipynb", "w", encoding="utf-8") as f:
    json.dump(notebook, f, indent=2)

print("Notebook generated successfully!")
