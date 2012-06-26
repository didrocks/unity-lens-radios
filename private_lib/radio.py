# -*- coding: utf-8 -*-
# Copyright: (C) 2012 Canonical
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

import logging
import re

_log = logging.getLogger(__name__)


class Radio(object):

    '''Represent a radio'''

    def __init__(self, data, onlineradioinfo):
        '''Tranform radio raw data to objects with the desired structure'''

        self.name = data['name']
        self.picture_url = '{0}{1}'.format(data['pictureBaseURL'],
                                           data['picture1Name'])
        if not data['picture1Name']:
            self.picture_url = 'audio-x-generic'
        year_regexp = re.compile("(Années*|Years*) (\d*)")
        genres_list = []
        decades_list = []
        for genre_candidate in [x.strip() for x in data['genresAndTopics'].split(',')]:
            try:
                decade = year_regexp.split(genre_candidate)[2]
                decades_list.append(transform_decade_str_in_int(decade))
            except IndexError:
                genres_list.append(genre_candidate)
        self.decades = decades_list
        self.genres = genres_list

        self.current_track = data['currentTrack']
        self.country = data['country']
        self.rating = data['rating']
        self.id = data['id']
        self.city = None
        self.description = None
        self.stream_urls = None
        self.web_link = None

        # keep it for lazy loading of more info on the radio
        self._onlineradioinfo = onlineradioinfo

    def refresh_details_attributes(self):
        '''Load details attributes and merge them into the object'''
        details = self._onlineradioinfo.get_details_by_station_id(self.id)
        self.city = details['city']
        self.current_track = details['current_track']
        self.description = details['description']
        self.stream_urls = details['stream_urls']
        self.web_link = details['web_link']

    def __getattribute__(self, name):
        '''Lazy load some attributes and use that to refresh the current_track'''
        if object.__getattribute__(self, 'stream_urls') is None and name in ('city', 'description', 'stream_urls', 'web_link'):
            self.refresh_details_attributes()
        return object.__getattribute__(self, name)


def transform_decade_str_in_int(decade):
    '''Transform simple decade form, like 90 to 1900 and 00 to 2000.

    Keep full date as they are'''
    comparison_decade = int(decade)  # keep initial for 00 or 05 years
    if comparison_decade > 20 and comparison_decade < 100:
        return int('19{0}'.format(decade))
    elif comparison_decade < 20:
        return int('20{0}'.format(decade))
    return comparison_decade
