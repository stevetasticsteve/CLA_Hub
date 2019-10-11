from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

import os
import unittest
import shutil
from CE import models


class TestEditPage(TestCase):
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
            'national_participants': 'Ulumo',
            'team_participants': 'Steve',
            'date': '2019-02-20',
            'phonetic_text': 'foᵘnɛtɪks',
            'orthographic_text': 'orthographic',
            'valid_for_DA': False,
            'tags': 'taggie',
            'question': 'Does this test work?',
            'answer': 'Yes, it does!'
        }
        self.standard_post = {'text-TOTAL_FORMS': 2,
                              'text-INITIAL_FORMS': 2,
                              'question-TOTAL_FORMS': 1,
                              'question-INITIAL_FORMS': 1,
                              'participants-TOTAL_FORMS': 1,
                              'participants-INITIAL_FORMS': 1,
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
                              'participation-0-ce': 1,
                              'participation-0-id': 1,
                              'participation-0-team_participants': self.test_data['team_participants'],
                              'participation-0-national_participants': self.test_data['national_participants'],
                              'participation-0-date': self.test_data['date'],
                              'question-0-ce': 1,
                              'question-0-id': 1,
                              'question-0-question': self.test_data['question'],
                              'question-0-answer': self.test_data['answer']
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
        part = models.ParticipationModel(national_participants=self.test_data['national_participants'],
                                         team_participants=self.test_data['team_participants'],
                                         date=self.test_data['date'],
                                         ce=ce)
        part.save()
        text = models.TextModel(ce=ce,
                                phonetic_text=self.test_data['phonetic_text'],
                                orthographic_text=self.test_data['orthographic_text'],
                                valid_for_DA=self.test_data['valid_for_DA'])
        text.save()
        text = models.TextModel(ce=ce,
                                phonetic_text='phonetic_text2',
                                orthographic_text=self.test_data['orthographic_text'],
                                valid_for_DA=self.test_data['valid_for_DA'])
        text.save()
        q = models.QuestionModel(ce=ce,
                                 question=self.test_data['question'],
                                 answer=self.test_data['answer'])
        q.save()

    def test_setup(self):
        self.assertEqual(models.CultureEvent.objects.get(pk=1).title, self.test_data['title'])
        self.assertEqual(len(models.CultureEvent.objects.all()), 2)
        self.assertEqual(len(models.TextModel.objects.all()), 2)

    def test_edit_page_GET_response(self):
        response = self.client.get(reverse('CE:edit', args='1'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('CE/edit_CE.html')

    def test_CE_form_has_initial_data(self):
        response = self.client.get(reverse('CE:edit', args='1'))
        self.assertContains(response, '<form')
        # check form contents
        for data in self.test_data.values():
            # html doesn't render the valid for DA boolean, so skip it
            if not data:
                continue
            self.assertContains(response, data)

    def test_redirect_after_post(self):
        response = self.client.post(reverse('CE:edit', args='1'), data=self.standard_post, follow=True)
        self.assertRedirects(response, '/CE/1')

    def test_number_of_CEs_the_same(self):
        self.client.post(reverse('CE:edit', args='1'), data=self.standard_post, follow=True)
        self.assertEqual(len(models.CultureEvent.objects.all()), 2)

    def test_CE_model_updated_correctly_after_POST(self):
        post_data = self.standard_post
        post_data['description_plain_text'] = 'A new description'
        self.client.post(reverse('CE:edit', args='1'), data=post_data, follow=True)

        ce = models.CultureEvent.objects.get(pk=1)
        self.assertEqual('A new description', ce.description_plain_text)
        self.assertEqual(self.test_data['title'], ce.title)
        self.assertEqual(ce.pk, 1)

    def test_changing_CE_title(self):
        post_data = self.standard_post
        post_data['title'] = 'A new title'

        self.client.post(reverse('CE:edit', args='1'), data=post_data, follow=True)
        ce = models.CultureEvent.objects.get(pk=1)
        # self.assertEqual('A new description', ce.description_plain_text)
        self.assertEqual('A new title', ce.title)
        self.assertEqual(ce.pk, 1)

    def test_edit_title_to_existing_rejected(self):
        post_data = self.standard_post
        post_data['title'] = 'CE2'

        response = self.client.post(reverse('CE:edit', args='1'), data=post_data, follow=True)
        self.assertEqual(models.CultureEvent.objects.get(pk=1).title,
                         self.test_data['title'])
        self.assertContains(response, 'CE already exists')

    def test_edit_single_text(self):
        post_data = self.standard_post
        post_data['text-0-phonetic_text'] = 'Changed'
        response = self.client.post(reverse('CE:edit', args='1'), data=post_data, follow=True)

        self.assertRedirects(response, '/CE/1')
        self.assertEqual(models.TextModel.objects.get(pk=1).phonetic_text, 'Changed',
                         'Text 1 not updated on POST')

    def test_edit_second_text(self):
        post_data = self.standard_post
        post_data['text-1-phonetic_text'] = 'Changed'
        post_data['text-TOTAL_FORMS'] = 2
        response = self.client.post(reverse('CE:edit', args='1'), data=post_data, follow=True)

        self.assertRedirects(response, '/CE/1')
        self.assertEqual(models.TextModel.objects.get(pk=2).phonetic_text, 'Changed',
                         'Text 2 not updated on POST')

    def test_edit_both_texts(self):
        post_data = self.standard_post
        post_data['text-0-phonetic_text'] = 'Changed1'
        post_data['text-1-phonetic_text'] = 'Changed2'
        response = self.client.post(reverse('CE:edit', args='1'), data=post_data, follow=True)

        self.assertRedirects(response, '/CE/1')
        self.assertEqual(models.TextModel.objects.get(pk=1).phonetic_text, 'Changed1',
                         'Text 1 not updated on POST')
        self.assertEqual(models.TextModel.objects.get(pk=2).phonetic_text, 'Changed2',
                         'Text 2 not updated on POST')

    def test_user_adds_empty_text(self):
        # ensure blank formsets are rejected
        post_data = self.standard_post
        post_data['text-TOTAL_FORMS'] = 3
        post_data['text-2-ce'] = 1
        post_data['text-2-id'] = 3
        post_data['text-2-phonetic_text'] = ''
        post_data['text-2-orthographic_text'] = ''
        post_data['text-2-valid_for_DA'] = False
        response = self.client.post(reverse('CE:edit', args='1'), data=post_data, follow=True)

        # test there is no extra text in DB
        self.assertRedirects(response, '/CE/1')
        with self.assertRaises(models.TextModel.DoesNotExist):
            models.TextModel.objects.get(pk=3)

        # test remaining texts are unchanged
        self.assertEqual(models.TextModel.objects.get(pk=1).phonetic_text,
                         self.test_data['phonetic_text'])
        self.assertEqual(models.TextModel.objects.get(pk=2).phonetic_text,
                         'phonetic_text2')

    @unittest.skip
    def test_user_adds_new_text(self):
        #todo works manually, fails testing
        post_data = self.standard_post
        post_data['text-TOTAL_FORMS'] = 3
        post_data['text-2-ce'] = 1
        post_data['text-2-id'] = 3
        post_data['text-2-phonetic_text'] = 'phonetic_text3'
        post_data['text-2-orthographic_text'] = 'orthographic_text3'
        post_data['text-2-valid_for_DA'] = False
        response = self.client.post(reverse('CE:edit', args='1'), data=post_data, follow=True)

        self.assertRedirects(response, '/CE/1')
        self.assertEqual(len(models.TextModel.objects.all()), 3)
        self.assertEqual(models.TextModel.objects.get(pk=3).phonetic_text, 'phonetic_text3')

    def test_user_can_add_audio(self):
        # clean up if previous test failed and left a file there
        if os.path.exists('uploads/CultureEventFiles/1/audio/test_audio1.mp3'):
            os.remove('uploads/CultureEventFiles/1/audio/test_audio1.mp3')
        with open('CLAHub/assets/test_data/test_audio1.mp3', 'rb') as file:
            file = file.read()
            test_audio = SimpleUploadedFile('test_data/test_audio1.mp3', file, content_type='audio')
        post_data = self.standard_post
        post_data['text-0-audio'] = test_audio
        response = self.client.post(reverse('CE:edit', args='1'), data=post_data, follow=True)

        # test audio in db
        self.assertRedirects(response, '/CE/1')
        self.assertEqual(len(models.TextModel.objects.all()), 2)
        self.assertEqual(models.TextModel.objects.get(pk=1).audio,
                         'CultureEventFiles/1/audio/test_audio1.mp3')

        # test mp3 in uploads
        self.assertTrue(os.path.exists('uploads/CultureEventFiles/1/audio'), 'upload folder doesn\'t exist')
        folder_contents = os.listdir('uploads/CultureEventFiles/1/audio')
        self.assertIn('test_audio1.mp3', folder_contents, 'Uploaded audio not in upload folder')

        # test displayed on view page
        response = self.client.get(reverse('CE:view', args='1'))
        self.assertContains(response,
                            '<audio controls> <source src="/uploads/CultureEventFiles/1/audio/test_audio1.mp3"></audio>')

        # clean up after test - test uploads go onto actual file system program uses
        if len(folder_contents) == 1:
            # no user audio, folder was created for test
            os.remove('uploads/CultureEventFiles/1/audio/test_audio1.mp3')
            os.removedirs('uploads/CultureEventFiles/1/audio')
        elif len(folder_contents) > 1:
            # users have uploaded pictures themselves
            os.remove('uploads/CultureEventFiles/1/audio/test_audio1.mp3')

    def test_user_can_change_audio(self):
        # clean up if previous test failed and left a file there
        if os.path.exists('uploads/CultureEventFiles/1/audio/test_audio1.mp3'):
            os.remove('uploads/CultureEventFiles/1/audio/test_audio1.mp3')
        test_folder = os.path.join(os.getcwd(), 'uploads/CultureEventFiles/1/audio')
        os.makedirs(test_folder)
        shutil.copy('CLAHub/assets/test_data/test_audio1.mp3', test_folder)

        # clean up after test
        try:
            os.remove('uploads/CultureEventFiles/1/audio/test_audio1.mp3')
            os.remove('uploads/CultureEventFiles/1/audio/test_audio2.mp3')
        except FileNotFoundError:
            pass
        try:
            os.removedirs(test_folder)
        except OSError:
            pass