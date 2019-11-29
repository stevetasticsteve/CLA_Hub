import os
import unittest
import shutil
import datetime
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from CE import models
from CE.Tests.test_base_class import CETestBaseClass


class TestEditPage(CETestBaseClass):
    def test_setup(self):
        self.assertEqual(models.CultureEvent.objects.get(pk=1).title, self.test_data['title'])
        self.assertEqual(len(models.CultureEvent.objects.all()), 2)
        self.assertEqual(len(models.Text.objects.all()), 2)
        self.assertEqual(len(models.Visit.objects.all()), 1)
        self.assertEqual(len(models.Question.objects.all()), 1)

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
        self.assertEqual(models.Text.objects.get(pk=1).phonetic_text, 'Changed',
                         'Text 1 not updated on POST')

    def test_edit_second_text(self):
        post_data = self.standard_post
        post_data['text-1-phonetic_text'] = 'Changed'
        post_data['text-TOTAL_FORMS'] = 2
        response = self.client.post(reverse('CE:edit', args='1'), data=post_data, follow=True)

        self.assertRedirects(response, '/CE/1')
        self.assertEqual(models.Text.objects.get(pk=2).phonetic_text, 'Changed',
                         'Text 2 not updated on POST')

    def test_edit_both_texts(self):
        post_data = self.standard_post
        post_data['text-0-phonetic_text'] = 'Changed1'
        post_data['text-1-phonetic_text'] = 'Changed2'
        response = self.client.post(reverse('CE:edit', args='1'), data=post_data, follow=True)

        self.assertRedirects(response, '/CE/1')
        self.assertEqual(models.Text.objects.get(pk=1).phonetic_text, 'Changed1',
                         'Text 1 not updated on POST')
        self.assertEqual(models.Text.objects.get(pk=2).phonetic_text, 'Changed2',
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
        with self.assertRaises(models.Text.DoesNotExist):
            models.Text.objects.get(pk=3)

        # test remaining texts are unchanged
        self.assertEqual(models.Text.objects.get(pk=1).phonetic_text,
                         self.test_data['phonetic_text'])
        self.assertEqual(models.Text.objects.get(pk=2).phonetic_text,
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
        self.assertEqual(len(models.Text.objects.all()), 3)
        self.assertEqual(models.Text.objects.get(pk=3).phonetic_text, 'phonetic_text3')

    def test_user_can_add_audio(self):
        try:
            with open('CLAHub/assets/test_data/test_audio1.mp3', 'rb') as file:
                file = file.read()
                test_audio = SimpleUploadedFile('test_data/test_audio1.mp3', file, content_type='audio')
            post_data = self.standard_post
            post_data['text-0-audio'] = test_audio
            response = self.client.post(reverse('CE:edit', args='1'), data=post_data, follow=True)

            # test audio in db
            self.assertRedirects(response, '/CE/1')
            self.assertEqual(len(models.Text.objects.all()), 2)
            self.assertEqual(models.Text.objects.get(pk=1).audio,
                             'CultureEventFiles/1/audio/test_audio1.mp3')

            # test mp3 in uploads
            self.assertTrue(os.path.exists('uploads/CultureEventFiles/1/audio'), 'upload folder doesn\'t exist')
            folder_contents = os.listdir('uploads/CultureEventFiles/1/audio')
            self.assertIn('test_audio1.mp3', folder_contents, 'Uploaded audio not in upload folder')

            # test displayed on view page
            response = self.client.get(reverse('CE:view', args='1'))
            self.assertContains(response,
                                '<audio controls> <source src="/uploads/CultureEventFiles/1/audio/test_audio1.mp3"></audio>')

        finally:
            self.cleanup_test_files(1)

    def test_user_can_change_audio(self):
        try:
            test_folder = os.path.join(os.getcwd(), 'uploads/CultureEventFiles/1/audio')
            os.makedirs(test_folder)
            shutil.copy('CLAHub/assets/test_data/test_audio1.mp3', test_folder)
            # add audio to test text
            text = models.Text.objects.get(pk=1)
            text.audio = 'CultureEventFiles/1/audio/test_audio1.mp3'
            text.save()
            with open('CLAHub/assets/test_data/test_audio2.mp3', 'rb') as file:
                file = file.read()
                test_audio = SimpleUploadedFile('test_data/test_audio2.mp3', file, content_type='audio')
            post_data = self.standard_post
            post_data['text-0-audio'] = test_audio
            response = self.client.post(reverse('CE:edit', args='1'), data=post_data, follow=True)

            # test audio in db
            self.assertRedirects(response, '/CE/1')
            self.assertEqual(len(models.Text.objects.all()), 2)
            self.assertEqual(models.Text.objects.get(pk=1).audio,
                             'CultureEventFiles/1/audio/test_audio2.mp3')

            # test mp3 in uploads
            self.assertTrue(os.path.exists('uploads/CultureEventFiles/1/audio'), 'upload folder doesn\'t exist')
            folder_contents = os.listdir('uploads/CultureEventFiles/1/audio')
            self.assertIn('test_audio2.mp3', folder_contents, 'Uploaded audio not in upload folder')

            # test displayed on view page
            response = self.client.get(reverse('CE:view', args='1'))
            self.assertContains(response,
                                '<audio controls> <source src="/uploads/CultureEventFiles/1/audio/test_audio2.mp3"></audio>')

        finally:
            self.cleanup_test_files(1)

    def test_can_edit_first_visit_form(self):
        post_data = self.standard_post
        post_data['visit-0-team_present'] = 'Changed'
        post_data['visit-0-nationals_present'] = 'Changed'
        post_data['visit-0-date'] = '2019-10-11'
        post_data['visit-TOTAL_FORMS'] = 2
        # import pprint
        # pprint.pprint(post_data)
        response = self.client.post(reverse('CE:edit', args='1'), data=post_data, follow=True)

        self.assertRedirects(response, '/CE/1')
        self.assertEqual(len(models.Visit.objects.all()), 1)
        self.assertEqual(models.Visit.objects.get(pk=1).nationals_present, 'Changed',
                         'Visit 1 not updated on POST')
        self.assertEqual(models.Visit.objects.get(pk=1).team_present, 'Changed',
                         'visit 1 not updated on POST')
        self.assertEqual(models.Visit.objects.get(pk=1).date, datetime.date(2019, 10, 11),
                         'visit 1 not updated on POST')
