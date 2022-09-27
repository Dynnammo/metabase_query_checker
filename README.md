# Metabase Query Checker
This small project aims to provide a simple way for data analysts using [Metabase](https://metabase.com) to check if there's queries that aren't running (i.e. the request failed due to unknown error).

## Setup
This project is build with . 
1. If not install, install [Poetry](https://python-poetry.org/) following their guidelines [here](https://python-poetry.org/docs/#installation) 
2. Install dependencies : `poetry install`
3. Copy the `.env.example` into `.env` (`cp .env.example .env`) and fill it with your Metabase instance URL, your username and password to connect.
4. Launch the script : `poetry run check_queries`
