#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import logging

logging.basicConfig(level=logging.DEBUG)

PROJECT_PATH = os.path.dirname(os.path.abspath(__file__))
CACHE_PATH = os.path.join(PROJECT_PATH,'.cache')
CONFIG_PATH = os.path.join(PROJECT_PATH,'.config')

CACHE_KEEPTIME = 20*60 #秒



