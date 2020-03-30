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

        self.new_ce_pk = 3
        self.test_data = {
            'title': 'A test CE',
            'description': 'Some things happened',
            'differences': 'It happened several times',
            'interpretation': 'I think this is a test',
            'team': 'Steve',
            'nationals': 'Ulumo',
        }
        self.test_pic = os.path.join(base_settings.BASE_DIR, 'CLAHub', 'assets', 'test_data', 'test_pic1.jpg')

    @staticmethod
    def cleanup_test_files(ce):
        ce = str(ce)
        test_folder_audio = os.path.join(os.getcwd(), 'uploads/CultureEventFiles/' + ce + '/audio/')
        test_folder_images = os.path.join(os.getcwd(), 'uploads/CultureEventFiles/' + ce + '/images/')
        folders = [test_folder_audio, test_folder_images]
        test_data = ['test_audio1.mp3', 'test_audio2.mp3', 'test_pic1.jpg', 'test_pic2.jpg']
        for data in test_data:
            try:
                os.remove(test_folder_audio + data)
            except FileNotFoundError:
                pass
            try:
                os.remove(test_folder_images + data)
            except FileNotFoundError:
                pass
        for folder in folders:
            try:
                os.removedirs(folder)
            except OSError:
                pass

    def test_login(self):
        # Test login and redirect
        self.login()
        self.assertEqual(self.selenium.current_url, self.live_server_url + '/CE/')
        self.assertIn('user1', self.selenium.find_element_by_id('login-status').get_attribute('innerHTML'))

    def test_add_CE(self):
        try:
            self.login()
            self.selenium.get((self.live_server_url + '/CE/new'))
            # check we've not been redirected to login
            self.assertNotEqual(self.selenium.current_url, self.live_server_url + '/accounts/login/?next=/CE/new')
    
            # Fill in CE form
            self.selenium.find_element_by_id("id_title").send_keys(self.test_data['title'])
            self.wait()
            self.selenium.find_element_by_id("id_description_plain_text").send_keys(self.test_data['description'])
            self.wait()
            self.selenium.find_element_by_id("id_differences").send_keys(self.test_data['differences'])
            self.wait()
            self.selenium.find_element_by_id("id_interpretation").send_keys(self.test_data['interpretation'])
            self.wait()
            self.selenium.find_element_by_id("id_picture").send_keys(self.test_pic)
            self.wait()
            # Fill in visits form
            self.selenium.find_element_by_id('add-visit-button').click()
            self.selenium.find_element_by_id("id_visit-0-team_present").send_keys(self.test_data['team'])
            self.selenium.find_element_by_id("id_visit-0-nationals_present").send_keys(self.test_data['nationals'])
            # todo get the date picker working
            self.selenium.find_element_by_id('add-visit-button').click()
            self.selenium.find_element_by_id("id_visit-1-team_present").send_keys(self.test_data['team'])
            self.selenium.find_element_by_id("id_visit-1-nationals_present").send_keys(self.test_data['nationals'])
            # submit
            self.selenium.find_element_by_id('submit-btn').click()
            self.wait()
    
            # test redirect
            self.assertEqual(self.selenium.current_url, self.live_server_url + '/CE/%d' % self.new_ce_pk)
            # test .db contents
            ce = models.CultureEvent.objects.get(pk=self.new_ce_pk)
            self.assertEqual(ce.title, self.test_data['title'], 'CE form not working on new page - title')
            self.assertEqual(ce.description_plain_text, self.test_data['description'], 'CE form not working on new page - desc')
            self.assertEqual(ce.differences, self.test_data['differences'], 'CE form not working on new page - differences')
            self.assertEqual(ce.interpretation, self.test_data['interpretation'],
                             'CE form not working on new page - interpretation')
            visits = models.Visit.objects.filter(ce=ce)
            self.assertEqual(len(visits), 2, 'Visits form not working on new page - too few visits')
            self.assertEqual(visits[0].team_present, self.test_data['team'],
                             'Visits form not working on new page - incorrect .db entry')
            pictures = models.Picture.objects.filter(ce=ce)
            self.assertEqual(len(pictures), 1, 'CE picture not in .db')
            self.assertIn(os.path.basename(self.test_pic), str(pictures[0].picture))
            # test upload folder contents
            upload_path = os.path.join(base_settings.BASE_DIR, 'uploads', 'CultureEventFiles', str(self.new_ce_pk))
            self.assertTrue(os.path.exists(os.path.join(upload_path, 'images', os.path.basename(self.test_pic))),
                            'Picture not found in upload folder')
            # test page contents
            title = self.selenium.find_element_by_id('title').get_attribute('innerHTML')
            self.assertEqual(ce.title, title, 'HTML no working right - title')
            self.assertTrue(self.selenium.find_element_by_id('CE_pictures').is_displayed()
                            , 'HTMl not working right - CE picture')

        finally:
            self.cleanup_test_files(self.new_ce_pk)

