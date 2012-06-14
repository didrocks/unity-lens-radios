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
import unittest

from ..radio import Radio


class RadioTests(unittest.TestCase):

    def test_radio_constructor(self):
        '''Build a radio object and ensure it has the right attributes'''

        radio_data = json.loads('{"playable":"FREE","genresAndTopics":"Electro, Lounge","broadcastType":1,"picture1Name":"2511_fr_1.gif",'\
                                '"streamContentFormat":"MP3","currentTrack":"Wahoo - Holding You","country":"France","id":2511,"rank":199,'\
                                '"name":"Vmix Late","subdomain":"vmixlatemix","bitrate":128,"rating":5,'\
                                '"pictureBaseURL":"http://static.radio.de/images/broadcasts/"}')

        radio = Radio(radio_data, None)
        self.assertEqual(radio.name, 'Vmix Late')
        self.assertEqual(radio.picture_url, 'http://static.radio.de/images/broadcasts/2511_fr_1.gif')
        self.assertEqual(list(radio.genre), ['Electro', 'Lounge'])
        self.assertIsInstance(radio.genre, (a for a in [1]).__class__)
        self.assertEqual(radio.current_track, 'Wahoo - Holding You')
        self.assertEqual(radio.country, 'France')
        self.assertEqual(radio.rating, 5)
        self.assertEqual(radio.id, 2511)
        self.assertEqual(radio.stream_url, None)
        self.assertRaises(AttributeError, lambda: radio.playable)


