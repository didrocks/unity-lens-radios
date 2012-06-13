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

#import json
import locale
#from urllib.parse import urlencode
#from urllib.request import urlopen, Request
#from urllib.error import HTTPError, URLError


def singleton(cls):
    singleton.instances = {}

    def getinstance(*args, **kwargs):
        instances = singleton.instances
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return getinstance


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
                language = 'en'
        self._language = language
        self.radio_base_url = self.MAIN_URLS.get(self._language, self.MAIN_URLS['en'])

    def __str__(self):
        return('{0}, using lang: {1}'.format(repr(self), self._language))
