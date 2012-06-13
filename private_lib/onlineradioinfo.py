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

    def get_category_types(self):
        '''returns a list of possible values of category_types

        This can be used  by get_categories_by_category_type(category_type)
        and get_stations_by_category(category_type, category_value)'''

        _log.debug('return category types')
        return self.VALID_CATEGORY_TYPES

    def _get_json_result_for_parameters(self, path, **parameters):
        '''Get a json resulting object from the selected radio.

        path represents the url path to get the request
        parameters are optional parameters given as GET param to the request'''

        url = '{website}/{path}?{parameters}'.format(website=self.radio_base_url, path=path,
                                                     parameters=urllib.parse.urlencode(parameters))
        req = urllib.request.Request(url)

        try:
            _log.debug('Contacting {0}'.format(url))
            response = urllib.request.urlopen(req)
            encoding = response.headers.get_content_charset()
            result = response.readall().decode(encoding)
        except (urllib.error.HTTPError, urllib.error.URLError) as error:
            _log.warning('Get a networking error: {0}'.format(error))
            raise ConnectionError(error)

        try:
            json_result = json.loads(result)
            _log.debug('Connection successfully completed done ({0} bytes) and returning: {1}'.format(len(result), json_result))
        except (ValueError, TypeError) as error:
            _log.warning("Couldn't convert the result into json: {0}. The Error is: {1}".format(result, error))
            raise ConnectionError(error)

        return json_result


