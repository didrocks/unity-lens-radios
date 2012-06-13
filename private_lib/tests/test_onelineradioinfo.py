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

from mock import patch, Mock
import os
import unittest
import urllib

from ..onlineradioinfo import singleton, OnlineRadioInfo, ConnectionError


class OnlineRadioInfoTestsCommon(unittest.TestCase):

    def setUp(self):
        # create the singleton. Don't call the super method for children if they need
        # to create the singleton with other parameters
        self.radioinfo = OnlineRadioInfo()

    def tearDown(self):
        # remove the current singleton
        try:
        # need to use the singleton to find the class as it's decorated
        # and report a getinstance instance otherwise
        # TODO: is there a better way to do that?
            del(singleton.instances[OnlineRadioInfo().__class__])
        except KeyError:
            pass


class OnlineRadioInfoMainTests(OnlineRadioInfoTestsCommon):

    def test_is_singleton(self):
        '''Test that OnlineRadioInfoTests is a singleton'''
        self.assertEqual(self.radioinfo, OnlineRadioInfo())

    def test_get_category(self):
        '''Test that get category is reporting what we need'''
        self.assertEqual(self.radioinfo.get_category_types(), self.radioinfo.VALID_CATEGORY_TYPES)


class OnlineRadioInfoLangTests(OnlineRadioInfoTestsCommon):

    def setUp(self):
        '''Setup a known lang environnement by default'''
        # don't call super().setup() here as we want to create our own object with different parameters
        self.system_lang = os.environ['LANG']
        os.environ['LANG'] = "fr_FR.UTF-8"

    def tearDown(self):
        '''restore system lang'''
        os.environ['LANG'] = self.system_lang
        super().tearDown()

    def test_auto_detect_lang(self):
        '''Test lang detection and linking to the right radio URL'''
        radioinfo = OnlineRadioInfo()
        self.assertEqual(radioinfo.MAIN_URLS['fr'], radioinfo.radio_base_url)

    def test_manual_lang(self):
        '''Test manual lang set and linking to the right radio URL'''
        radioinfo = OnlineRadioInfo(language='en')
        self.assertEqual(radioinfo.MAIN_URLS['en'], radioinfo.radio_base_url)

    def test_auto_invalid_lang(self):
        '''Ensure that invalid lang in LANG variable fallback to en radio URL'''
        os.environ['LANG'] = "D"
        radioinfo = OnlineRadioInfo()
        self.assertEqual(radioinfo.MAIN_URLS['en'], radioinfo.radio_base_url)

    def test_manual_not_support_lang(self):
        '''Test manual lang provided that isn't supported fallback to en radio URL'''
        radioinfo = OnlineRadioInfo(language='klingon')
        self.assertEqual(radioinfo.MAIN_URLS['en'], radioinfo.radio_base_url)


class OnlineRadioInfoJsonLineTests(OnlineRadioInfoTestsCommon):

    def _setup_mock_urllib(self, urllibmock):
        '''Setup the urllib mock object with exceptions and data'''
        urllibmock.error.HTTPError = urllib.error.HTTPError
        urllibmock.error.URLError = urllib.error.URLError
        urllibmock.parse.urlencode = urllib.parse.urlencode
        urllibmock.request.urlopen().headers.get_content_charset.return_value = "UTF-8"
        urllibmock.request.urlopen().readall().decode.return_value = '{"foo": [{"bar":"baz"}]}'

    @patch('private_lib.onlineradioinfo.urllib')
    def test_getting_results(self, urllibmock):
        '''Test getting regular results back in a json format'''
        self._setup_mock_urllib(urllibmock)
        result = self.radioinfo._get_json_result_for_parameters('foo/bar', baz='france', bill='de')

        self.assertEqual(result, {'foo': [{'bar': 'baz'}]})
        urllibmock.request.Request.assert_called_once_with(self.radioinfo.radio_base_url + "/foo/bar?bill=de&baz=france")
        self.assertTrue(urllibmock.request.urlopen.called)
        urllibmock.request.urlopen().headers.get_content_charset.assert_called_once_with()
        urllibmock.request.urlopen().readall().decode.assert_called_once_with("UTF-8")

    @patch('private_lib.onlineradioinfo.urllib')
    def test_raising_http_error(self, urllibmock):
        '''Raising an exception while can't connect to the Internet or getting content'''
        self._setup_mock_urllib(urllibmock)
        urllibmock.request.urlopen = Mock(side_effect=urllib.error.HTTPError(Mock(), Mock(), Mock(), Mock(), Mock()))

        urllibmock.request.urlopen = Mock(side_effect=urllib.error.URLError(Mock(), Mock()))
        self.assertRaises(ConnectionError, self.radioinfo._get_json_result_for_parameters, 'foo/bar', baz='france', bill='de')

    @patch('private_lib.onlineradioinfo.urllib')
    def test_invalid_json_error(self, urllibmock):
        '''Raising an exception when receives invalid json content'''
        self._setup_mock_urllib(urllibmock)
        urllibmock.request.urlopen().readall().decode.return_value = '{"foo": [{"bar":"baz"}] extraword}'
        self.assertRaises(ConnectionError, self.radioinfo._get_json_result_for_parameters, 'foo/bar', baz='france', bill='de')
