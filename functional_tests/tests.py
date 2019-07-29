# from django.test import LiveServerTestCase
import unittest
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys
import time

MAX_WAIT = 5


# Use case 1
class NewCETest(unittest.TestCase):
    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(2)

    def tearDown(self):
        self.browser.quit()


    def test_can_create_new_CE(self):
    # Steve navigates to the homepage
        self.browser.get('http://localhost:8000/CE')
        self.assertIn('Home', self.browser.title, 'Home screen not shown')

        self.fail('finish the test!')


# Steve has just come back from a CE about cutting down a tree and wants to document it.
# He clicks to create a new CE

# The program asks for his login, we don't want just anyone editing things!
# Steve logs in with his credentials and is permitted to go to the edit CE view


# The edit CE view is shown and he starts to input data. He fills out most fields and
# attaches audio and pictures.

# Steve decides to save his work and have lunch.

# Shortly after lunch Steve returns to his CE and transcribes the text he got in phonetic script.
# Steve marks the phonetics as rough and needing team checking.
# Steve goes through the text and adds several OCM tags to the text.

# Steve saves his work

# Steve goes to the OCM summary of a tag he just made to see what other tags are there.

# Steve logs out


# Use case 2

# Rhett logs in

# Rhett adds a CE about stone axes and saves his work. Stone axes were used to Fell trees

# Rhett notices Steve's CE about felling a tree and cross references it in his description.
# Stone axes were used to 'Fell trees' is now a cross reference to the tree felling CE

# Rhett adds some OCM tags

# Rhett saves his work

# Rhett logs out


# Use case 3

# Philip logs in

# Philip looks at the most recently modified CE's. He checks Rhett's first and follows the cross
# reference to Steve's tree felling CE

# He spots a mistake in Steve's phonetic transcription.

# Philip clicks to edit the page, he corrects the mistake and marks it as needing to be talked about amongst the team.

# Philip logs out


# Use case 4

# The team are having a meeting. Gerdine logs in and pulls up the list of things the team need to discuss. They see
# Philip's correction of Steve's phonetics.

# The team decide the correction is good and mark it as approved. It disappears from the list.

# Gerdine logs out


# Use case 5

# The team are near the end of language study and need to produce a culture write-up.

# Steve logs in and clicks to export the OCM summaries as a word document.

# The program creates a .docx and asks Steve where he wants to save it.

# Steve has a quick scan through and checks his most recent OCM tag is there. Seeing it is he's
# satisfied that the others will be there too.

# Steve logs out

