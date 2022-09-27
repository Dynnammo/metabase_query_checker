# Metabase Query Checker
This small project aims to provide a simple way for data analysts using [Metabase](https://metabase.com) to check if there's queries that aren't working (i.e. the request failed due to unknown error), and send a Rocket.Chat notification.

## Setup
This project is build with . 
1. If not install, install [Poetry](https://python-poetry.org/) following their guidelines [here](https://python-poetry.org/docs/#installation) 
2. Install dependencies : `poetry install`
3. Copy the `.env.example` into `.env` (`cp .env.example .env`) and fill it with your Metabase instance URL, your username and password to connect, and same for your Rocket.Chat credentials.
4. Launch the script : `poetry run check_queries`

## TODO
- [ ] Make Rocket.Chat notification optional
- [ ] More informations on error : name of the card, error message

