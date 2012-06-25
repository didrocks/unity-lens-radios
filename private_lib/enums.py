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

from gettext import gettext as _
import logging


class CATEGORIES():
    (RECOMMENDED, TOP, LOCAL, SEARCH_RADIO) = range(4)

LEVELS = (logging.ERROR,
        logging.WARNING,
        logging.INFO,
        logging.DEBUG,
        )

DBUS_NAME = 'com.canonical.Unity.Lens.Radios'
DBUS_PATH = '/com/canonical/unity/lens/radios'

LENS_NAME = 'radios'

SEARCH_HINT = _("Search online radios")
