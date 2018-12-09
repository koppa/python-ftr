# -*- coding: utf-8 -*-
"""
Copyright 2015 Olivier Cortès <oc@1flow.io>.

This file is part of the python-ftr project.

python-ftr is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of
the License, or (at your option) any later version.

python-ftr is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public
License along with python-ftr. If not, see http://www.gnu.org/licenses/


"""

import logging

logging.getLogger('requests').setLevel(logging.ERROR)

from .config import (  # NOQA
    ftr_get_config as get_config,
    SiteConfig,
    SiteConfigException,
    SiteConfigNotFound,
    InvalidSiteConfig,
    NoTestUrlException,
)

from .extractor import (  # NOQA
    ContentExtractor
)

from .process import (  # NOQA
    ftr_process as process,
)
