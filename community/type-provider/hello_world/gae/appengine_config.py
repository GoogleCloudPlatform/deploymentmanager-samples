import os
import sys
import logging

from google.appengine.ext import vendor
vendor.add('lib')
sys.path.append(os.path.join(os.path.dirname(__file__), 'lib'))

logging.basicConfig(level=logging.INFO)