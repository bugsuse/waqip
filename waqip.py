# coding: utf-8

"""
    To access air quality data from World Air Quality Index Project

    @author:
    @date:
"""

import numpy as np
import pandas as pd

import requests

class WAQIP(object):
    '''To access air quality from World Air Quality Index Project
    '''
    def __init__(self, token):
        '''Initial
        :param token: token to access air quality
        '''

        self.token = token

    def get_city(self, city):
        '''To access air quality specific city or station
        :param city (integer): specific city or station id
        :return: df (pandas.DataFrame): dataframe with air quality specific city
        '''
        self.city = city
        self.url = 'https://api.waqi.info/feed/@{0}/?token={1}'.format(self.city, self.token)

        urls = requests.request(method='get', url=self.url)
        df = self._parse_json(urls.json())

        return df

    def get_latlon(self, latitudes, longitudes):
        '''To access air quality specific latitude and longitude coordinate
        :param latitudes (float): latitudes for assigned station
        :param longitudes (float): longitudes for assigned station
        :return: df (pandas.DataFrame): dataframe with air quality specific latitude and longitude coordinate
        '''
        self.laitudes, self.longitudes = latitudes, longitudes
        self.url = 'https://api.waqi.info/feed/geo:{0};{1}/?token={2}'.format(latitudes, longitudes, self.token)

        urls = requests.request(method='get', url=self.url)
        df = self._parse_json(urls.json())

        return df

    def search(self, keyword):
        '''
        :param keyword (str): keyword to search air quality, such as city or station name
        :return: json with searching results
        '''
        self.url = 'https://api.waqi.info/search/?token={0}&keyword={1}'.format(self.token, keyword)

        return requests.request(method='get', url=self.url).json()

    def get_map_bound(self, latlng):
        '''
        :param latlng (list or np.array): the latitude and longitude coordinates for map bound, and start latitude,
                    longitude and end latitude, longitude, respectively
        :return: json with air quality
        '''

        self.url = 'https://api.waqi.info/map/bounds/?latlng={0},{1},{2},{3}&token={4}'.format(latlng[0],
                                                                                               latlng[1],
                                                                                               latlng[2],
                                                                                               latlng[3],
                                                                                               self.token)
        return requests.request(method='get', url=self.url).json()

    def _parse_json(self, aqid):
        '''To parse air quality json data
        :param aqid: air quality directory
        :return: df (pandas.DataFrame): dataframe with air quality
        '''
        columns = ['date', 'tz', 'city', 'idx', 'lat', 'lon',
                   'aqi', 'pm25', 'pm10', 'so2', 'no2', 'o3', 'co',
                   'h', 't', 'r', 'w']
        df = pd.DataFrame(columns=columns)

        if isinstance(aqid, dict):
            self.status = aqid.get('status', None)
            self.data = aqid.get('data', None)
        else:
            raise ValueError('URL Wrong: {0}.'.format(self.url))

        if self.status == 'ok':
            if isinstance(self.data, dict):
                city = self.data.get('city', None)
                time = self.data.get('time', None)
                iaqi = self.data.get('iaqi', None)
                attb = self.data.get('attributions', None)
                df.loc[0, 'aqi'] = self.aqi = self.data.get('aqi', None)
                df.loc[0, 'idx'] = self.data.get('idx', None)

                if isinstance(city, dict):
                    df.loc[0, 'city'] = self.name = city.get('name', None)
                    geo = city.get('geo', None)
                    if isinstance(geo, list) and len(geo) == 2:
                        df.loc[0, 'lat'] = self.latitude = np.float(geo[0])
                        df.loc[0, 'lon'] = self.longitude = np.float(geo[1])
                else:
                    df.loc[0, 'city'] = self.city = None
                    df.loc[0, 'lat'] = self.latitude = None
                    df.loc[0, 'lon'] = self.longitude = None

                if isinstance(time, dict):
                    df.loc[0, 'date'] = self.date = time.get('s', None)
                    df.loc[0, 'tz'] = self.tz = time.get('tz', None)
                else:
                    df.loc[0, 'date'] = self.date = time.get('s', None)
                    df.loc[0, 'tz'] = self.tz = time.get('tz', None)

                for i in ['pm25', 'pm10', 'so2', 'no2', 'o3', 'co', 'h', 't', 'r', 'w']:
                    df.loc[0, i] = self._parse(iaqi, i)
            else:
                print('city/station is {0}, status is ok, but data is {1}, and return df with None.'.format(self.city,
                                                                                                             self.data))
                df.loc[0, :] = None
            return df
        elif self.status in ['nug', 'retry']:
            if self.city is None:
                return self.get_latlon(self.latitudes, self.longitudes)
            else:
                return self.get_city(self.city)
        elif self.status == 'error':
            raise ValueError(aqid.get('data', None), self.city)
        elif self.status == 'nope':
            print('city/station: {0} maybe no data. and status : {1} and response: {2}.'.format(self.city, self.status, self.data))
        else:
            print('status : {0}\ndata:{1}.'.format(self.status, self.data))
            raise ValueError('What happened?')

    def _parse(self, iaqi, var):
        '''Nothing
        '''
        if isinstance(iaqi, dict):
            vard = iaqi.get(var, None)
        else:
            vard = None
        if isinstance(vard, dict):
            return vard.get('v', None)
        else:
            return None
