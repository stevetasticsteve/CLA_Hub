from ..base_settings import *
import os

DEBUG = False
ALLOWED_HOSTS = [os.environ['ALLOWED_HOSTS']]
SECRET_KEY = os.environ['SECRET_KEY']