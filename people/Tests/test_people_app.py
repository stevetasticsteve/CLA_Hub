from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

import datetime
import os

from people import models
from CLAHub import base_settings

# class PeopleTest(TestCase):



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

        self.test_pk1 = '1'
        self.new_pk = str(int(self.test_pk1) + 1)
        self.num_profiles = 1

    @staticmethod
    def cleanup_test_files():
        picture_folder = os.path.join(os.getcwd(), 'uploads', 'people', 'profile_pictures')
        thumbnail_folder = os.path.join(os.getcwd(), 'uploads', 'people', 'thumbnails')
        folders = [picture_folder, thumbnail_folder]
        test_data = ['test_pic1.jpg', 'test_pic2.jpg']
        for data in test_data:
            try:
                os.remove(os.path.join(picture_folder, data))
            except FileNotFoundError:
                pass
            try:
                os.remove(os.path.join(thumbnail_folder, data))
            except FileNotFoundError:
                pass
        for folder in folders:
            try:
                os.removedirs(folder)
            except OSError:
                pass

    def test_setup(self):
        self.assertEqual(1, len(models.Person.objects.all()))
        example_person = models.Person.objects.get(pk=self.test_pk1)
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

        self.assertRedirects(response, reverse('people:detail', args=self.new_pk))

    def test_database_entry_after_post(self):
        self.client.post(reverse('people:new'), self.post_data)

        self.assertEqual(len(models.Person.objects.all()), self.num_profiles + 1)
        new_entry = models.Person.objects.get(pk=self.new_pk)
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
        self.assertEqual(models.Person.objects.get(pk=self.test_pk1).name,
                         models.Person.objects.get(pk=self.new_pk).name)
        self.assertEqual(models.Person.objects.get(pk=self.test_pk1).village,
                         models.Person.objects.get(pk=self.new_pk).village)

    def test_picture_upload(self):
        try:
            uploads_dir = os.path.join(base_settings.BASE_DIR, 'uploads', 'people', 'profile_pictures')
            num_uploads = len(os.listdir(uploads_dir))
            post_data = self.post_data
            with open('CLAHub/assets/test_data/test_pic1.JPG', 'rb') as file:
                file = file.read()
                test_image = SimpleUploadedFile('test_data/test_pic1.JPG', file, content_type='image')
                post_data['picture'] = test_image
                response = self.client.post(reverse('people:new'), post_data)

            self.assertRedirects(response, reverse('people:detail', args=self.new_pk))
            # check pic in .db
            pic = models.Person.objects.get(pk=self.new_pk).picture
            self.assertEqual(str(pic), 'people/profile_pictures/test_pic1.jpg')
            thumb = models.Person.objects.get(pk=self.new_pk).thumbnail
            self.assertEqual(str(thumb), 'people/thumbnails/test_pic1.jpg')
            # test new picture present in file system
            self.assertEqual(len(os.listdir(uploads_dir)), num_uploads + 1)
            pic_path = 'uploads/people/profile_pictures/test_pic1.jpg'
            thumb_path = 'uploads/people/thumbnails/test_pic1.jpg'
            self.assertTrue(os.path.exists(pic_path),
                            'Picture not located on file system')
            self.assertTrue(os.path.exists(thumb_path),
                            'Picture not located on file system')
            # test thumbnail smaller than pic
            self.assertLess(os.path.getsize(thumb_path), os.path.getsize(pic_path),
                            'Compression isn\'t working')

        finally:
            self.cleanup_test_files()

#
# class EditPersonTest(NewPersonViewTest):
#     def setUp(self):
#         pass
#         # super(NewPersonViewTest)
#
#     def test_edit(self):
#         print(self.test_pk1)

