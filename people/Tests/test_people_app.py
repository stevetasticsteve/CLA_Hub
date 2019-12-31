from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.files import File

import datetime
import os
import shutil
from unittest import skip

from people import models
from CLAHub import base_settings


class PeopleTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        credentials = User(username='Tester')
        credentials.set_password('secure_password')
        credentials.save()

    def setUp(self):
        self.client.login(username='Tester', password='secure_password')
        self.new_post_data = {
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
            born=datetime.date(1970, 2, 2),
            medical='Healthy',
            team_contact='high fived us',
            education=2
        )
        example.save()

        self.unchanged_post = {
            'name': 'Test person 1',
            'village': '2',
            'clan': 'Snake clan',
            'born': '1970-02-02',
            'medical': 'Healthy',
            'team_contact': 'high fived us',
            'education': '2'
        }

        self.test_pk1 = '1'
        self.new_pk = str(int(self.test_pk1) + 1)
        self.num_profiles = 1
        self.thumbnail_folder = os.path.join(os.getcwd(), 'uploads', 'people', 'thumbnails')
        self.picture_folder = os.path.join(os.getcwd(), 'uploads', 'people', 'profile_pictures')
        self.test_pic1 = 'test_pic1.jpg'
        self.test_pic1_path = 'CLAHub/assets/test_data/test_pic1.jpg'

    def get_num_of_uploads(self):
        return len(os.listdir(self.picture_folder))

    def cleanup_test_files(self):
        folders = [self.picture_folder, self.thumbnail_folder]
        test_data = ['test_pic1.jpg', 'test_pic2.jpg']
        for data in test_data:
            try:
                os.remove(os.path.join(self.picture_folder, data))
            except FileNotFoundError:
                pass
            try:
                os.remove(os.path.join(self.thumbnail_folder, data))
            except FileNotFoundError:
                pass
        for folder in folders:
            try:
                os.removedirs(folder)
            except OSError:
                pass

    def add_test_picture_file(self):
        # add picture file to uploads
        num_uploads = len(os.listdir(self.picture_folder))
        test_image_path = os.path.join(base_settings.BASE_DIR, 'CLAHub', 'assets', 'test_data', self.test_pic1)

        # add image to test profile
        person = models.Person.objects.get(pk=self.test_pk1)
        with open(self.test_pic1_path, 'rb') as file:
            file = file.read()
            person.picture = SimpleUploadedFile(name=self.test_pic1, content=file, content_type='image')
            person.save()
        return num_uploads

    def run_test_uploaded_file(self):
        pic_db_path = os.path.join('people', 'profile_pictures', self.test_pic1)
        pic_path = os.path.join(self.picture_folder, self.test_pic1)
        thumb_db_path = os.path.join('people', 'thumbnails', self.test_pic1)
        thumb_path = os.path.join(self.thumbnail_folder, self.test_pic1)

        # check pic in .db
        person = models.Person.objects.get(pk=self.test_pk1)
        self.assertEqual(str(person.picture), pic_db_path)
        self.assertEqual(str(person.thumbnail), thumb_db_path)

        # test new picture present in file system
        self.assertTrue(os.path.exists(pic_path),
                        'Picture not located on file system')
        self.assertTrue(os.path.exists(thumb_path),
                        'Picture not located on file system')
        input()


class BaseClassTest(PeopleTest):
    def test_setup(self):
        self.assertEqual(1, len(models.Person.objects.all()))
        example_person = models.Person.objects.get(pk=self.test_pk1)
        self.assertEqual('Test person 1', example_person.name)
        self.assertEqual(datetime.date(1970, 2, 2), example_person.born)

    def test_picture_add_method(self):
        try:
            self.add_test_picture_file()
            self.run_test_uploaded_file()
        finally:
            self.cleanup_test_files()


# class PeopleHomeAndAlphabeticalPageTest(PeopleTest):
#     def test_home_get_response(self):
#         response = self.client.get(reverse('people:home'))
#
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed('people/home.html')
#
#     def test_home_page_content(self):
#         response = self.client.get(reverse('people:home'))
#
#         self.assertContains(response, 'Recently edited profiles')
#
#     def test_alphabetical_get_response(self):
#         response = self.client.get(reverse('people:alphabetically'))
#
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed('people/alphabetical.html')
#
#     def test_alphabetical_content(self):
#         response = self.client.get(reverse('people:alphabetically'))
#
#         self.assertContains(response, 'People Alphabetically')
#
#
# class NewPersonViewTest(PeopleTest):
#     def test_new_person_GET_response(self):
#         response = self.client.get(reverse('people:new'))
#
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed('people/new.html')
#
#     def test_new_person_content(self):
#         response = self.client.get(reverse('people:new'))
#
#         self.assertContains(response, 'Add a Person')
#
#     def test_redirect_after_post(self):
#         response = self.client.post(reverse('people:new'), self.new_post_data)
#
#         self.assertRedirects(response, reverse('people:detail', args=self.new_pk))
#
#     def test_database_entry_after_post(self):
#         self.client.post(reverse('people:new'), self.new_post_data)
#
#         self.assertEqual(len(models.Person.objects.all()), self.num_profiles + 1)
#         new_entry = models.Person.objects.get(pk=self.new_pk)
#         self.assertEqual(self.new_post_data['name'], new_entry.name)
#         self.assertEqual(self.new_post_data['medical'], new_entry.medical)
#         self.assertEqual(self.new_post_data['education'], new_entry.education)
#         self.assertEqual(datetime.date, type(new_entry.born))
#
#     def test_same_data_allowed(self):
#         # .db unique constraint not applied as names, and village can be shared
#         post_data = self.new_post_data
#         post_data['name'] = 'Test person 1'
#         post_data['village'] = '2'
#         self.client.post(reverse('people:new'), post_data)
#
#         self.assertEqual(len(models.Person.objects.all()), 2)
#         self.assertEqual(models.Person.objects.get(pk=self.test_pk1).name,
#                          models.Person.objects.get(pk=self.new_pk).name)
#         self.assertEqual(models.Person.objects.get(pk=self.test_pk1).village,
#                          models.Person.objects.get(pk=self.new_pk).village)
#
#     def test_picture_upload(self):
#         try:
#             uploads_before = self.get_num_of_uploads()
#             post_data = self.new_post_data
#             with open('CLAHub/assets/test_data/test_pic1.jpg', 'rb') as file:
#                 file = file.read()
#                 test_image = SimpleUploadedFile('test_data/test_pic1.jpg', file, content_type='image')
#                 post_data['picture'] = test_image
#                 response = self.client.post(reverse('people:new'), post_data)
#
#             self.assertRedirects(response, reverse('people:detail', args=self.new_pk))
#             # check pic in .db
#             pic = models.Person.objects.get(pk=self.new_pk).picture
#             self.assertEqual(str(pic), 'people/profile_pictures/test_pic1.jpg')
#             thumb = models.Person.objects.get(pk=self.new_pk).thumbnail
#             self.assertEqual(str(thumb), 'people/thumbnails/test_pic1.jpg')
#             # test new picture present in file system
#             self.assertEqual(self.get_num_of_uploads(), uploads_before + 1)
#             pic_path = 'uploads/people/profile_pictures/test_pic1.jpg'
#             thumb_path = 'uploads/people/thumbnails/test_pic1.jpg'
#             self.assertTrue(os.path.exists(pic_path),
#                             'Picture not located on file system')
#             self.assertTrue(os.path.exists(thumb_path),
#                             'Picture not located on file system')
#             # test thumbnail smaller than pic
#             self.assertLess(os.path.getsize(thumb_path), os.path.getsize(pic_path),
#                             'Compression isn\'t working')
#
#         finally:
#             self.cleanup_test_files()
#
#
# class EditPersonTest(PeopleTest):
#     def test_edit_response(self):
#         response = self.client.get(reverse('people:edit', args=self.test_pk1))
#
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed('people/edit.html')
#
#     def test_edit_content(self):
#         response = self.client.get(reverse('people:edit', args=self.test_pk1))
#
#         self.assertContains(response, 'Test person 1')
#
#     def test_redirect_after_post_no_changes(self):
#         response = self.client.post(reverse('people:edit', args=self.test_pk1), data=self.unchanged_post)
#
#         self.assertRedirects(response, reverse('people:detail', args=self.test_pk1))
#
#     def test_redirect_after_change(self):
#         post_data = self.unchanged_post
#         post_data['name'] = 'Changed'
#         response = self.client.post(reverse('people:edit', args=self.test_pk1), data=post_data)
#
#         self.assertRedirects(response, reverse('people:detail', args=self.test_pk1))
#
#     def test_contents_changed(self):
#         post_data = self.unchanged_post
#         post_data['name'] = 'Changed'
#         self.client.post(reverse('people:edit', args=self.test_pk1), data=post_data)
#
#         self.assertEqual(models.Person.objects.get(pk=self.test_pk1).name, 'Changed')
#
#     def test_contents_erased(self):
#         post_data = self.unchanged_post
#         post_data['clan'] = ''
#         self.client.post(reverse('people:edit', args=self.test_pk1), data=post_data)
#
#         self.assertEqual(models.Person.objects.get(pk=self.test_pk1).clan, '')
#
#     def test_name_removed_fail(self):
#         post_data = self.unchanged_post
#         post_data['name'] = ''
#         response = self.client.post(reverse('people:edit', args=self.test_pk1), data=post_data)
#
#         # should respond with the original form
#         self.assertContains(response, 'Test person 1')
#
#     def test_add_picture(self):
#         try:
#             uploads_dir = os.path.join(base_settings.BASE_DIR, 'uploads', 'people', 'profile_pictures')
#             num_uploads = len(os.listdir(uploads_dir))
#             post_data = self.unchanged_post
#             with open('CLAHub/assets/test_data/test_pic1.jpg', 'rb') as file:
#                 file = file.read()
#                 test_image = SimpleUploadedFile('test_data/test_pic1.jpg', file, content_type='image')
#                 post_data['picture'] = test_image
#                 response = self.client.post(reverse('people:edit', args=self.test_pk1), post_data, follow=True)
#
#             self.assertRedirects(response, reverse('people:detail', args=self.test_pk1))
#             # test pic in response
#             self.assertContains(response, 'test_pic1.jpg')
#             # check pic in .db
#             pic = models.Person.objects.get(pk=self.test_pk1).picture
#             self.assertEqual(str(pic), 'people/profile_pictures/test_pic1.jpg')
#             thumb = models.Person.objects.get(pk=self.test_pk1).thumbnail
#             self.assertEqual(str(thumb), 'people/thumbnails/test_pic1.jpg')
#             # test new picture present in file system
#             self.assertEqual(len(os.listdir(uploads_dir)), num_uploads + 1)
#             pic_path = 'uploads/people/profile_pictures/test_pic1.jpg'
#             thumb_path = 'uploads/people/thumbnails/test_pic1.jpg'
#             self.assertTrue(os.path.exists(pic_path),
#                             'Picture not located on file system')
#             self.assertTrue(os.path.exists(thumb_path),
#                             'Picture not located on file system')
#             # test thumbnail smaller than pic
#             self.assertLess(os.path.getsize(thumb_path), os.path.getsize(pic_path),
#                             'Compression isn\'t working')
#
#         finally:
#             self.cleanup_test_files()
#
#     def test_change_picture(self):
#         try:
#             self.add_test_picture_file()
#             uploads_before = self.get_num_of_uploads()
#             replacement_image_path = os.path.join(base_settings.BASE_DIR, 'CLAHub', 'assets', 'test_data',
#                                                   'test_pic2.jpg')
#             with open(replacement_image_path, 'rb') as file:
#                 file = file.read()
#                 test_pic = SimpleUploadedFile('test_data/test_pic2.jpg',
#                                               file, content_type='image')
#                 post_data = self.unchanged_post
#                 post_data['picture'] = test_pic
#                 response = self.client.post(reverse('people:edit', args=self.test_pk1), post_data, follow=True)
#
#             self.assertRedirects(response, reverse('people:detail', args=self.test_pk1))
#             # test pic in response
#             self.assertContains(response, 'test_pic2.jpg')
#             # test pic in .db
#             profile = models.Person.objects.get(pk=self.test_pk1)
#             self.assertEqual(str(profile.picture), 'people/profile_pictures/test_pic2.jpg')
#             self.assertEqual(str(profile.thumbnail), 'people/thumbnails/test_pic2.jpg')
#             # test pic in file system
#             self.assertEqual(self.get_num_of_uploads(), uploads_before + 1)
#             pic_path = 'uploads/people/profile_pictures/test_pic2.jpg'
#             thumb_path = 'uploads/people/thumbnails/test_pic2.jpg'
#             self.assertTrue(os.path.exists(pic_path),
#                             'Picture not located on file system')
#             self.assertTrue(os.path.exists(thumb_path),
#                             'Picture not located on file system')
#             # test old pic still there
#             pic_path = 'uploads/people/profile_pictures/test_pic1.jpg'
#             self.assertTrue(os.path.exists(pic_path),
#                             'Picture not located on file system')
#         finally:
#             self.cleanup_test_files()
#
#     @ skip
#     def test_post_with_blank_picture(self):
#         # The edit form passes pic = '' if the user edits a profile containing a picture and doesn't specify a new picture
#         # The picture shouldn't be overwritten by a blank
#         try:
#             self.add_test_picture_file()
#             uploads_before = self.get_num_of_uploads()
#             post_data = self.unchanged_post
#             post_data['picture'] = ''
#             response = self.client.post(reverse('people:edit', args=self.test_pk1), post_data, follow=True)
#
#             self.assertRedirects(response, reverse('people:detail', args=self.test_pk1))
#             # test pic in response
#             # self.assertContains(response, 'test_pic1.jpg')
#             # test pic in .db
#             profile = models.Person.objects.get(pk=self.test_pk1)
#             self.assertEqual(str(profile.picture), 'people/profile_pictures/test_pic1.jpg')
#             self.assertEqual(str(profile.thumbnail), 'people/thumbnails/test_pic1.jpg')
#             # test pic in file system
#             self.assertEqual(self.get_num_of_uploads(), uploads_before + 2)
#             pic_path = 'uploads/people/profile_pictures/test_pic1.jpg'
#             thumb_path = 'uploads/people/thumbnails/test_pic1.jpg'
#             self.assertTrue(os.path.exists(pic_path),
#                             'Picture not located on file system')
#             self.assertTrue(os.path.exists(thumb_path),
#                             'Picture not located on file system')
#
#         finally:
#             self.cleanup_test_files()
#
#     def test_picture_clear(self):
#         try:
#             self.add_test_picture_file()
#             uploads_before = self.get_num_of_uploads()
#             post_data = self.unchanged_post
#             post_data['picture-clear'] = 'on'
#             response = self.client.post(reverse('people:edit', args=self.test_pk1), post_data, follow=True)
#
#             self.assertRedirects(response, reverse('people:detail', args=self.test_pk1))
#             # test pic not in response
#             self.assertNotContains(response, 'test_pic1.jpg')
#             # test blank in .db
#             profile = models.Person.objects.get(pk=self.test_pk1)
#             self.assertEqual(str(profile.picture), '')
#             self.assertEqual(str(profile.thumbnail), '')
#             # test pic still in file system
#             self.assertEqual(self.get_num_of_uploads(), uploads_before)
#             pic_path = 'uploads/people/profile_pictures/test_pic1.jpg'
#             self.assertTrue(os.path.exists(pic_path),
#                             'Picture not located on file system')
#
#         finally:
#             self.cleanup_test_files()
#
#     @ skip
#     def test_uploading_pre_existing_file(self):
#         try:
#             uploads_before = self.get_num_of_uploads()
#             post_data = self.unchanged_post
#             with open('CLAHub/assets/test_data/test_pic1.jpg', 'rb') as file:
#                 file = file.read()
#                 test_image = SimpleUploadedFile('test_data/test_pic1.jpg', file, content_type='image')
#                 post_data['picture'] = test_image
#                 response = self.client.post(reverse('people:edit', args=self.test_pk1), post_data, follow=True)
#
#             self.assertRedirects(response, reverse('people:detail', args=self.test_pk1))
#             # test pic in response
#             self.assertContains(response, 'test_pic1.jpg')
#             # check pic in .db
#             pic = models.Person.objects.get(pk=self.test_pk1).picture
#             self.assertEqual(str(pic), 'people/profile_pictures/test_pic1.jpg')
#             thumb = models.Person.objects.get(pk=self.test_pk1).thumbnail
#             self.assertEqual(str(thumb), 'people/thumbnails/test_pic1.jpg')
#             # test new picture present in file system
#             self.assertEqual(self.get_num_of_uploads(), uploads_before)
#             pic_path = 'uploads/people/profile_pictures/test_pic1.jpg'
#             thumb_path = 'uploads/people/thumbnails/test_pic1.jpg'
#             self.assertTrue(os.path.exists(pic_path),
#                             'Picture not located on file system')
#             self.assertTrue(os.path.exists(thumb_path),
#                             'Picture not located on file system')
#             # test thumbnail smaller than pic
#             self.assertLess(os.path.getsize(thumb_path), os.path.getsize(pic_path),
#                             'Compression isn\'t working')
#
#         finally:
#             self.cleanup_test_files()