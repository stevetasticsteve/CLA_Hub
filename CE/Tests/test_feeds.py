from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from CE import models
from CLAHub import base_settings

import os

test_data_folder = os.path.join(base_settings.BASE_DIR, 'CLAHub', 'assets', 'test_data')


class Test_PodcastFeed(TestCase):
    def setUp(self):
        self.texts_in_db = len(models.Text.objects.all())
        test_ce = models.CultureEvent(title='test CE')
        test_ce.save()
        self.test_ce_pk = str(test_ce.pk)

        with open(os.path.join(test_data_folder, 'test_audio1.mp3'), 'rb') as file:
            file = file.read()
            audio = SimpleUploadedFile(name='test_audio1.mp3', content=file, content_type='audio')
            for i in range(10):
                text = models.Text(text_title='Text %d' % i,
                                   audio = audio,
                                   ce=test_ce)
                text.save()

    def tearDown(self):
        upload_folder = os.path.join(base_settings.BASE_DIR, 'uploads', 'CultureEventFiles', self.test_ce_pk, 'audio')
        for file in os.listdir(upload_folder):
            if 'test_audio1' in file:
                os.remove(os.path.join(upload_folder, file))

    def test_setup(self):
        texts = models.Text.objects.all()
        self.assertEqual(len(texts), self.texts_in_db + 10)
        self.assertIn('test_audio1.mp3', str(models.Text.objects.get(pk=(1 + self.texts_in_db)).audio))

    def test_podcast_response(self):
        response = self.client.get(reverse('CE:podcast'))

        self.assertEqual(response.status_code, 200)

    def test_rss_xml(self):
        response = self.client.get(reverse('CE:podcast'))

        self.assertContains(response, '<rss version="2.0"')
        self.assertContains(response, '</rss>')

    def test_enclosure(self):
        response = self.client.get(reverse('CE:podcast'))

        self.assertContains(response, '<enclosure')
        self.assertContains(response, 'url="http://')
        self.assertContains(response, 'test_audio1.mp3')

    def test_enclosure_length(self):
        response = self.client.get(reverse('CE:podcast'))

        self.assertContains(response, 'length="90"')
