# Airbyte connector for the NHL API
[Airbyte](https://airbyte.com/) connector to load the following data from the official [NHL API](https://gitlab.com/dword4/nhlapi/-/blob/master/stats-api.md) (more streams will be implemented in the future):

- All Team Rosters for the current NHL season.
- Player details for each player on each of the team rosters. 
- Historic player stats for each player on each of the team rosters. 

# Usage
Clone the official [airbyte repository](https://github.com/airbytehq/airbyte) and dd the `source-nhl-api` folder to `airbyte/airbyte-integrations/connectors/`.

Run `cd airbyte/airbyte-integrations/connectors/` .

To run the connector locally, make sure to install the necessary requirements inside a virtual environment:
```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Let's read some data from the NHL API:
```
python main.py read --config sample_files/config.json --catalog sample_files/configured_catalog.json
```

Now let's run the connector using Docker and the Airbyte UI:
```
docker build . -t airbyte/source-nhl-api
cd ../../../
docker-compose up
```
Go to `localhost:8000` in your browser to open the Airbyte UI. Under "Settings", go to sources and add the `source-nhl-api` connection. You are now able to setup a new connection using the NHL API connector. 
