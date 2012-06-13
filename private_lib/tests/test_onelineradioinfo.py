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

import os
import unittest

from ..onlineradioinfo import singleton, OnlineRadioInfo


class OnlineRadioInfoTests(unittest.TestCase):

    def tearDown(self):
        # remove the current singleton
        try:
        # need to use the singleton to find the class as it's decorated
        # and report a getinstance instance otherwise
        # TODO: is there a better way to do that?
            del(singleton.instances[OnlineRadioInfo().__class__])
        except KeyError:
            pass

    def test_is_singleton(self):
        '''Test that OnlineRadioInfoTests is a singleton'''
        radioinfo = OnlineRadioInfo()
        self.assertEqual(radioinfo, OnlineRadioInfo())


class OnelineRadioInfoLangTests(OnlineRadioInfoTests):

    def setUp(self):
        '''Setup a known lang environnement by default'''
        #super.setUp()
        self.system_lang = os.environ['LANG']
        os.environ['LANG'] = "fr_FR.UTF-8"

    def tearDown(self):
        '''restore system lang'''
        os.environ['LANG'] = self.system_lang
        super().tearDown()

    def test_auto_detect_lang(self):
        '''Test lang detection and linking to the right radio URL'''
        radioinfo = OnlineRadioInfo()
        self.assertEqual('fr', radioinfo._language)
        self.assertEqual(radioinfo.MAIN_URLS['fr'], radioinfo.radio_base_url)

    def test_manual_lang(self):
        '''Test manual lang set and linking to the right radio URL'''
        radioinfo = OnlineRadioInfo(language='fr')
        self.assertEqual('fr', radioinfo._language)
        self.assertEqual(radioinfo.MAIN_URLS['fr'], radioinfo.radio_base_url)

    def test_auto_invalid_lang(self):
        '''Ensure that invalid lang in LANG variable fallback to en radio URL'''
        os.environ['LANG'] = "D"
        radioinfo = OnlineRadioInfo()
        self.assertEqual('en', radioinfo._language)
        self.assertEqual(radioinfo.MAIN_URLS['en'], radioinfo.radio_base_url)

    def test_manual_not_support_lang(self):
        '''Test manual lang provided that isn't supported fallback to en radio URL'''
        radioinfo = OnlineRadioInfo(language='klingon')
        self.assertEqual('klingon', radioinfo._language)
        self.assertEqual(radioinfo.MAIN_URLS['en'], radioinfo.radio_base_url)
