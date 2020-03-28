from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth import get_user_model

import time
import os

from CLAHub import base_settings
from CE import models


class SeleniumTests(StaticLiveServerTestCase):
    fixtures = ['CLAHub/fixtures/functional_tests.json']

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = webdriver.Firefox(executable_path=os.path.join(base_settings.BASE_DIR, 'geckodriver'))
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    @staticmethod
    def wait():
        time.sleep(0.5)

    @staticmethod
    def pause():
        input('test paused, press any key to continue')

    def login(self):
        self.selenium.get((self.live_server_url + '/accounts/login/'))
        self.selenium.find_element_by_name("username").send_keys('user1')
        self.wait()
        self.selenium.find_element_by_name("password").send_keys('password')
        self.wait()
        self.selenium.find_element_by_id('login-btn').click()
        self.wait()

    def setUp(self):
        # hash the passwords!
        User = get_user_model()
        for user in User.objects.all():
            user.set_password(user.password)
            user.save()
        self.user = User.objects.all()[0]

    def test_login(self):
        # Test login and redirect
        self.login()
        self.assertEqual(self.selenium.current_url, self.live_server_url + '/CE/')
        self.assertIn('user1', self.selenium.find_element_by_id('login-status').get_attribute('innerHTML'))

    def test_add_CE(self):
        new_ce_pk = 3
        test_data = {
            'title' : 'A test CE',
            'description': 'Some things happened',
            'team': 'Steve',
            'nationals': 'Ulumo',
        }

        self.login()
        self.selenium.get((self.live_server_url + '/CE/new'))
        # check we've not been redirected to login
        self.assertNotEqual(self.selenium.current_url, self.live_server_url + '/accounts/login/?next=/CE/new')

        # Fill in CE form
        self.selenium.find_element_by_id("id_title").send_keys(test_data['title'])
        self.wait()
        self.selenium.find_element_by_id("id_description_plain_text").send_keys(test_data['description'])
        self.wait()
        # Fill in visits form
        self.selenium.find_element_by_id('add-visit-button').click()
        self.selenium.find_element_by_id("id_visit-0-team_present").send_keys(test_data['team'])
        self.selenium.find_element_by_id("id_visit-0-nationals_present").send_keys(test_data['nationals'])
        # todo get the date picker working
        self.selenium.find_element_by_id('add-visit-button').click()
        self.selenium.find_element_by_id("id_visit-1-team_present").send_keys(test_data['team'])
        self.selenium.find_element_by_id("id_visit-1-nationals_present").send_keys(test_data['nationals'])
        # submit
        self.selenium.find_element_by_id('submit-btn').click()
        self.wait()

        # test redirect
        self.assertEqual(self.selenium.current_url, self.live_server_url + '/CE/%d' % new_ce_pk)
        # test .db contents
        ce = models.CultureEvent.objects.get(pk=new_ce_pk)
        self.assertEqual(ce.title, test_data['title'], 'CE form not working on new page - title')
        self.assertEqual(ce.description_plain_text, test_data['description'], 'CE form not working on new page - desc')
        visits = models.Visit.objects.filter(ce=ce)
        self.assertEqual(len(visits), 2, 'Visits form not working on new page - too few visits')
        self.assertEqual(visits[0].team_present, test_data['team'],
                         'Visits form not working on new page - incorrect .db entry')

