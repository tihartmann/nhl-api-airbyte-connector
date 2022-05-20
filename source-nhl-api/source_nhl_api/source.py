#
# Copyright (c) 2021 Airbyte, Inc., all rights reserved.
#
from abc import ABC
from typing import Any, Iterable, List, Mapping, MutableMapping, Optional, Tuple

import requests
from airbyte_cdk.sources import AbstractSource
from airbyte_cdk.sources.streams import Stream
from airbyte_cdk.sources.streams.http import HttpStream
from airbyte_cdk.sources.streams.http.auth import TokenAuthenticator
from airbyte_cdk.models import SyncMode

class NhlApiStream(HttpStream, ABC):
    url_base = "https://statsapi.web.nhl.com/api/v1/"

    def next_page_token(self, response: requests.Response) -> Optional[Mapping[str, Any]]:
            """
            :param response: the most recent response from the API
            :return If there is another page in the result, a mapping (e.g: dict) containing information needed to query the next page in the response.
                    If there are no more pages in the result, return None.
            """
            return None

    def request_params(
        self, stream_state: Mapping[str, Any], stream_slice: Mapping[str, any] = None, next_page_token: Mapping[str, Any] = None
    ) -> MutableMapping[str, Any]:
        return {}

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        """
        TODO: Override this method to define how a response is parsed.
        :return an iterable containing each record in the response
        """
        yield from [response.json()]

class Teams(NhlApiStream):

    primary_key = "id"

    def path(self, **kwargs) -> str:
        return "teams"
    
    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()["teams"]

class TeamRosters(NhlApiStream):
    primary_key = "id"

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        team_id = stream_slice["team_id"]
        return f"teams/{team_id}"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice : Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {
            "expand": "team.roster",
            }
        return params
    
    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        teams_stream = Teams()
        for team in teams_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"team_id": team["id"]}, **kwargs)

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()["teams"]

class Players(NhlApiStream):

    primary_key = "id"

    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        player_id = stream_slice["player_id"]
        return f"people/{player_id}"

    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        teamRosters_stream = TeamRosters()
        for team in teamRosters_stream.read_records(sync_mode=SyncMode.full_refresh):
            for player in team["roster"]["roster"]:
                yield from super().read_records(stream_slice={"player_id": player["person"]["id"]}, **kwargs)

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()["people"]
    


class PlayerStats(NhlApiStream):

    primary_key = None
    
    def path(self, stream_slice: Mapping[str, Any], **kwargs) -> str:
        player_id = stream_slice["player_id"]
        return f"people/{player_id}/stats"

    def request_params(
        self,
        stream_state: Mapping[str, Any],
        stream_slice : Mapping[str, Any] = None,
        next_page_token: Mapping[str, Any] = None,
    ) -> MutableMapping[str, Any]:
        params = {
            "stats": "yearByYear",
        }
        return params
    
    def read_records(self, stream_slice: Optional[Mapping[str, Any]] = None, **kwargs) -> Iterable[Mapping[str, Any]]:
        players_stream = Players()
        for player in players_stream.read_records(sync_mode=SyncMode.full_refresh):
            yield from super().read_records(stream_slice={"player_id": player["id"]}, **kwargs)

    def parse_response(self, response: requests.Response, **kwargs) -> Iterable[Mapping]:
        yield from response.json()["stats"]

class SourceNhlApi(AbstractSource):
    def check_connection(self, logger, config) -> Tuple[bool, any]:
        teamRosters_stream = TeamRosters()
        players_stream = Players()
        playerStats_stream = PlayerStats()

        try:
            teamRosters_stream.read_records(sync_mode=SyncMode.full_refresh)
            players_stream.read_records(sync_mode=SyncMode.full_refresh)
            playerStats_stream.read_records(sync_mode=SyncMode.full_refresh)
            return True, None
        except Exception as e:
            return False, e


    def streams(self, config: Mapping[str, Any]) -> List[Stream]:
        return [
            #Teams(), 
            TeamRosters(),
            Players(),
            PlayerStats(),
            ]

