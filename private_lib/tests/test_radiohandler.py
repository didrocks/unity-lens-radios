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

from copy import deepcopy
from gi.repository import Gio
from gi.repository import Unity
import mock
from mock import Mock, patch
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
            self.assertIsInstance(unity_filters[i + 1], Unity.CheckOptionFilter)
            self.assertEqual(unity_filters[i + 1].get_option("1980"), None)
            self.assertNotEqual(unity_filters[i + 1].get_option("bar"), None)

    def test_is_radio_fulfill_filters(self):
        '''Prepare some radios and filters, and check that the criterias matches'''
        radio_attributes = {'name': "Radio1", "pictureBaseURL": "/root/", "picture1Name": "foo.png", "genresAndTopics": "Rock, Techno, Années 90s, Years 2100",
                         'currentTrack': "Radio1 current track", "country": "France", "rating": 5, "id": 42}
        valid_radio = Radio(radio_attributes, None)
        test_filter = {'decade': (1990, 2000), 'genre': ['Techno', 'Rock'], 'country': ['France']}
        self.assertTrue(self.radiohandler._is_radio_fulfill_filters(valid_radio, test_filter))

        # no matching country
        unvalid_radio_attr = deepcopy(radio_attributes)
        unvalid_radio_attr["country"] = 'UK'
        self.assertFalse(self.radiohandler._is_radio_fulfill_filters(Radio(unvalid_radio_attr, None), test_filter))

        # no matching genre
        unvalid_radio_attr = deepcopy(radio_attributes)
        unvalid_radio_attr["genresAndTopics"] = "Foo, Années 1990"
        self.assertFalse(self.radiohandler._is_radio_fulfill_filters(Radio(unvalid_radio_attr, None), test_filter))

        # no matching decade (below)
        unvalid_radio_attr = deepcopy(radio_attributes)
        unvalid_radio_attr["genresAndTopics"] = "Foo, Années 142"
        self.assertFalse(self.radiohandler._is_radio_fulfill_filters(Radio(unvalid_radio_attr, None), test_filter))

        # no matching decade (above)
        unvalid_radio_attr = deepcopy(radio_attributes)
        unvalid_radio_attr["genresAndTopics"] = "Foo, Années 4242"
        self.assertFalse(self.radiohandler._is_radio_fulfill_filters(Radio(unvalid_radio_attr, None), test_filter))

        # valid radio as no genre
        valid_radio_attr = deepcopy(radio_attributes)
        valid_radio_attr["genresAndTopics"] = "Années 90s, Years 2100"
        self.assertTrue(self.radiohandler._is_radio_fulfill_filters(Radio(valid_radio_attr, None), test_filter))

        # valid radio as no decade
        valid_radio_attr = deepcopy(radio_attributes)
        valid_radio_attr["genresAndTopics"] = "Rock"
        self.assertTrue(self.radiohandler._is_radio_fulfill_filters(Radio(valid_radio_attr, None), test_filter))

        # filters checking:
        # no decade:
        test_filter = {'genre': ['Techno', 'Rock'], 'country': ['France']}
        self.assertTrue(self.radiohandler._is_radio_fulfill_filters(valid_radio, test_filter))

        # no genre
        test_filter = {'decade': (1990, 2000), 'country': ['France']}
        self.assertTrue(self.radiohandler._is_radio_fulfill_filters(valid_radio, test_filter))

        # no country
        test_filter = {'decade': (1990, 2000), 'genre': ['Techno', 'Rock']}
        self.assertTrue(self.radiohandler._is_radio_fulfill_filters(valid_radio, test_filter))

    # TODO: test act
    def test_return_active_filters(self):
        '''Testing that active filters that are returned have the expected form'''
        def return_mock_filter_with_active_options(domain):
            obj = Mock()
            if domain == "decade":
                obj.get_first_active.return_value = 1900
                obj.get_last_active.return_value = 1950
            elif domain == 'genre' or domain == 'country':
                if domain == 'genre':
                    dom_id = 1
                if domain == 'country':
                    dom_id = 2
                active = Mock()
                active.active = True
                active.id = dom_id + 42
                unactive = Mock()
                unactive.active = False
                unactive.id = dom_id + 4242
                obj.options = (active, unactive)
            return obj

        def return_mock_filter_with_no_decade(domain):
            if domain != 'decade':
                return return_mock_filter_with_active_options(domain)
            decade_filter_result = Mock()
            decade_filter_result.get_first_active.return_value = None
            decade_filter_result.get_last_active.return_value = None
            return decade_filter_result

        def return_mock_filter_with_no_genre(domain):
            if domain != 'genre':
                return return_mock_filter_with_active_options(domain)
            genre_filter_result = Mock()
            unactive = Mock()
            unactive.active = False
            genre_filter_result.options = [unactive]
            return genre_filter_result

        def return_mock_filter_with_no_country(domain):
            if domain != 'country':
                return return_mock_filter_with_active_options(domain)
            genre_filter_result = Mock()
            unactive = Mock()
            unactive.active = False
            genre_filter_result.options = [unactive]
            return genre_filter_result

        scope = Mock()
        scope.get_filter = return_mock_filter_with_active_options
        self.assertEquals(self.radiohandler._return_active_filters(scope),
                          {'genre': {43}, 'country': {44}, 'decade': [1900, 1950]})

        # testing no having decade parameter
        scope.get_filter = return_mock_filter_with_no_decade
        self.assertEquals(self.radiohandler._return_active_filters(scope), {'genre': {43}, 'country': {44}})

        scope.get_filter = return_mock_filter_with_no_genre
        self.assertEquals(self.radiohandler._return_active_filters(scope), {'country': {44}, 'decade': [1900, 1950]})

        scope.get_filter = return_mock_filter_with_no_country
        self.assertEquals(self.radiohandler._return_active_filters(scope), {'genre': {43}, 'decade': [1900, 1950]})
