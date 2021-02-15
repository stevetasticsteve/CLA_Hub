![Django CI](https://github.com/stevetasticsteve/CLA_Hub/workflows/Django%20CI/badge.svg)
# CLA Hub
A [webapp](https://en.wikipedia.org/wiki/Web_application) project to give bush teams a way to collaboratively create 
and maintain a culture file for learning tribal language and culture.
The software is intended to be run on a Raspberry pi 3 on an internal team network and accessed through a desktop web 
browser.

Check out http://stevetasticsteve.pythonanywhere.com to see a showcase version.

![Screenshot](https://raw.githubusercontent.com/stevetasticsteve/CLA_Hub/master/CLAHub/assets/example_data/CLAHub_screenshot.png)

## Getting started, Docker install
CLAHub is available as a docker container. An installation script is provided if you want a one command install.
### Linux
```curl https://raw.githubusercontent.com/stevetasticsteve/CLA_Hub/master/deployment_tools/install_CLAHub.sh | bash```
 
**warning** Running the above script is bad practice - it downloads code from the internet and runs it on
your system. Only use it if you trust me :) Or check [the script](https://raw.githubusercontent.com/stevetasticsteve/CLA_Hub/master/deployment_tools/install_CLAHub.sh)
to make sure there's no funny business behind the scenes.

- Installs Docker using docker convenience script
- Downloads CLAHub Docker image (180Mb for x86, 813Mb for arm)
- Runs CLAHub as a container listening on port 8000 (will survive system restarts)
- Database persists in a Docker volume named clahub


### Windows/MacOS
Use [Docker desktop](https://www.docker.com/products/docker-desktop)

## Installing as source code
### Prerequisites
- [Python3](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)
- Python3-venv (Linux)

### Installing
1. Download the CLAHub code by cloning the repository with Git (roughly a 10Mb download):

    Open a [Powershell](https://www.tenforums.com/tutorials/25581-open-windows-powershell-windows-10-a.html) window 
    (Windows), or [terminal](https://www.howtogeek.com/140679/beginner-geek-how-to-start-using-the-linux-terminal/) 
    (Linux) and type:
    
    **git clone https://github.com/stevetasticsteve/CLA_Hub /path/to/new_folder**
    
    *Replace /path/to/new_folder with where you want the new folder to be!*

2. Create a python virtual environment **in** the new folder

    Windows | Linux
    ------- | -----
    Open a Powershell window in the folder, type: | Open a terminal in the folder, type: 
    **python -m venv venv** | **python3 -m venv venv**


3. Activate the virtual environment

    Windows | Linux
    ------- | -----
    In the Powershell window type: | In the terminal i, type: 
    **venv\Scripts\activate.bat** | **source venv/bin/activate**
    
4. Change from production to development settings
    - go to CLAHub/settings folder
    - open \_\__init\_\_.py in a text editor (like notepad)
    - change __from .production import *__ to __from .development import *__
    - save \_\__init\_\_.py
    
5. Install the Python dependencies (roughly a 12Mb download)

    In Powershell/terminal type: **pip install -r requirements.txt**
    
6. Create (or copy over) the database *f*

    ##### Creating a new database
    - In Powershell/terminal type: **python manage.py migrate**
    - Create at least one new user, type: **python manage.py createsuperuser**
     - Follow the prompts to create a user. Repeat as necessary. 
    ##### Importing an existing database
    If a team has already been working with CLAHub a database can be imported. This can be used so individuals have a 
    (non synced) copy of contents of CLAHub to view when not connected to the team's network - or if the server is
    migrating to a new machine.
    - Copy the old CLAHub_database.db into the new folder (the same place as manage.py). *This copies over all users,
    passwords and data that has been entered.*
    - Replace the uploads folder in the new installation (which is mostly empty) with your old uploads folder. *This 
    copies over all uploaded audio and pictures.*
    
7. Launch the server

    In Powershell/terminal type: **python manage.py runserver**
    *You need to leave this terminal open, if you close it the server will close*
    
    **An error will be displayed if the virtual environment isn't enabled. If your terminal doesn't say (venv) then do
    stage 3 again to activate the venv. This needs to be done every time you launch.** 
    
8. Use CLAHub

    Open a web browser and navigate to localhost:8000
    
    *CLAHub is running on your computer until you close the terminal, or shut down the computer. It is available only 
    from your computer, other computers are unable to access CLAHub in this run mode. If you want other computers to 
    access CLAHub you need to deploy it properly, see Deployment below*
    
    There is a quick and dirty way to enable access on the LAN for other machines. Use the command 
    **python manage.py runserver 0.0.0.0:8000** for stage 7. This isn't the best way to do it, but it will work for a 
    small team if you don't mind leaving your computer on and/or manually starting CLAHub often.
    

## Running the tests
python manage.py test CE people
  
 ## Built with
 [Django](https://www.djangoproject.com/) - the web framework used
 
 ## Contributing
 Contributions are very welcome. See [Contributing](CONTRIBUTING.md) for details.
 
 ## License
 This project is licensed under [GPL 3.0 ](https://github.com/stevetasticsteve/CLA_Hub/blob/master/LICENSE.md).
 
