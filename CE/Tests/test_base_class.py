import os

from django.contrib.auth.models import User
from django.test import TestCase

from CE import models
from CLAHub import base_settings


class CETestBaseClass(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        credentials = User(username='Tester')
        credentials.set_password('secure_password')
        credentials.save()
        credentials2 = User(username='Tester2')
        credentials2.set_password('secure_password2')
        credentials2.save()

    def setUp(self):
        # the prexisiting model objects variable is used to exclude example data
        self.prexisiting_model_objects = {
            'CE': len(models.CultureEvent.objects.all()),
            'Text': len(models.Text.objects.all()),
            'Visit': len(models.Visit.objects.all()),
            'Question': len(models.Question.objects.all()),
        }
        self.test_data = {
            'username': 'Tester',
            'title': 'Test CE1',
            'description_plain_text': 'A culture event happened',
            'differences': 'Last time it was different',
            'interpretation': 'It probably has meaning',
            'nationals_present': 'Initial data',
            'team_present': 'Steve',
            'date': '2019-02-20',
            'phonetic_text': 'foᵘnɛtɪks',
            'orthographic_text': 'orthographic',
            'tags': 'taggie',
            'question': 'Does this test work?',
            'answer': 'Yes, it does!'}

        self.client.login(username='Tester', password='secure_password')
        ce = models.CultureEvent(title=self.test_data['title'],
                                 description_plain_text=self.test_data['description_plain_text'],
                                 differences=self.test_data['differences'],
                                 interpretation=self.test_data['interpretation'], )
        ce.save()
        ce2 = models.CultureEvent(title='TestCE2')
        ce2.save()
        ce.tags.add(self.test_data['tags'])
        visit = models.Visit(nationals_present=self.test_data['nationals_present'],
                             team_present=self.test_data['team_present'],
                             date=self.test_data['date'],
                             ce=ce)
        visit.save()
        text = models.Text(ce=ce,
                           phonetic_text=self.test_data['phonetic_text'],
                           orthographic_text=self.test_data['orthographic_text'])
        text.save()
        text2 = models.Text(ce=ce,
                            phonetic_text='phonetic_text2',
                            orthographic_text=self.test_data['orthographic_text'])
        text2.save()
        q = models.Question(ce=ce,
                            question=self.test_data['question'],
                            answer=self.test_data['answer'])
        q.save()

        self.test_ce1_pk = str(self.prexisiting_model_objects['CE'] + 1)
        self.test_ce2_pk = str(self.prexisiting_model_objects['CE'] + 2)
        self.test_text1_pk = str(self.prexisiting_model_objects['Text'] + 1)
        self.test_text2_pk = str(self.prexisiting_model_objects['Text'] + 2)
        self.test_visit_pk = str(self.prexisiting_model_objects['Visit'] + 1)
        self.test_question_pk = str(self.prexisiting_model_objects['Question'] + 1)
        self.new_ce_pk = str(self.prexisiting_model_objects['CE'] + 3)
        self.test_ce1_upload_path = os.path.join(base_settings.MEDIA_ROOT, 'CultureEventFiles', str(self.test_ce1_pk))
        self.test_files_path = os.path.join(base_settings.BASE_DIR, 'CLAHub', 'assets', 'test_data')
        self.test_pic1_path = os.path.join(self.test_files_path, 'test_pic1.jpg')
        self.test_audio1_path = os.path.join(self.test_files_path, 'test_audio1.mp3')
        self.test_audio2_path = os.path.join(self.test_files_path, 'test_audio2.mp3')
        self.upload_folder = os.path.join(base_settings.MEDIA_ROOT, 'CultureEventFiles')

        # formset IDs are and CEs are picked up through the view normally, but need to be supplied for tests
        # text-0-ce refers is the CE.pk used as foreign key
        # text-0-id refers to the text.pk
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
                              'text-0-phonetic_text': self.test_data['phonetic_text'],
                              'text-0-orthographic_text': self.test_data['orthographic_text'],
                              'text-0-ce': self.test_ce1_pk,
                              'text-0-id': 1,
                              'text-1-phonetic_text': self.test_data['phonetic_text'],
                              'text-1-orthographic_text': self.test_data['orthographic_text'],
                              'text-1-ce': self.test_ce1_pk,
                              'text-1-id': '2',
                              'visit-0-ce': self.test_ce1_pk,
                              'visit-0-id': 1,
                              'visit-0-team_present': self.test_data['team_present'],
                              'visit-0-nationals_present': 'Posted_data',
                              'visit-0-date': self.test_data['date'],
                              'question-0-ce': self.test_ce1_pk,
                              'question-0-id': 3,
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

    @staticmethod
    def get_number_of_uploaded_images(ce):
        ce_upload_path = os.path.join(base_settings.MEDIA_ROOT, 'CultureEventFiles', str(ce), 'images')
        try:
            return len(os.listdir(ce_upload_path))
        except FileNotFoundError:
            return 0

    @staticmethod
    def cleanup_test_files(ce):
        ce = str(ce)
        test_folder_audio = os.path.join(base_settings.MEDIA_ROOT, 'CultureEventFiles', ce, 'audio')
        test_folder_images = os.path.join(base_settings.MEDIA_ROOT, 'CultureEventFiles', ce, 'images')
        folders = [test_folder_audio, test_folder_images]
        test_data = ['test_audio1.mp3', 'test_audio2.mp3', 'test_pic1.jpg', 'test_pic2.jpg']
        for data in test_data:
            try:
                os.remove(os.path.join(test_folder_audio, data))
            except FileNotFoundError:
                pass
            try:
                os.remove(os.path.join(test_folder_images, data))
            except FileNotFoundError:
                pass
        for folder in folders:
            try:
                os.removedirs(folder)
            except OSError:
                pass
        example_ce_folder = os.path.join(base_settings.MEDIA_ROOT, 'CultureEventFiles', '1', 'audio')
        if os.path.exists(example_ce_folder):
            for f in os.listdir(example_ce_folder):
                if f != 'example_audio1.mp3':
                    os.remove(os.path.join(example_ce_folder, f))


class TestBaseClass(CETestBaseClass):
    def test_setup(self):
        self.assertEqual(models.CultureEvent.objects.get(pk=3).title, self.test_data['title'])
        self.assertEqual(len(models.CultureEvent.objects.all()),
                         self.prexisiting_model_objects['CE'] + 2)
        self.assertEqual(len(models.Text.objects.all()),
                         self.prexisiting_model_objects['Text'] + 2)
        self.assertEqual(len(models.Visit.objects.all()),
                         self.prexisiting_model_objects['Visit'] + 1)
        self.assertEqual(len(models.Question.objects.all()),
                         self.prexisiting_model_objects['Question'] + 1)
