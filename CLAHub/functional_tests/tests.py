from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth import get_user_model

import time
import os

from CLAHub import base_settings

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

    def test_login(self):
        # hash the passwords!
        User = get_user_model()
        for user in User.objects.all():
            user.set_password(user.password)
            user.save()

        # Test login and redirect
        self.selenium.get((self.live_server_url + '/accounts/login/'))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys('user1')
        self.wait()
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys('password')
        self.wait()
        self.selenium.find_element_by_id('login-btn').click()
        self.wait()
        self.assertEqual(self.selenium.current_url, self.live_server_url + '/CE/')
        self.assertIn('user1', self.selenium.find_element_by_id('login-status').get_attribute('innerHTML'))
