from ..base_settings import *
from dotenv import load_dotenv
import os

load_dotenv()
DEBUG = False
ALLOWED_HOSTS = [os.environ['ALLOWED_HOSTS']]
SECRET_KEY = os.environ['SECRET_KEY']