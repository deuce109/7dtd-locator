import logging
from typing import Any, Callable, Dict, List
import requests
import json

class Marker(dict):
    x: float
    y: float
    icon: str = 'https://upload.wikimedia.org/wikipedia/commons/e/ec/Twemoji2_1f3da.svg'

    def __init__ (self, x: float, y: float, icon:str = None):
        self.x = x
        self.y = y
        self.icon = icon if icon else self.icon

class DashboardAPI():
     
    _session: requests.Session

    _base_url: str

    def __init__(self, base_url="http://localhost:8080", token_file="dashboard-token.json"):

        tokens: List[Dict[str,str]] = []
        with open(token_file) as tokens_file:
            tokens = json.load(tokens_file)

        if len(tokens) == 0:
            raise Exception("Dashboard token not found")
        
        locator_token = [token for token in tokens if token.get("name", None) == 'Locator'][0]

        if locator_token:
            
            self._session = requests.Session()
            self._base_url = base_url

            headers = {}

            headers['X-SDTD-API-TOKENNAME'] = locator_token['name']
            headers['X-SDTD-API-SECRET'] = locator_token['secret']

            self._session.headers = headers

        else:
            raise Exception("Dashboard token not found")

    def _get_json_key(self, response: requests.Response):
        return response.json()['data']

    def _build_url(self, subpath: str):

        return self._base_url + subpath
    
    def _process_response(self, res: requests.Response, data_retrieval: Callable[[requests.Response], Any] = None):
        if res.ok:
            if data_retrieval:
                return data_retrieval(res)
            else:
                logging.info(f"Response: {res.status_code}  {res.text}")
                return
        else:
            logging.warning(f'Status Code: {res.status_code}  Reason: {res.text}')
            return

    def add_marker_to_map(self, marker: Marker):
            
        response = self._session.post( self._build_url('/api/markers'), json=marker.__dict__)
        self._process_response(response)

    def get_markers(self):

        response = self._session.get(self._build_url('/api/markers'))
        return self._process_response(response, data_retrieval=self._get_json_key)
    
    def get_players(self):

        response = self._session.get(self._build_url('/api/player'))
        return self._process_response(response, data_retrieval=self._get_json_key)['players']
    
    def get_hostiles(self):

        response = self._session.get(self._build_url('/api/hostile'))
        return self._process_response(response, data_retrieval=self._get_json_key)
    
    def get_animals(self):

        response = self._session.get(self._build_url('/api/animal'))
        return self._process_response(response, data_retrieval=self._get_json_key)

    def clear_markers(self):
        
        markers = self.get_markers()

        for marker in markers:
            response = self._session.delete(self._build_url(f"/api/markers/{marker['id']}"))
            self._process_response(response)

    def add_markers(self, markers: List[Marker]):

        for marker in markers:
            self.add_marker_to_map(marker)
