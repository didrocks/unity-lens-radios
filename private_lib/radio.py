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


class Radio(object):

    '''Represent a radio'''

    def __init__(self, data, onlineradioinfo):
        '''Tranform radio raw data to objects with the desired structure'''

        self.name = data['name']
        self.picture_url = '{0}{1}'.format(data['pictureBaseURL'],
                                           data['picture1Name'])
        self.genre = (x.strip() for x in data['genresAndTopics'].split(','))
        self.current_track = data['currentTrack']
        self.country = data['country']
        self.rating = data['rating']
        self.id = data['id']
        self.stream_url = None

        # keep it for lazy loading of more info on the radio
        self._onlineradioinfo = onlineradioinfo

        # TODO: get stream_url lazy (when activation happen)
