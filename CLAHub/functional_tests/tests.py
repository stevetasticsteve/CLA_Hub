from selenium import webdriver
from selenium.webdriver.support.ui import Select
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
            'text_title1': 'New text 1',
            'text_title2': 'New text 2',
            'speaker': 'Steve',  # todo change to an integer to test the auto link. Add a person fixture
            'phonetic_text': 'foᵘnɛtɪks',
            'orthographic_text': 'phonetics',
            'discourse_type': '1',
            'phonetic_standard': '2',
            'Q1': 'Q1',
            'A1': 'A1',
            'Q2': 'Q2',
            'A2': 'A2',
        }
        self.edited_data = self.test_data.copy()
        for key in self.edited_data:
            self.edited_data[key] = 'Changed ' + self.edited_data[key]
        self.test_pic = os.path.join(base_settings.BASE_DIR, 'CLAHub', 'assets', 'test_data', 'test_pic1.jpg')
        self.test_audio1 = os.path.join(base_settings.BASE_DIR, 'CLAHub', 'assets', 'test_data', 'test_audio1.mp3')
        self.test_audio2 = os.path.join(base_settings.BASE_DIR, 'CLAHub', 'assets', 'test_data', 'test_audio2.mp3')

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

    def test_add_and_edit_CE(self):
        try:
            self.login()
            self.selenium.get((self.live_server_url + '/CE/new'))
            # check we've not been redirected to login
            self.assertNotEqual(self.selenium.current_url, self.live_server_url + '/accounts/login/?next=/CE/new')

            # Fill in CE form
            self.selenium.find_element_by_id("id_title").send_keys(self.test_data['title'])
            self.selenium.find_element_by_id("id_description_plain_text").send_keys(self.test_data['description'])
            self.selenium.find_element_by_id("id_differences").send_keys(self.test_data['differences'])
            self.selenium.find_element_by_id("id_interpretation").send_keys(self.test_data['interpretation'])
            self.selenium.find_element_by_id("id_picture").send_keys(self.test_pic)
            # Fill in visits form
            self.selenium.find_element_by_id('add-visit-button').click()
            self.selenium.find_element_by_id("id_visit-0-team_present").send_keys(self.test_data['team'])
            self.selenium.find_element_by_id("id_visit-0-nationals_present").send_keys(self.test_data['nationals'])
            # todo get the date picker working
            self.selenium.find_element_by_id('add-visit-button').click()
            self.selenium.find_element_by_id("id_visit-1-team_present").send_keys(self.test_data['team'])
            self.selenium.find_element_by_id("id_visit-1-nationals_present").send_keys(self.test_data['nationals'])
            # Fill in texts form
            self.selenium.find_element_by_id('add-text-button').click()
            self.selenium.find_element_by_id("id_text-0-text_title").send_keys(self.test_data['text_title1'])
            self.selenium.find_element_by_id("id_text-0-speaker_plain_text").send_keys(self.test_data['speaker'])
            self.selenium.find_element_by_id("id_text-0-phonetic_text").send_keys(self.test_data['phonetic_text'])
            self.selenium.find_element_by_id("id_text-0-orthographic_text").send_keys(
                self.test_data['orthographic_text'])
            Select(self.selenium.find_element_by_id("id_text-0-discourse_type")).select_by_visible_text('Narrative')
            Select(self.selenium.find_element_by_id("id_text-0-phonetic_standard")). \
                select_by_visible_text('Double checked by author')
            self.selenium.find_element_by_id("id_text-0-audio").send_keys(self.test_audio1)

            self.selenium.find_element_by_id('add-text-button').click()
            self.selenium.find_element_by_id("id_text-1-text_title").send_keys(self.test_data['text_title2'])
            self.selenium.find_element_by_id("id_text-1-speaker_plain_text").send_keys(self.test_data['speaker'])
            self.selenium.find_element_by_id("id_text-1-phonetic_text").send_keys(self.test_data['phonetic_text'])
            self.selenium.find_element_by_id("id_text-1-orthographic_text").send_keys(
                self.test_data['orthographic_text'])
            Select(self.selenium.find_element_by_id("id_text-1-discourse_type")).select_by_visible_text('Narrative')
            Select(self.selenium.find_element_by_id("id_text-1-phonetic_standard")). \
                select_by_visible_text('Double checked by author')
            self.selenium.find_element_by_id("id_text-1-audio").send_keys(self.test_audio2)
            # Fill in Q form
            self.selenium.find_element_by_id('add-question-button').click()
            self.selenium.find_element_by_id("id_question-0-question").send_keys(self.test_data['Q1'])
            self.selenium.find_element_by_id("id_question-0-answer").send_keys(self.test_data['A1'])
            self.selenium.find_element_by_id('add-question-button').click()
            self.selenium.find_element_by_id("id_question-1-question").send_keys(self.test_data['Q2'])
            self.selenium.find_element_by_id("id_question-1-answer").send_keys(self.test_data['A2'])
            # submit
            self.selenium.find_element_by_id('submit-btn').click()
            self.wait()

            # test redirect
            self.assertEqual(self.selenium.current_url, self.live_server_url + '/CE/%d' % self.new_ce_pk)
            # test .db contents
            ce = models.CultureEvent.objects.get(pk=self.new_ce_pk)
            self.assertEqual(ce.title, self.test_data['title'], 'CE form not working on new page - title')
            self.assertEqual(ce.description_plain_text, self.test_data['description'],
                             'CE form not working on new page - desc')
            self.assertEqual(ce.differences, self.test_data['differences'],
                             'CE form not working on new page - differences')
            self.assertEqual(ce.interpretation, self.test_data['interpretation'],
                             'CE form not working on new page - interpretation')
            visits = models.Visit.objects.filter(ce=ce)
            self.assertEqual(len(visits), 2, 'Visits form not working on new page - too few visits')
            self.assertEqual(visits[0].team_present, self.test_data['team'],
                             'Visits form not working on new page - incorrect .db entry')
            pictures = models.Picture.objects.filter(ce=ce)
            self.assertEqual(len(pictures), 1, 'CE picture not in .db')
            self.assertIn(os.path.basename(self.test_pic), str(pictures[0].picture))
            texts = models.Text.objects.filter(ce=ce)
            self.assertEqual(len(texts), 2, 'Too few texts in .db')
            self.assertEqual(texts[0].text_title, self.test_data['text_title1'],
                             ' Texts form not working - incorrect .db entry text_title')
            self.assertEqual(texts[1].text_title, self.test_data['text_title2'],
                             ' Texts form not working - incorrect .db entry text_title')
            self.assertEqual(texts[0].speaker, self.test_data['speaker'],
                             'Texts form not working - incorrect .db entry speaker')
            self.assertEqual(texts[0].phonetic_text, self.test_data['phonetic_text'],
                             'Texts form not working - incorrect .db entry phonetic_text')
            self.assertEqual(texts[0].orthographic_text, self.test_data['orthographic_text'],
                             'Texts form not working - incorrect .db entry orthographic_text')
            self.assertEqual(texts[0].phonetic_standard, self.test_data['phonetic_standard'],
                             'Texts form not working - incorrect .db entry phonetic_standard')
            self.assertEqual(texts[0].discourse_type, self.test_data['discourse_type'],
                             'Texts form not working - incorrect .db entry discourse_type')
            self.assertIn(os.path.basename(self.test_audio1), str(texts[0].audio),
                          'Texts form not working - incorrect .db entry audio')
            self.assertIn(os.path.basename(self.test_audio2), str(texts[1].audio),
                          'Texts form not working - incorrect .db entry audio')
            questions = models.Question.objects.filter(ce=ce)
            self.assertEqual(len(questions), 2, 'Questions form not working - too few questions')
            self.assertEqual(questions[0].question, self.test_data['Q1'],
                             'Questions form not working - incorrect .db entry: Q')
            self.assertEqual(questions[0].answer, self.test_data['A1'],
                             'Questions form not working - incorrect .db entry: A')
            # test upload folder contents
            upload_path = os.path.join(base_settings.BASE_DIR, 'uploads', 'CultureEventFiles', str(self.new_ce_pk))
            self.assertTrue(os.path.exists(os.path.join(upload_path, 'images', os.path.basename(self.test_pic))),
                            'Picture not found in upload folder')
            self.assertTrue(os.path.exists(os.path.join(upload_path, 'audio', os.path.basename(self.test_audio2))),
                            'Audio not found in upload folder')
            self.assertTrue(os.path.exists(os.path.join(upload_path, 'audio', os.path.basename(self.test_audio1))),
                            'Audio not found in upload folder')
            # test page contents
            self.assertEqual(ce.title, self.selenium.find_element_by_id('title').get_attribute('innerHTML'),
                             'HTML no working right - title')
            self.assertTrue(self.selenium.find_element_by_id('CE_pictures').is_displayed()
                            , 'HTMl not working right - CE picture')

            # Test edit page
            self.selenium.get((self.live_server_url + '/CE/%d/edit' % self.new_ce_pk))
            self.wait()
            # 1. Test initial contents
            self.assertEqual(self.selenium.find_element_by_id("id_title").get_attribute('value'),
                             self.test_data['title'], 'Edit page displaying wrong info: CE title')
            self.assertEqual(self.selenium.find_element_by_id("id_description_plain_text").get_attribute('value'),
                             self.test_data['description'], 'Edit page displaying wrong info: CE description')
            self.assertEqual(self.selenium.find_element_by_id("id_differences").get_attribute('value'),
                             self.test_data['differences'], 'Edit page displaying wrong info: CE differences')
            self.assertEqual(self.selenium.find_element_by_id("id_interpretation").get_attribute('value'),
                             self.test_data['interpretation'], 'Edit page displaying wrong info: CE interpretation')
            # todo examine the picture
            self.assertEqual(self.selenium.find_element_by_id("id_visit-0-team_present").get_attribute('value'),
                             self.test_data['team'], 'Edit page displaying wrong info: Visits, team')
            self.assertEqual(self.selenium.find_element_by_id("id_visit-0-nationals_present").get_attribute('value'),
                             self.test_data['nationals'], 'Edit page displaying wrong info: Visits, nationals')
            self.assertEqual(self.selenium.find_element_by_id("id_visit-1-team_present").get_attribute('value'),
                             self.test_data['team'], 'Edit page displaying wrong info: Visits, team')
            self.assertEqual(self.selenium.find_element_by_id("id_visit-1-nationals_present").get_attribute('value'),
                             self.test_data['nationals'], 'Edit page displaying wrong info: Visits, nationals')

            self.assertEqual(self.selenium.find_element_by_id("id_text-0-text_title").get_attribute('value'),
                             self.test_data['text_title1'], 'Edit page displaying wrong info: text title')
            self.assertEqual(self.selenium.find_element_by_id("id_text-1-text_title").get_attribute('value'),
                             self.test_data['text_title2'], 'Edit page displaying wrong info: text title')
            self.assertEqual(self.selenium.find_element_by_id("id_text-0-phonetic_text").get_attribute('value'),
                             self.test_data['phonetic_text'], 'Edit page displaying wrong info: phonetic text')
            self.assertEqual(self.selenium.find_element_by_id("id_text-0-orthographic_text").get_attribute('value'),
                             self.test_data['orthographic_text'], 'Edit page displaying wrong info: orthographic txt')
            self.assertEqual(self.selenium.find_element_by_id("id_text-0-speaker_plain_text").get_attribute('value'),
                             self.test_data['speaker'], 'Edit page displaying wrong info: speaker')
            self.assertEqual(self.selenium.find_element_by_id("id_text-0-discourse_type").get_attribute('value'),
                             self.test_data['discourse_type'], 'Edit page displaying wrong info: discourse type')
            self.assertEqual(self.selenium.find_element_by_id("id_text-0-phonetic_standard").get_attribute('value'),
                             self.test_data['phonetic_standard'], 'Edit page displaying wrong info: phonetic standard')
            # self.assertEqual(self.selenium.find_element_by_id("id_text-0-audio").get_attribute('value'),
            #                  os.path.join('uploads', 'CultureEventFiles', str(self.new_ce_pk), 'audio',
            #                               os.path.basename(self.test_audio1)), 'Edit page displaying wrong info: audio')
            # todo Find a way to identify audio currently: xxx.mp3

            self.assertEqual(self.selenium.find_element_by_id("id_question-0-question").get_attribute('value'),
                             self.test_data['Q1'], 'Edit page displaying wrong info: question')
            self.assertEqual(self.selenium.find_element_by_id("id_question-0-answer").get_attribute('value'),
                             self.test_data['A1'], 'Edit page displaying wrong info: question')
            self.assertEqual(self.selenium.find_element_by_id("id_question-1-question").get_attribute('value'),
                             self.test_data['Q2'], 'Edit page displaying wrong info: question')
            self.assertEqual(self.selenium.find_element_by_id("id_question-1-answer").get_attribute('value'),
                             self.test_data['A2'], 'Edit page displaying wrong info: question')

            # 2 Edit contents
            # Edit CE form
            self.selenium.find_element_by_id("id_title").clear()
            self.selenium.find_element_by_id("id_title").send_keys(self.edited_data['title'])
            self.selenium.find_element_by_id("id_description_plain_text").clear()
            self.selenium.find_element_by_id("id_description_plain_text").send_keys(self.edited_data['description'])
            self.selenium.find_element_by_id("id_differences").clear()
            self.selenium.find_element_by_id("id_differences").send_keys(self.edited_data['differences'])
            self.selenium.find_element_by_id("id_interpretation").clear()
            self.selenium.find_element_by_id("id_interpretation").send_keys(self.edited_data['interpretation'])
            # todo picture
            # Edit visits form - changed half the fields, leave half the same
            self.selenium.find_element_by_id("id_visit-0-team_present").clear()
            self.selenium.find_element_by_id("id_visit-0-team_present").send_keys(self.edited_data['team'])
            self.selenium.find_element_by_id("id_visit-1-nationals_present").clear()
            self.selenium.find_element_by_id("id_visit-1-nationals_present").send_keys(self.edited_data['nationals'])
            # Edit questions form - change half the fields, leave half the same
            self.selenium.find_element_by_id("id_question-0-question").clear()
            self.selenium.find_element_by_id("id_question-0-question").send_keys(self.edited_data['Q1'])
            self.selenium.find_element_by_id("id_question-1-answer").clear()
            self.selenium.find_element_by_id("id_question-1-answer").send_keys(self.edited_data['A2'])
            # Edit text form - change title of one of the texts, change one of the audio files
            self.selenium.find_element_by_id("id_text-0-text_title").clear()
            self.selenium.find_element_by_id("id_text-0-text_title").send_keys(self.edited_data['text_title1'])
            self.selenium.find_element_by_id("id_text-1-audio").clear()
            self.selenium.find_element_by_id("id_text-1-audio").send_keys(self.test_audio1)
            # Submit
            self.selenium.find_element_by_id('submit-btn').click()
            self.wait()

            # test redirect
            self.assertEqual(self.selenium.current_url, self.live_server_url + '/CE/%d' % self.new_ce_pk)
            # test edited .db contents
            ce = models.CultureEvent.objects.get(pk=self.new_ce_pk)
            self.assertEqual(ce.title, self.edited_data['title'], 'CE form not working on edit page - title')
            self.assertNotEqual(ce.title, self.test_data['title'], 'CE form not working on edit page - title')
            self.assertEqual(ce.description_plain_text, self.edited_data['description'],
                             'CE form not working on edit page - desc')
            self.assertEqual(ce.differences, self.edited_data['differences'],
                             'CE form not working on edit page - differences')
            self.assertEqual(ce.interpretation, self.edited_data['interpretation'],
                             'CE form not working on edit page - interpretation')
            # test visits
            visits = models.Visit.objects.filter(ce=ce)
            self.assertEqual(len(visits), 2, 'Visits form not working on edit page - too few visits')
            self.assertEqual(visits[0].team_present, self.edited_data['team'],
                             'Visits form not working on edit page - incorrect .db entry')
            self.assertEqual(visits[1].team_present, self.test_data['team'],
                             'Visits form not working on edit page - incorrect .db entry')
            self.assertEqual(visits[0].nationals_present, self.test_data['nationals'],
                             'Visits form not working on edit page - incorrect .db entry')
            self.assertEqual(visits[1].nationals_present, self.edited_data['nationals'],
                             'Visits form not working on edit page - incorrect .db entry')
            # test questions
            questions = models.Question.objects.filter(ce=ce)
            self.assertEqual(len(questions), 2, 'Questions form not working - too few questions')
            self.assertEqual(questions[0].question, self.edited_data['Q1'],
                             'Questions form not working on edit page - incorrect .db entry: Q')
            self.assertEqual(questions[1].question, self.test_data['Q2'],
                             'Questions form not working on edit page - incorrect .db entry: Q')
            self.assertEqual(questions[0].answer, self.test_data['A1'],
                             'Questions form not working on edit page - incorrect .db entry: A')
            self.assertEqual(questions[1].answer, self.edited_data['A2'],
                             'Questions form not working on edit page - incorrect .db entry: A')
            # test texts
            texts = models.Text.objects.filter(ce=ce)
            self.assertEqual(len(texts), 2, 'Too few texts in .db')
            self.assertEqual(texts[0].text_title, self.edited_data['text_title1'],
                             ' Texts form on edit page not working - incorrect .db entry text_title')
            self.assertIn(os.path.basename(self.test_audio1.rstrip('.mp3')), str(texts[1].audio),
                          'Texts form not on edit page working - incorrect .db entry audio')
            # todo a duplicate mp3 file is created here.


        finally:
            self.cleanup_test_files(self.new_ce_pk)
