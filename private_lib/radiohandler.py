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
import logging

from .enums import CATEGORIES
from .onlineradioinfo import OnlineRadioInfo
from .radio import transform_decade_str_in_int
from .tools import singleton

_ = gettext.gettext
_log = logging.getLogger(__name__)


@singleton
class RadioHandler(object):
    '''Class handling radios requests and populating model by category and filters'''

    def __init__(self):
        self._last_search = None
        # all radios from previous search, before filtering
        self._last_all_radios_dict = {}

    def get_unity_radio_categories(self, categories):
        '''Build and return new radio categories for unity'''
        _log.debug("Got unity categories")
        unity_categories = []
        for category in categories:
            unity_categories.append(Unity.Category.new(category['name'], category['icon'],
                                    Unity.CategoryRenderer.HORIZONTAL_TILE))
        return unity_categories

    def get_unity_radio_filters(self):
        '''Build and return new radio filters for unity'''
        _log.debug("Got unity filter")
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
            filt.add_option(country, country, None)
        unity_filters.append(filt)
        return unity_filters

    def get_model_data_from_content_search(self, search_terms, scope):
        '''Search current content, eventually filtered

        returns a tuple with the radio itself and an updated model data ready to be appended (iterator)'''

        _log.debug("Searching for: {0}".format(search_terms))
        radios_dict = self._last_all_radios_dict
        # first, the search itself
        if self._last_search is None or search_terms != self._last_search:
            if search_terms == "":
                radios_dict = OnlineRadioInfo().get_most_wanted_stations()
                # change the generator to a list for copying them back in cache
                for category in radios_dict:
                    radios_dict[category] = list(radios_dict[category])
            else:
                radios_dict = {}
                radios_dict["search"] = OnlineRadioInfo().get_stations_by_searchstring(search_terms)

            # save the state, without filters (all radios)
            self._last_all_radios_dict = radios_dict
            self._last_search = search_terms

        filters = self._return_active_filters(scope)
        validate_function = lambda radio, absorber: radio
        if filters:
            validate_function = self._filter_radios
        for category in radios_dict:
            if category == "search":
                cat = CATEGORIES.SEARCH_RADIO
            elif category == "recommended":
                cat = CATEGORIES.RECOMMENDED
            elif category == "top":
                cat = CATEGORIES.TOP
            elif category == "local":
                cat = CATEGORIES.LOCAL
            for valid_radio in validate_function(radios_dict[category], filters):
                yield (valid_radio, (str(valid_radio.id), valid_radio.picture_url, cat, "text/html", valid_radio.name, valid_radio.current_track, ""))

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
            for option in scope.get_filter(category).options:
                if option.props.active:
                    if category not in filters:
                        filters[category] = set()
                    filters[category].add(option.props.id)
        _log.debug("Returning active filters: {0}".format(filters))
        return filters

    def _filter_radios(self, radios, filters):
        '''Filter a radio set and return matching radios'''
        # in a list to keep the order as the radio came from the request
        return [radio for radio in radios if self._is_radio_fulfill_filters(radio, filters)]

    def _is_radio_fulfill_filters(self, radio, filters):
        '''Return True if the radio should be part of the filtering result'''
        valid = True
        for category in filters:
            if category == "decade":
                # initialize with false by default
                if radio.decades:
                    valid = False
                for decade in radio.decades:
                    radio_decade = transform_decade_str_in_int(decade)
                    if radio_decade >= filters['decade'][0] and radio_decade <= filters['decade'][1]:
                        valid = True
                        break
            elif category == "genre":
                for genre in radio.genres:
                    if genre not in filters["genre"]:
                        valid = False
                        break
            elif category == "country":
                if radio.country not in filters["country"]:
                    valid = False
            if not valid:
                break  # no need to check the other filters if not valid
        return valid
