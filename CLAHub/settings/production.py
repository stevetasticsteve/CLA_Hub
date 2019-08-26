from .development import *
import os

ALLOWED_HOSTS = os.environ['ALLOWED_HOSTS']
SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = False