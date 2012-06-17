# -*- coding: utf-8 -*-
# Copyright: (C) 2012 Canonical
# Copyright: (C) 2012 Tristan Fischer (based on his work)
#
# Authors:
#  Didier Roche <didrocks@ubuntu.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import json
import locale
import logging
import urllib

from .radio import Radio

_log = logging.getLogger(__name__)


def singleton(cls):
    singleton.instances = {}

    def getinstance(*args, **kwargs):
        instances = singleton.instances
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return getinstance


class ConnectionError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


@singleton
class OnlineRadioInfo(object):
    '''Class to get radio informations from the web.

    If a language is provided (either at, de, en, fr) it will override the
    autodetection.
    en is the default'''

    MAIN_URLS = {'at': 'http://www.radio.at/',
                 'de': 'http://radio.de/info',
                 'en': 'http://rad.io/info',
                 'fr': 'http://radio.fr/info'}
    VALID_CATEGORY_TYPES = ('genre', 'topic', 'country', 'city', 'language')

    def __init__(self, language=None):
        if not language:
            try:
                language = locale.setlocale(locale.LC_MESSAGES, '').split('_')[0]
            except locale.Error:
                _log.debug('Current local {0} is not supported, falling back to en'.format(language))
                language = 'en'
        self.radio_base_url = self.MAIN_URLS.get(language, self.MAIN_URLS['en'])
        _log.debug('Selected radio for {0} language: {1}'.format(language, self.radio_base_url))

    def __str__(self):
        return('{0}, using radio: {1}'.format(repr(self), self.radio_base_url))

    def get_recommended_stations(self):
        '''returns a generator list of 12 editors recommended stations'''
        _log.debug('getting recommended stations')
        for json_radio in self._get_json_result_for_parameters('broadcast/editorialreccomendationsembedded'):
            yield Radio(json_radio, self)

    def get_top_stations(self):
        '''returns a generator list of the 100 most listen stations'''
        _log.debug('getting top stations')
        return self.get_stations_by_category('top')

    def get_most_wanted_stations(self, num_entries=25):
        '''Return a dict of most wanted Radios by types of recommendation, limited to num_entries per type

        Format is: {"recommended": (Radio generator), <- equivalent to get_recommended_stations()
                    "top":         (Radio generator), <- equivalent to get_top_stations()
                    "local"        (Radio generator)} <- most listened radio locally
        '''
        _log.debug('getting {0} most wanted stations'.format(num_entries))
        json_result = self._get_json_result_for_parameters('account/getmostwantedbroadcastlists', sizeoflists=num_entries)
        result = {}
        for source_type, dest_type in (('recommendedBroadcasts', 'recommended'), ('topBroadcasts', 'top'), ('localBroadcasts', 'local')):
            result[dest_type] = (Radio(json_radio, self) for json_radio in json_result[source_type])
        return result

    def get_stations_by_searchstring(self, search_string, max_num_entries=1000):
        '''returns a generator list of Radio matching a search string,

        max_num_entries is the maximum number of results'''
        _log.debug('getting stations for {1} research, limited to {0} results'.format(search_string, max_num_entries))
        for json_radio in self._get_json_result_for_parameters('index/searchembeddedbroadcast', q=search_string,
                                                                                                start=0,
                                                                                                end=max_num_entries):
            yield Radio(json_radio, self)

    def get_details_by_station_id(self, station_id):
        '''Return some updated details info for the current station id

        Return format is a dict with additional infos.'''
        _log.debug('get details info for station numbered: {0}'.format(station_id))
        radio_details = {}
        json_details = self._get_json_result_for_parameters('broadcast/getbroadcastembedded', broadcast=station_id)
        # successfull search
        if 'streamURL' in json_details:
            radio_details['city'] = json_details['city']
            radio_details['current_track'] = json_details['currentTrack']
            radio_details['description'] = json_details['description']
            radio_details['stream_urls'] = self._resolve_playlist(json_details['streamURL'])
            radio_details['web_link'] = json_details['link']

        return radio_details

    def get_category_types(self):
        '''returns a list of possible values of category_types

        This can be used by get_categories_by_category_type(category_type)
        and get_stations_by_category(category_type, category_value)'''
        _log.debug('returning category types')
        return self.VALID_CATEGORY_TYPES

    def get_categories_by_category_type(self, category_type):
        '''returns a list of possible values of category for a given category_type.

        This should be used only if you want to introspect in a ui the available categories'''
        _log.debug('returning available categories for category type [{0}'.format(category_type))
        return self._get_json_result_for_parameters('menu/valuesofcategory', category='_{0}'.format(category_type))

    def get_stations_by_category(self, category_type, category_value=''):
        '''returns a generator list of Radio for a given category of category_type'''
        _log.debug('getting stations for {1} in {0}'.format(category_type, category_value))
        for json_radio in self._get_json_result_for_parameters('menu/broadcastsofcategory', category='_{0}'.format(category_type),
                                                                                            value=category_value):
            yield Radio(json_radio, self)

    def _get_json_result_for_parameters(self, path, **parameters):
        '''Get a json resulting object from the selected radio.

        path represents the url path to get the request
        parameters are optional parameters given as GET param to the request'''

        response = self._url_request(path, **parameters)

        try:
            json_result = json.loads(response)
            _log.debug('Connection successfully completed done ({0} bytes) and returning: {1}'.format(len(response), json_result))
        except (ValueError, TypeError) as error:
            _log.warning("Couldn't convert the result into json: {0}. The Error is: {1}".format(response, error))
            raise ConnectionError(error)

        return json_result

    def _resolve_playlist(self, playlist_url):
        _log.debug('Resolving playlist: {0}'.format(playlist_url))

        stream_url = []
        if playlist_url.endswith('m3u') or playlist_url.endswith('pls'):
            response = self._url_request(playlist_url)

        if playlist_url.endswith('m3u'):
            _log.debug('m3u file found')
            for entry in response.splitlines():
                if entry and not entry.strip().startswith('#'):
                    stream_url.append(entry.strip())

        elif playlist_url.endswith('pls'):
            _log.debug('pls file found')
            for line in response.splitlines():
                if line.strip().startswith('File'):
                    stream_url.append(line.split('=')[1])

        if not stream_url:
            _log.debug('Failing to parse it or to find a useful playlist, trying to assign it directly')
            stream_url = [playlist_url]
        return stream_url

    def _url_request(self, path, **parameters):
        '''Get a response for a particular path

        path represents the url path to get the request
        parameters are optional parameters given as GET param to the request

        Returns the reponse'''

        url = '{website}/{path}'.format(website=self.radio_base_url, path=path)
        if parameters:
            url += '?{0}'.format(urllib.parse.urlencode(parameters))
        req = urllib.request.Request(url)

        try:
            _log.debug('Contacting {0}'.format(url))
            response = urllib.request.urlopen(req)
            encoding = response.headers.get_content_charset()
            result = response.readall().decode(encoding)
        except (urllib.error.HTTPError, urllib.error.URLError) as error:
            _log.warning('Get a networking error: {0}'.format(error))
            raise ConnectionError(error)

        return result
