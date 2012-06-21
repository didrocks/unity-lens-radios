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

import json
from mock import patch
import unittest

from ..radio import Radio, transform_decade_str_in_int


class RadioTests(unittest.TestCase):

    def setUp(self):
        self.radio_data = json.loads('{"playable":"FREE","genresAndTopics":"Electro, Années 90, Years 00s, Years 1500, Years 80s, Lounge",'\
                                     '"broadcastType":1,"picture1Name":"2511_fr_1.gif",'\
                                     '"streamContentFormat":"MP3","currentTrack":"Wahoo - Holding You","country":"France","id":2511,"rank":199,'\
                                     '"name":"Vmix Late","subdomain":"vmixlatemix","bitrate":128,"rating":5,'\
                                     '"pictureBaseURL":"http://static.radio.de/images/broadcasts/"}')
        self.radio = Radio(self.radio_data, None)

    def test_radio_constructor(self):
        '''Build a radio object and ensure it has the right attributes'''

        radio = self.radio
        self.assertEqual(radio.name, 'Vmix Late')
        self.assertEqual(radio.picture_url, 'http://static.radio.de/images/broadcasts/2511_fr_1.gif')
        self.assertEqual(radio.genres, ['Electro', 'Lounge'])
        self.assertEqual(radio.decades, [1990, 2000, 1500, 1980])
        self.assertEqual(radio.current_track, 'Wahoo - Holding You')
        self.assertEqual(radio.country, 'France')
        self.assertEqual(radio.rating, 5)
        self.assertEqual(radio.id, 2511)
        self.assertRaises(AttributeError, lambda: radio.playable)

    def test_ensure_no_decade_if_nothing(self):
        '''Test that no decade is used if we have no decade on list'''
        radio_data = json.loads('{"playable":"FREE","genresAndTopics":"Electro, Lounge",'\
                                '"broadcastType":1,"picture1Name":"2511_fr_1.gif",'\
                                '"streamContentFormat":"MP3","currentTrack":"Wahoo - Holding You","country":"France","id":2511,"rank":199,'\
                                '"name":"Vmix Late","subdomain":"vmixlatemix","bitrate":128,"rating":5,'\
                                '"pictureBaseURL":"http://static.radio.de/images/broadcasts/"}')
        radio = Radio(radio_data, None)
        self.assertEqual(radio.genres, ['Electro', 'Lounge'])
        self.assertEqual(radio.decades, [])

    def test_refresh_details_attributes(self):
        '''Test refresh details radio attributes'''
        radio = self.radio
        with patch.object(radio, '_onlineradioinfo') as onelineradioinfo:
            onelineradioinfo.get_details_by_station_id.return_value = \
            {'city': 'Paris', 'current_track': 'Megashira - At Last',
             'description': 'Makes your nights sweeter !',
             'stream_urls': ['http://live2.vmix.fr:8010'], 'web_link': 'http://www.vmix.fr/'}
            self.assertEqual(radio.current_track, 'Wahoo - Holding You')
            radio.refresh_details_attributes()

            self.assertEqual(radio.city, 'Paris')
            self.assertEqual(radio.current_track, 'Megashira - At Last')
            self.assertEqual(radio.description, 'Makes your nights sweeter !')
            self.assertEqual(radio.stream_urls, ['http://live2.vmix.fr:8010'])
            self.assertEqual(radio.web_link, 'http://www.vmix.fr/')
            onelineradioinfo.get_details_by_station_id.assert_called_once_with(2511)

    def test_lazy_load_attributes(self):
        '''Test lazy loading details radio attributes'''
        radio = self.radio
        with patch.object(radio, '_onlineradioinfo') as onelineradioinfo:
            onelineradioinfo.get_details_by_station_id.return_value = \
            {'city': 'Paris', 'current_track': 'Megashira - At Last',
             'description': 'Makes your nights sweeter !',
             'stream_urls': ['http://live2.vmix.fr:8010'], 'web_link': 'http://www.vmix.fr/'}
            radio.id
            radio.current_track
            self.assertEquals(onelineradioinfo.get_details_by_station_id.call_count, 0)
            self.assertEquals(radio.city, 'Paris')
            self.assertEquals(onelineradioinfo.get_details_by_station_id.call_count, 1)
            self.assertEquals(radio.stream_urls, ['http://live2.vmix.fr:8010'])
            self.assertEquals(onelineradioinfo.get_details_by_station_id.call_count, 1)

    def test_transform_decade(self):
        '''Test different form of decade transformation'''
        self.assertEquals(transform_decade_str_in_int('00'), 2000)
        self.assertEquals(transform_decade_str_in_int('90'), 1990)
        self.assertEquals(transform_decade_str_in_int('1995'), 1995)
        self.assertEquals(transform_decade_str_in_int('230'), 230)
