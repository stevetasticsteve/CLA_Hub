# CLA Hub
A Django project to give bush teams a way to collaboratively create and maintain a culture file for learning tribal language and culture.
The software is intended to be run on a Raspberry pi 3 on an internal team network and accessed through a desktop web browser.

Check out http://stevetasticsteve.pythonanywhere.com to see a showcase version.

![Screenshot](https://raw.githubusercontent.com/stevetasticsteve/CLA_Hub/master/CLAHub/assets/example_data/CLAHub_screenshot.png)

## Getting started
Setting up CLAHub on your machine to test it out, or to work on the code can be achieved in the following steps.
See deployment for installing on a server where CLAHub can be accessed by multiple machines on a LAN. 
### Prerequisites
- [Python3](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)
- Python3-venv (Linux)

### Installing
1. Download the CLAHub code by cloning the repository with Git (roughly a 10Mb download):

    Open a Powershell window (Windows), or terminal (Linux) and type:
    **git clone https://github.com/stevetasticsteve/CLA_Hub /path/to/new_folder**
    
    *Replace /path/to/new_folder with where you want the new folder to be!*

2. Create a python virtual environment within the new folder

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
    - open __init__.py in a text editor (like notepad)
    - change __from .production import *__ to __from .development import *__
    - save __init__.py
    
5. Install the Python dependencies (roughly a 12Mb download)

    In Powershell/terminal type: **pip install -r requirements.txt**
    
6. Create (or copy over) the database

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
    stage 3 again to activate the venv. This needs to be done every time you launch** 
    
8. Use CLAHub

    Open a web browser and navigate to localhost:8000
    
    *CLAHub is running on your computer until you close the terminal, or shut down the computer. It is available only 
    from your computer, other computers are unable to access CLAHub in this run mode. If you want other computers to 
    access CLAHub you need to deploy it properly, see Deployment below*
    
    There is a quick and dirty way to enable access on the LAN for other machines. Use the command 
    **python manage.py runserver 0.0.0.0:8000** for stage 7. This isn't the best way to do it, but it will work for a 
    small team if you don't mind leaving your computer on and/or manually starting CLAHub often.
    

## Running the tests
...
  
 ## Deployment
 Automated deployment tools and proper documentation haven't been developed yet, manual installation is necessary.
Currently there's only [this list](https://github.com/stevetasticsteve/CLA_Hub/blob/master/deployment_tools/Deployment%20steps_Linux.txt)
of steps I took in deploying to our Raspberry pi.
If anyone is intersted in installing CLAHub themselves and that list makes no sense to them feel free to contact me and 
I'll make easier installation options a higher priority.

### Deployment requirements
* A server running Linux
  * Apache or Nginx
  * Python 3
  * Python modules [(requirements.txt)](https://github.com/stevetasticsteve/CLA_Hub/blob/master/requirements.txt)
  * ffmpeg (for the podcast feed)
  
 ## Built with
 [Django](https://www.djangoproject.com/) - the web framework used
 
 ## Contributing
 ...
 
 ## License
 This project is licensed under [GPL 3.0 ](https://github.com/stevetasticsteve/CLA_Hub/blob/master/LICENSE).

## Core features
- Create web pages to document culture events (CEs)
    - Allow cross linking to other CEs
    - Provides a template for documenting CEs
    - Fields for phonetic and orthographic text
    - Label phonetic text with different levels of accuracy enabling exports of thoroughly checked
      phonetic data to other tools
    - Able to tag phonetic/orthographic texts as valid for discourse analysis
    - Able to attach/embed audio recordings of vernacular texts
    - Able to attach/embed photos of CEs. Auto compression of pictures for low storage needs.
    - Store CE data in a database format allowing for retrieval and other processing
    -- Be able to tag vernacular text with outline of cultural materials (OCM) tags
    - Unanswered questions regarding individual CE that can be gathered summarised

- CE index page
    - Displays most recently modified CEs
    -- Able to show alphabetical list of CEs

- OCM summaries
    -- Lift tagged vernacular text from CEs and generate summaries of all tags related to that cultural area
    -- Be able to export OCM summaries

- Needs team input tag
    -- Be able to tag something as needing to be discussed among the team, a page will be generated keeping track
      of all these things. During a team meeting the team can work through the page and edit and tick off items.

- Login and authorisation
    - Team members login with unique accounts that track contributions

- Backups
    - Culture file must be easy to back up and retrieve

- Exportable
    -- Tools to export all data in useful formats. Particularly .docx format (missionaries love MS Word)

- Transferable
    - Team members leaving for home assignment need to be able to take a copy home for study


## Possible add-on tools
- Phonetic to orthographic text auto convert
- Listening collection
- Support for mobile devices
- Meeting minutes and action points
- Lexicon
- List of language activities for each CE (TPR, photobook etc.)
- Auto create anki decks.
- Deployment tools to help non techie missionaries set up Raspi web server

## Request features from team mates
- OCM Guide
- Text accent tag
- Texts added to navbar - search and filter texts
- Caption to picture
