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

from gi.repository import Gio
from gi.repository import Unity
import json
import mock
from mock import patch, Mock
import unittest

from ..radiohandler import singleton, RadioHandler
from ..radio import Radio


class RadioHandlerTests(unittest.TestCase):

    def setUp(self):
        # create the singleton. Don't call the super method for children if they need
        # to create the singleton with other parameters
        self.radiohandler = RadioHandler()

    def tearDown(self):
        # remove the current singleton
        try:
        # need to use the singleton to find the class as it's decorated
        # and report a getinstance instance otherwise
        # TODO: is there a better way to do that?
            del(singleton.instances[RadioHandler().__class__])
        except KeyError:
            pass

    def test_is_singleton(self):
        '''Test that RadioHandler is a singleton'''
        self.assertEqual(self.radiohandler, RadioHandler())

    def test_ensure_no_last_result(self):
        '''Ensure that once it's created fresh, we have no previous result'''
        self.assertEqual(self.radiohandler._last_all_radios, None)
        self.assertEqual(self.radiohandler._last_search, None)

    def test_getting_unity_categories(self):
        '''Test getting fresh new unity categories'''
        # FIXME: replace with local assets
        categories = [{'name': 'cat1',
                       'icon': Gio.ThemedIcon.new('/usr/share/icons/unity-icon-theme/places/svg/group-mostused.svg')},
                      {'name': 'cat2',
                       'icon': Gio.ThemedIcon.new('/usr/share/icons/unity-icon-theme/places/svg/group-recent.svg')}]
        unity_cat = self.radiohandler.get_unity_radio_categories(categories)
        self.assertEqual(len(unity_cat), 2)
        self.assertEqual(unity_cat[0].get_property('name'), 'cat1')
        self.assertEqual(unity_cat[1].get_property('name'), 'cat2')
        for i in range(2):
            self.assertIsInstance(unity_cat[i].get_property('icon_hint'), Gio.ThemedIcon)
            self.assertEqual(unity_cat[i].get_property('renderer'), 'tile-horizontal')

    @patch('private_lib.radiohandler.OnlineRadioInfo')
    def test_getting_filters(self, onlineradioinfomock):
        '''Test getting fresh new unity filters'''
        onlineradioinfomock().get_categories_by_category_type.return_value = ["foo", "bar"]
        unity_filters = self.radiohandler.get_unity_radio_filters()
        self.assertEqual(onlineradioinfomock().get_categories_by_category_type.call_args_list[0], mock.call('genre'))
        self.assertEqual(onlineradioinfomock().get_categories_by_category_type.call_args_list[1], mock.call('country'))
        self.assertEqual(len(onlineradioinfomock().get_categories_by_category_type.call_args_list), 2)
        self.assertEqual(len(unity_filters), 3)
        self.assertIsInstance(unity_filters[0], Unity.MultiRangeFilter)
        self.assertNotEqual(unity_filters[0].get_option("1980"), None)
        self.assertEqual(unity_filters[0].get_option("bar"), None)

        for i in range(2):
            self.assertIsInstance(unity_filters[i+1], Unity.CheckOptionFilter)
            self.assertEqual(unity_filters[i+1].get_option("1980"), None)
            self.assertNotEqual(unity_filters[i+1].get_option("bar"), None)

    def test_is_radio_fulfill_filters(self):
        '''Prepare some radios and filters, and check that the criterias matches'''
        radios = (Radio({'name': "Radio1", "pictureBaseURL": "/root/", "picture1Name": "foo.png", "genresAndTopics": ["Rock", "Techno"],
                         'currentTrack': "Radio1 current track", "country": "France", "rating": 5, "id": 42}),
                  Radio({'name': "Radio2", "pictureBaseURL": "/root/", "picture2Name": "bar.png", "genresAndTopics": ["Techno"],
                         'currentTrack': "Radio2 current track", "country": "UK", "rating": 4, "id": 123}),
                  Radio({'name': "Radio3", "pictureBaseURL": "/root/", "picture3Name": "baz.png", "genresAndTopics": ["Techno"],
                         'currentTrack': "Radio3 current track", "country": "France", "rating": 4, "id": 123}))
        filters = {'decade': [90-00], 'genre': ['Techno', 'Rock'], 'country': ['France']}

        # TODO: do with multiple filters, check the result for each radio

   # TODO: later integration tests ensuring that:
   # - they have the right categories
   # - the search is the expected one
