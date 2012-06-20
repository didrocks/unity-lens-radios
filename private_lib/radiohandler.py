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

import gettext
from gi.repository import Unity

from .enums import CATEGORIES
from .onlineradioinfo import OnlineRadioInfo
from .tools import singleton

_ = gettext.gettext


@singleton
class RadioHandler(object):
    '''Class handling radios requests and populating model by category and filters'''

    def __init__(self):
        self._last_search = None
        # all radios from previous search, before filtering
        self._last_all_radios = None

    def get_unity_radio_categories(self, categories):
        '''Build and return new radio categories for unity'''
        unity_categories = []
        for category in categories:
            unity_categories.append(Unity.Category.new(category['name'], category['icon'],
                                    Unity.CategoryRenderer.HORIZONTAL_TILE))
        return unity_categories

    def get_unity_radio_filters(self):
        '''Build and return new radio filters for unity'''
        # decade, genre, country
        unity_filters = []
        filt = Unity.MultiRangeFilter.new("decade", _("Decade"), None, False)
        filt.add_option("0", _("Old"), None)
        filt.add_option("1960", _("60s"), None)
        filt.add_option("1970", _("70s"), None)
        filt.add_option("1980", _("80s"), None)
        filt.add_option("1990", _("90s"), None)
        filt.add_option("2000", _("00s"), None)
        filt.add_option("2010", _("10s"), None)
        unity_filters.append(filt)
        filt = Unity.CheckOptionFilter.new("genre", _("Genre"), None, False)
        for genre in OnlineRadioInfo().get_categories_by_category_type('genre'):
            filt.add_option(genre, genre, None)
        unity_filters.append(filt)
        filt = Unity.CheckOptionFilter.new("country", _("Country"), None, False)
        for country in OnlineRadioInfo().get_categories_by_category_type('country'):
            filt.add_option(genre, genre, None)
        unity_filters.append(filt)
        return unity_filters

    def search_content(self, search_terms, model, scope):
        '''Search currrent content, eventually filtered, returned an updated model'''

        all_radio_results = self._last_all_radios
        # first, the search itself
        if search_terms != self._last_search:
            pass # TODO: magic here for the search and kill the get_initial_content call

        radio_results = all_radio_results
        # filters the list of radios
        filters = self._return_active_filters(scope)
        if filters:
            radio_results = self._filter_radios(radio_results, filters)

        # save the state, without filters (all radios)
        self._last_all_radios = all_radio_results
        self._last_search = search_terms

    def _return_active_filters(self, scope):
        '''Return current active filters for the scope

        Return a dict of category, and then:
               - a tuple of data (start-end) for the multirange selector
               - a set of activated options for the check selector'''
        filters = {}
        # check filters on the current radio list
        decade_filter = scope.get_filter("decade")
        if decade_filter.get_first_active() and decade_filter.get_last_active():
            filters["decade"] = [decade_filter.get_first_active(), decade_filter.get_last_active()]
        for category in ("genre", "country"):
            for option in scope.get_filter[category].options:
                if option.active:
                    if category not in filters:
                        filters.category = set()
                    filters[category].add(option.id)
        return filters

    def get_initial_content(self, model, filters=None):
        '''Get the recommended, top, local stations

        Return the whole model object'''

        # TODO: Merge into the search method

        model.clear()
        radios_dict = OnlineRadioInfo().get_most_wanted_stations()
        for category in radios_dict:
            if filters:
                radios = self._filter_radios(radios_dict[category])
            else:
                # resolve all radios in a list as we want to store them
                radios = list(radios_dict[category])
            self._last_radio_content = radios
            for radio in radios:
                #model.append((uri, icon_hint, cat, "text/html",
                #        title, comment, dnd_uri))
                #model.append(uri, entry.picture, CATEGORY_LOOKUP, mime, name, display, dnd_uri)
                pass

    def _filter_radios(self, radios, filters):
        '''Filter a radio set and return matching radios'''
        # in a list to keep the order as the radio came from the request
        return [radio for radio in radios if self._is_radio_fulfill_filters(radio, filters)]

    def _is_radio_fulfill_filters(self, radio, filters):
        '''Return True if the radio should be part of the filtering result'''
        valid = True
        for category in filters:
            if category == "decade":
                pass # TODO
            elif category == "genre":
                for genre in radio.genres:
                    if genre not in category["genre"]:
                        valid = False
                        break
            elif category == "country":
                if radio.country not in category["country"]:
                    valid = False
                    break
        return valid
