"""
The MIT License (MIT)

Copyright (c) 2014 - 2016 Mohab Usama
"""

import logging


VERSION = '0.7'


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.handlers = [logging.StreamHandler()]
