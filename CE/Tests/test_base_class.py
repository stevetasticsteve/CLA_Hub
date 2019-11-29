import os
from django.test import TestCase
from django.contrib.auth.models import User
from CE import models


class CETestBaseClass(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        credentials = User(username='Tester')
        credentials.set_password('secure_password')
        credentials.save()

    def setUp(self):
        self.test_data = {
            'username': 'Tester',
            'title': 'Example CE1',
            'description_plain_text': 'A culture event happened',
            'differences': 'Last time it was different',
            'interpretation': 'It probably has meaning',
            'nationals_present': 'Ulumo',
            'team_present': 'Steve',
            'date': '2019-02-20',
            'phonetic_text': 'foᵘnɛtɪks',
            'orthographic_text': 'orthographic',
            'valid_for_DA': False,
            'tags': 'taggie',
            'question': 'Does this test work?',
            'answer': 'Yes, it does!'}

        self.standard_post = {'text-TOTAL_FORMS': 2,
                              'text-INITIAL_FORMS': 2,
                              'question-TOTAL_FORMS': 1,
                              'question-INITIAL_FORMS': 1,
                              'visit-TOTAL_FORMS': 1,
                              'visit-INITIAL_FORMS': 1,
                              'title': self.test_data['title'],
                              'description_plain_text': self.test_data['description_plain_text'],
                              'tags': self.test_data['tags'],
                              'differences': self.test_data['differences'],
                              'interpretation': self.test_data['interpretation'],
                              'text-0-ce': 1,
                              'text-0-id': 1,
                              'text-0-phonetic_text': self.test_data['phonetic_text'],
                              'text-0-orthographic_text': self.test_data['orthographic_text'],
                              'text-0-valid_for_DA': self.test_data['valid_for_DA'],
                              'text-1-ce': 1,
                              'text-1-id': 2,
                              'text-1-phonetic_text': self.test_data['phonetic_text'],
                              'text-1-orthographic_text': self.test_data['orthographic_text'],
                              'text-1-valid_for_DA': self.test_data['valid_for_DA'],
                              'visit-0-ce': 1,
                              'visit-0-id': 1,
                              'visit-0-team_present': self.test_data['team_present'],
                              'visit-0-nationals_present': self.test_data['nationals_present'],
                              'visit-0-date': self.test_data['date'],
                              'question-0-ce': 1,
                              'question-0-id': 1,
                              'question-0-question': self.test_data['question'],
                              'question-0-answer': self.test_data['answer']
                              }

        self.new_post = {'title': 'Test CE',
                         'description_plain_text': self.test_data['description_plain_text'],
                         'visit-0-date': self.test_data['date'],
                         'visit-0-nationals_present': self.test_data['nationals_present'],
                         'visit-0-team_present': self.test_data['team_present'],
                         'text-TOTAL_FORMS': 0,
                         'text-INITIAL_FORMS': 0,
                         'question-TOTAL_FORMS': 0,
                         'question-INITIAL_FORMS': 0,
                         'visit-TOTAL_FORMS': 1,
                         'visit-INITIAL_FORMS': 0
                         }

        self.client.login(username='Tester', password='secure_password')
        ce = models.CultureEvent(title=self.test_data['title'],
                                 description_plain_text=self.test_data['description_plain_text'],
                                 differences=self.test_data['differences'],
                                 interpretation=self.test_data['interpretation'], )
        ce.save()
        ce2 = models.CultureEvent(title='CE2')
        ce2.save()
        ce.tags.add(self.test_data['tags'])
        visit = models.Visit(nationals_present=self.test_data['nationals_present'],
                             team_present=self.test_data['team_present'],
                             date=self.test_data['date'],
                             ce=ce)
        visit.save()
        text = models.Text(ce=ce,
                           phonetic_text=self.test_data['phonetic_text'],
                           orthographic_text=self.test_data['orthographic_text'],
                           valid_for_DA=self.test_data['valid_for_DA'])
        text.save()
        text = models.Text(ce=ce,
                           phonetic_text='phonetic_text2',
                           orthographic_text=self.test_data['orthographic_text'],
                           valid_for_DA=self.test_data['valid_for_DA'])
        text.save()
        q = models.Question(ce=ce,
                            question=self.test_data['question'],
                            answer=self.test_data['answer'])
        q.save()

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
