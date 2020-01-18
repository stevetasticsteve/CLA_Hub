#!/bin/bash

# updates CLAHub
cd /media/NAS/CLAHub
git fetch --all &&
git reset --hard origin/master &&
source venv/bin/activate &&
python manage.py makemigrations &&
python manage.py migrate &&
sudo systemctl restart CLAHub
