from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile


import datetime

from people import models


class PeopleHomeAndAlphabeticalPageTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        credentials = User(username='Tester')
        credentials.set_password('secure_password')
        credentials.save()

    def setUp(self):
        self.client.login(username='Tester', password='secure_password')

    def test_home_get_response(self):
        response = self.client.get(reverse('people:home'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('people/home.html')

    def test_home_page_content(self):
        response = self.client.get(reverse('people:home'))

        self.assertContains(response, 'Recently edited profiles')

    def test_alphabetical_get_response(self):
        response = self.client.get(reverse('people:alphabetically'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('people/alphabetical.html')

    def test_alphabetical_content(self):
        response = self.client.get(reverse('people:alphabetically'))

        self.assertContains(response, 'People Alphabetically')


class NewPersonViewTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        credentials = User(username='Tester')
        credentials.set_password('secure_password')
        credentials.save()

    def setUp(self):
        self.client.login(username='Tester', password='secure_password')
        self.post_data = {
            'name': 'Test person 2',
            'village': '1',
            'clan': 'Python clan',
            'born': '1980-01-01',
            'medical': 'Broken face',
            'team_contact': 'We met them',
            'education': '1'
        }
        # add an example record
        example = models.Person(
            name='Test person 1',
            village='2',
            clan='Snake clan',
            born=datetime.date(1970,2,2),
            medical='Healthy',
            team_contact='high fived us',
            education=2
        )
        example.save()

    def test_setup(self):
        self.assertEqual(1, len(models.Person.objects.all()))
        example_person = models.Person.objects.get(pk=1)
        self.assertEqual('Test person 1', example_person.name)
        self.assertEqual(datetime.date(1970, 2, 2), example_person.born)

    def test_new_person_GET_response(self):
        response = self.client.get(reverse('people:new'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('people/new.html')

    def test_new_person_content(self):
        response = self.client.get(reverse('people:new'))

        self.assertContains(response, 'Add a Person')

    def test_redirect_after_post(self):
        response = self.client.post(reverse('people:new'), self.post_data)

        self.assertRedirects(response, '/people/2')

    def test_database_entry_after_post(self):
        self.client.post(reverse('people:new'), self.post_data)

        self.assertEqual(len(models.Person.objects.all()), 2)
        new_entry = models.Person.objects.get(pk=2)
        self.assertEqual(self.post_data['name'], new_entry.name)
        self.assertEqual(self.post_data['medical'], new_entry.medical)
        self.assertEqual(self.post_data['education'], new_entry.education)
        self.assertEqual(datetime.date, type(new_entry.born))

    def test_same_data_allowed(self):
        # .db unique constraint not applied as names, and village can be shared
        post_data = self.post_data
        post_data['name'] = 'Test person 1'
        post_data['village'] = '2'
        self.client.post(reverse('people:new'), post_data)

        self.assertEqual(len(models.Person.objects.all()), 2)
        self.assertEqual(models.Person.objects.get(pk=1).name, models.Person.objects.get(pk=2).name)
        self.assertEqual(models.Person.objects.get(pk=1).village, models.Person.objects.get(pk=2).village)

    def test_picture_upload(self):
        post_data = self.post_data
        with open('CLAHub/assets/test_data/test_pic1.JPG', 'rb') as file:
            file = file.read()
            test_image = SimpleUploadedFile('test_data/test_pic1.JPG', file, content_type='image')
        post_data['picture'] = test_image
        self.client.post(reverse('people:new'), post_data)

        self.
