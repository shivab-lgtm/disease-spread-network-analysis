# Disease Spread Network Analysis

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/shivab-lgtm/disease-spread-network-analysis/blob/main/Disease_Spread_Network_Data_Cleaning.ipynb)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Neo4j](https://img.shields.io/badge/Graph_Database-Neo4j_5.x-008CC1?logo=neo4j)
![Flutter](https://img.shields.io/badge/Frontend-Flutter_Web-02569B?logo=flutter)

> **"A Disease Spread Network Analysis is a healthcare data analytics system that studies the relationships between diseases, locations, and healthcare facilities to understand how diseases are distributed and connected across regions. It uses graph databases, GIS visualization, and data processing techniques to identify disease clusters, analyze geographic patterns, and provide insights into disease occurrence and spread trends."**

---

## 📌 Project Overview

This platform integrates data engineering, spatial epidemiology, and graph theory into an end-to-end surveillance pipeline:
1. **Raw Surveillance Ingestion**: Intake of raw, uncurated electronic health records (EHR) containing real-world defects.
2. **Data Cleaning & Standardization**: Automated pipeline implemented in Python & Pandas (available as a Google Colab notebook).
3. **Graph ETL & Modeling**: Relational-to-Graph decomposition loaded into **Neo4j** to model multi-hop disease transmission paths.
4. **GIS Visualization & Web Interface**: Interactive geographical cluster and time-series incidence analytics dashboard.

---

## 🗂️ Repository Structure

| File / Directory | Description |
| :--- | :--- |
| **[`Disease_Spread_Network_Data_Cleaning.ipynb`](Disease_Spread_Network_Data_Cleaning.ipynb)** | Complete data cleaning, quality profiling, and Neo4j graph export pipeline. |
| **[`raw_disease_surveillance_data.csv`](raw_disease_surveillance_data.csv)** | Raw, uncleaned dataset (155 records) exhibiting duplicates, typos, missing GPS coordinates, and non-standard dates. |
| **[`cleaned_disease_surveillance_data.csv`](cleaned_disease_surveillance_data.csv)** | Cleaned, validated, and geocoded master surveillance dataset (150 records). |
| **[`Disease_Spread_Network_Website.html`](Disease_Spread_Network_Website.html)** | Standalone, interactive zero-install web application for quick presentation. |
| **[`EpiWatchFlutter-master/`](EpiWatchFlutter-master/)** | Full Flutter Web application and FastAPI backend service. |

---

## 🧹 Data Cleaning Pipeline & Techniques

The data cleaning pipeline in [`Disease_Spread_Network_Data_Cleaning.ipynb`](Disease_Spread_Network_Data_Cleaning.ipynb) addresses five major categories of real-world healthcare data noise:

### 1. Deduplication (Entity Reconciliation)
* **Technique**: Primary key tracking and deduplication (`drop_duplicates(subset=['report_id'], keep='first')`).
* **Why**: Prevents inflated epidemiological case counts caused by redundant hospital network transmissions.

### 2. Temporal Normalization (Mixed Date Formatting)
* **Technique**: Multi-pattern parsing (`pd.to_datetime(format='mixed')`) normalized to standard ISO-8601 (`YYYY-MM-DD`).
* **Why**: Standardizes inconsistent clinic logs (`03/08/2026`, `2026-08-03`, `03-08-2026`) and filters invalid date strings for rolling weekly trend calculations.

### 3. Semantic Canonicalization (Clinical Disease Taxonomy)
* **Technique**: Case-insensitive string normalization and clinical synonym dictionary mapping.
* **Why**: Unifies disparate terms (`"acute respiratory infection"`, `"COVID-19"`, `"Flu / Influenza"`) into standardized clinical categories (**Respiratory**, **Vector-borne**, **Gastrointestinal**), enabling syndromic cluster detection.

### 4. Fuzzy Geocoding & Master Entity Matching
* **Technique**: Substring/regex matching against a master spatial facility registry based on OpenStreetMap Healthsites.
* **Why**: Resolves abbreviations and typos (`"kem hosp"`, `"K.E.M. Hospital"`, `"ltmg sion"`) and infills missing latitude and longitude coordinates essential for GIS map rendering.

### 5. Numerical Sanitization & Integrity Constraints
* **Technique**: Numeric coercion, NaN imputation, and logical range bounds (`new_cases >= 0`).
* **Why**: Eliminates typographical data entry defects such as negative case counts (`-5`).

---

## 🕸️ Neo4j Graph Database Model

### Schema Entities:
- **`(:Facility)`**: Healthcare facilities (Hospitals, Clinics, Polyclinics) with weekly caseload metrics.
- **`(:Location)`**: Geographic districts and zones (Mumbai City, Mumbai Suburban, Thane, Pune).
- **`(:Disease)`**: Pathogens with syndromic categories and $R_0$ transmission estimates.
- **`(:Cluster)`**: Detected epidemiological outbreak signals grouping affected facilities.

### Graph Relationships:
- `(:Facility)-[:LOCATED_IN]->(:Location)`
- `(:Facility)-[:PART_OF_CLUSTER]->(:Cluster)`
- `(:Facility)-[:REPORTS_OUTBREAK]->(:Disease)`
- `(:Disease)-[:SPREAD_TO]->(:Location)`

### Key Analytical Cypher Queries:

#### 1. Display Full Disease Spread Network
```cypher
MATCH (n) RETURN n;
