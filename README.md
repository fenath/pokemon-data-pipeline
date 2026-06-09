# Pokémon Data Pipeline

A data engineering project built with **Python** and **Google BigQuery**, using the **PokéAPI** as the data source and implementing a **Bronze → Silver → Gold** architecture for analytical workloads.

## Overview

This project demonstrates the development of a complete ELT pipeline, from API ingestion to analytical data modeling.

The pipeline extracts Pokémon data from the PokéAPI, stores the raw information in a Bronze layer, cleans and deduplicates records in the Silver layer, and produces business-ready analytical datasets in the Gold layer.

The project was created as a portfolio piece to showcase data engineering concepts such as data modeling, SQL analytics, API integration, incremental loading, and layered warehouse architecture.

## Architecture

```text
PokéAPI
    │
    ▼
Python Ingestion Scripts
    │
    ▼
BigQuery Bronze Layer
    │
    ▼
BigQuery Silver Layer
    │
    ▼
BigQuery Gold Layer
    │
    ▼
Analytical SQL Queries
```

## Technologies

* Python
* Google Cloud Platform
* Google BigQuery
* SQL
* Pandas
* Requests

## Data Warehouse Layers

### Bronze

Stores raw ingested data while preserving ingestion history.

Tables:

* pokemon_details
* pokemon_species
* pokemon_types
* pokemon_stats
* pokemon_moves
* pokemon_abilities
* evolution_chains
* pkm_type_relations

### Silver

Applies deduplication using `ROW_NUMBER()` and keeps the latest version of each entity.

### Gold

Contains business-oriented datasets ready for analysis.

Main tables:

* pokemon_complete
* pokemon_stats_pivot
* pokemon_fraquezas
* pokemon_evolution

## Features

* REST API ingestion
* Incremental loading
* Layered data warehouse architecture
* Recursive SQL for evolution chains
* Window Functions
* Type weakness calculation
* Analytical SQL datasets

## Example analyses

* Top Pokémon by Base Stat Total
* Top 3 Pokémon of each type
* Average statistics by generation
* Type weakness analysis
* Evolution chain analysis
* Type distribution
* Ranking by speed, attack and defense

## Repository structure

```text
.
├── ingestion/
├── sql/
│   ├── bronze/
│   ├── silver/
│   ├── gold/
│   └── analytics/
├── diagrams/
├── docs/
└── README.md
```

## Future improvements

* Workflow orchestration
* Automated tests
* Dashboard integration
* Incremental scheduling
* Data quality validation

## Purpose

This project was developed for learning and portfolio purposes, demonstrating practical skills in modern data engineering using Google Cloud Platform and SQL-based analytical modeling.
