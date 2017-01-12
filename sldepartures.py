"""
SL departure fetcher
by Gustaf Brahme
""" 

import base64
import json
import requests
import pytz
import math
from pytz import timezone
from datetime import datetime
from datetime import timedelta
 
API_BASE_URL = "http://api.sl.se/api2/realtimedeparturesV4.json"
tzSweden = timezone('Europe/Stockholm')
 
class SlDeparture:
    def __init__(self, key, siteId, transportType = "Buses"):
        self._key = key
        self._siteId = siteId
        self._transportType = transportType

    def __get_node(self, response, *ancestors):    
        document = response
        for ancestor in ancestors:
            if ancestor not in document:
                return {}
            else:
                document = document[ancestor]
        return document
 
    def get_minutes_left(self, json):
        nextDeparture = self.get_next_departure(json)     
        now = datetime.now(tzSweden)
        departureTime = datetime.strptime(nextDeparture["ExpectedDateTime"],"%Y-%m-%dT%H:%M:%S").replace(tzinfo=tzSweden)     
        timedelta = departureTime - now
        return int(math.floor(timedelta.total_seconds() / 60))
         
    def get_next_departure(self, json):
        items = self.__get_node(json,"ResponseData", self._transportType)
        return items[0]   
 
    def get_departures(self):
        url = API_BASE_URL + "?key=" + self._key + "&siteid=" + self._siteId + "&timewindow=60"
        response = requests.get(url)
        if response.status_code == 200:
            return json.loads(response.content.decode('UTF-8'),'UTF-8')
        else:
            raise Exception("Error: " + str(response.status_code) + str(response.content))
 
    def get_next(self):
        return self.get_minutes_left(self.get_departures()) 
    