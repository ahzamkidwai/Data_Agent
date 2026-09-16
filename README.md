# Data Agent

A lightweight AI-powered data workflow that routes user requests between ETL tasks and SQL analytics. The project combines LangChain/LangGraph agents with PostgreSQL and data extraction utilities to help users transform raw data sources into queryable, analysis-ready datasets.

## Project short description for GitHub

AI-powered data agent for ETL and SQL querying with PostgreSQL-backed analytics workflows.

## Overview

This repository is designed to help users interact with data using natural-language instructions. Instead of writing ETL code or SQL manually, the system routes a request to the most appropriate agent:

- ETL Agent: extracts data from APIs and transforms it into CSV/JSON outputs.
- SQL Agent: curates user questions, retrieves database schema context, generates SQL, validates safety, and executes queries.
- Data Agent Router: decides whether a request is ETL-related or SQL-related.

The project is built around Python, LangChain, LangGraph, PostgreSQL, and Pandas.

## Features

- Natural-language routing between SQL and ETL tasks
- API data extraction into structured formats
- Data transformation using Pandas-based execution logic
- Postgres schema discovery for SQL generation
- SQL safety check before execution
- Graph-based agent orchestration with LangGraph

## Repository structure

```text
Data Agent/
├── README.md
├── pyproject.toml
├── feed_data.py
├── src/
│   ├── agents/
│   │   ├── data_agent.py
│   │   ├── etl_analyst.py
│   │   ├── scratch.py
│   │   └── sql_analyst.py
│   ├── data/
│   │   ├── payments.csv
│   │   ├── ratings.csv
│   │   ├── rides.csv
│   │   ├── users.csv
│   │   ├── vehicles.csv
│   │   ├── extract/
│   │   │   └── Extracted_data.csv
│   │   └── transform/
│   ├── data_agent/
│   │   └── __init__.py
│   ├── models/
│   │   └── schema.py
│   └── utils/
│       ├── database.py
│       ├── etl_tools.py
│       └── llm_pick.py
└── .env (optional, local configuration)
```

## Main components

### 1. Router / orchestration
Located in `src/agents/data_agent.py`

- Routes incoming requests to either the SQL or ETL workflow.
- Uses a structured LLM response to classify questions.

### 2. ETL workflow
Located in `src/agents/etl_analyst.py` and `src/utils/etl_tools.py`

- Extracts data from REST APIs.
- Saves results as CSV or JSON.
- Transforms files with Pandas based on user intent.

### 3. SQL workflow
Located in `src/agents/sql_analyst.py`

- Curates the user question.
- Pulls database schema metadata.
- Generates a SQL query for Postgres.
- Validates that the query is safe.
- Executes it and returns a human-friendly answer.

### 4. Database utilities
Located in `src/utils/database.py`

- Connects to PostgreSQL.
- Retrieves schema information.
- Executes validated SQL queries.

## Setup

### Prerequisites

- Python 3.11+
- PostgreSQL database
- API access for the LLM provider in use
- A valid `.env` file with your credentials

### Install dependencies

Using `pip`:

```bash
pip install -r requirements.txt
```

This project is configured with `pyproject.toml`, so a modern Python workflow is also supported using `uv`:

```bash
uv sync
```

### Environment variables

Create a `.env` file in the project root and add the variables required by the scripts. For example:

```env
DB_HOST=localhost
DB_PORT=5432
DB_DATABASE=your_database
DB_USER=your_user
DB_PASSWORD=your_password

host=localhost
port=5432
database=your_database
user=your_user
password=your_password
```

> The exact environment variable names depend on the file you are running. Some scripts use the `DB_*` convention, while others use lowercase names such as `host`, `database`, and `user`.

## Usage

### Load data into PostgreSQL

```bash
python feed_data.py
```

This script creates the main tables and loads the CSV data found in `src/data` into PostgreSQL.

### Run the data agent

```bash
python src/agents/data_agent.py
```

The router will decide whether to use the SQL or ETL agent based on the user request.

## Notes

- The project uses OpenRouter-based LLM selection via `src/utils/llm_pick.py`.
- The ETL pipeline is currently focused on API extraction and simple Pandas-based transformation.
- Some generated SQL and ETL logic is meant to be used as an experimental agent workflow and may require tuning for production-grade use cases.

## License

This project does not currently include a license file. Add one if you plan to publish it publicly on GitHub.

## Contributing

Pull requests and improvements are welcome. If you are extending the project, consider keeping the agent workflows modular and validating both SQL safety and ETL output before deployment.
