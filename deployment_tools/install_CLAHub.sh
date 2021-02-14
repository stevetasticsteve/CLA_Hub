#!/bin/bash

# This script installs Docker on a Linux system and then runs CLAHub as a container.
# It sets up a Database with a single user: admin password: CLAHub

curl -fsSL https://get.docker.com -o get-docker.sh
if ! sudo sh get-docker.sh; then
  echo "Docker installation failed, try to do it manually." && exit 1
fi
if [[ $(uname -m) == x86_64 ]]; then
  sudo docker run -d --restart unless-stopped --name clahub -p 8000:8000 -v clahub:/code/data stevetasticsteve/clahub:latest
elif [[ $(uname -m) == arm32v7 ]]; then
  sudo docker run -d --restart unless-stopped --name clahub -p 8000:8000 -v clahub:/code/data stevetasticsteve/clahub:arm
else
  echo "Container not available for this architecture" && exit 1
fi
sudo docker container exec clahub python manage.py migrate
export DJANGO_SUPERUSER_PASSWORD="CLAHub"
export DJANGO_SUPERUSER_EMAIL="email@email.com"
export DJANGO_SUPERUSER_USERNAME="admin"
sudo docker container exec clahub python manage.py createsuperuser --noinput
echo
echo "---"
echo "CLAHub was installed. Access it in your browser: <localhost:8000> (on the server itself)."
echo " or <server ip address>:8000 on other computers in your local network."
echo "Login as admin, password=CLAHub and add users from the admin portal."