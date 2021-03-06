import datetime
import os

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from CLAHub import base_settings
from people import models


class PeopleTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        credentials = User(username='Tester')
        credentials.set_password('secure_password')
        credentials.save()

    def setUp(self):
        self.client.login(username='Tester', password='secure_password')
        self.village = models.Village(village_name='Torokum')
        self.village.save()
        self.new_post_data = {
            'name': 'Test person 2',
            'village': '2',
            'clan': 'Python clan',
            'born': '1980-01-01',
            'medical': 'Broken face',
            'team_contact': 'We met them',
            'education': '1'
        }
        # add an example record
        self.example_village = models.Village(village_name='Kokoma')
        self.example_village.save()
        example = models.Person(
            name='Test person 1',
            village=self.example_village,
            clan='Snake clan',
            born=datetime.date(1970, 2, 2),
            medical='Healthy',
            team_contact='high fived us',
            education=2
        )
        example.save()

        self.unchanged_post = {
            'name': 'Test person 1',
            'village': '1',
            'clan': 'Snake clan',
            'born': '1970-02-02',
            'medical': 'Healthy',
            'team_contact': 'high fived us',
            'education': '2'
        }

        self.test_pk1 = '1'
        self.new_pk = str(int(self.test_pk1) + 1)
        self.num_profiles = 1
        self.thumbnail_folder = os.path.join(base_settings.MEDIA_ROOT, 'people', 'thumbnails')
        self.picture_folder = os.path.join(base_settings.MEDIA_ROOT, 'people', 'profile_pictures')
        self.test_data_path = os.path.join(base_settings.BASE_DIR, 'CLAHub', 'assets', 'test_data')
        self.test_pic1_path = os.path.join(self.test_data_path, 'test_pic1.jpg')
        self.test_pic2_path = os.path.join(self.test_data_path, 'test_pic2.jpg')

    def get_num_of_uploads(self):
        return len(os.listdir(self.picture_folder))

    def cleanup_test_files(self):
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
        example_ce_folder = os.path.join(base_settings.MEDIA_ROOT, 'CultureEventFiles', '1', 'audio')
        if os.path.exists(example_ce_folder):
            for f in os.listdir(example_ce_folder):
                if f != 'example_audio1.mp3':
                    os.remove(os.path.join(example_ce_folder, f))

    def add_test_picture_file(self):
        # add picture file to uploads
        num_uploads = len(os.listdir(self.picture_folder))

        # add image to test profile
        person = models.Person.objects.get(pk=self.test_pk1)
        with open(self.test_pic1_path, 'rb') as file:
            file = file.read()
            person.picture = SimpleUploadedFile(name='test_pic1.jpg', content=file, content_type='image')
            person.save()
        return num_uploads

    def run_test_uploaded_file(self, pk):
        pic_db_path = os.path.join('people', 'profile_pictures', 'test_pic1.jpg')
        pic_path = os.path.join(self.picture_folder, 'test_pic1.jpg')
        thumb_db_path = os.path.join('people', 'thumbnails', 'test_pic1.jpg')
        thumb_path = os.path.join(self.thumbnail_folder, 'test_pic1.jpg')

        # check pic in .db
        person = models.Person.objects.get(pk=pk)
        self.assertEqual(str(person.picture), pic_db_path)
        self.assertEqual(str(person.thumbnail), thumb_db_path)

        # test new picture present in file system
        self.assertTrue(os.path.exists(pic_path),
                        'Picture not located on file system')
        self.assertTrue(os.path.exists(thumb_path),
                        'Picture not located on file system')


class BaseClassTest(PeopleTest):
    def test_setup(self):
        self.assertEqual(1, len(models.Person.objects.all()))
        example_person = models.Person.objects.get(pk=self.test_pk1, village=self.example_village)
        self.assertEqual('Test person 1', example_person.name)
        self.assertEqual(datetime.date(1970, 2, 2), example_person.born)

    def test_picture_add_method(self):
        try:
            self.add_test_picture_file()
            self.run_test_uploaded_file(self.test_pk1)
        finally:
            self.cleanup_test_files()


class PeopleHomeAndAlphabeticalPageTest(PeopleTest):
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


class NewPersonViewTest(PeopleTest):
    def test_new_person_GET_response(self):
        response = self.client.get(reverse('people:new'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('people/new.html')

    def test_new_person_content(self):
        response = self.client.get(reverse('people:new'))

        self.assertContains(response, 'Add a Person')

    def test_redirect_after_post(self):
        response = self.client.post(reverse('people:new'), self.new_post_data)

        self.assertRedirects(response, reverse('people:detail', args=self.new_pk))

    def test_database_entry_after_post(self):
        self.client.post(reverse('people:new'), self.new_post_data)

        self.assertEqual(len(models.Person.objects.all()), self.num_profiles + 1)
        new_entry = models.Person.objects.get(pk=self.new_pk)
        self.assertEqual(self.new_post_data['name'], new_entry.name)
        self.assertEqual(self.new_post_data['education'], new_entry.education)
        self.assertEqual(datetime.date, type(new_entry.born))

    def test_same_data_allowed(self):
        # .db unique constraint not applied as names, and village can be shared
        post_data = self.new_post_data
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
            uploads_before = self.get_num_of_uploads()
            post_data = self.new_post_data
            with open(self.test_pic1_path, 'rb') as file:
                file = file.read()
                test_image = SimpleUploadedFile('test_data/test_pic1.jpg', file, content_type='image')
                post_data['picture'] = test_image
                response = self.client.post(reverse('people:new'), post_data)

            self.assertRedirects(response, reverse('people:detail', args=self.new_pk))
            self.run_test_uploaded_file(self.new_pk)
            self.assertEqual(self.get_num_of_uploads(), uploads_before + 1)

        finally:
            self.cleanup_test_files()

    def test_picture_compression(self):
        try:
            post_data = self.new_post_data
            with open(self.test_pic1_path, 'rb') as file:
                file = file.read()
                test_image = SimpleUploadedFile('test_data/test_pic1.jpg', file, content_type='image')
                post_data['picture'] = test_image
                self.client.post(reverse('people:new'), post_data)

            test_file_size = os.path.getsize(self.test_pic1_path)
            profile_pic_size = os.path.getsize(os.path.join(self.picture_folder, 'test_pic1.jpg'))
            thumbnail_size = os.path.getsize(os.path.join(self.thumbnail_folder, 'test_pic1.jpg'))
            self.assertLess(thumbnail_size, profile_pic_size)
            self.assertLess(profile_pic_size, test_file_size)

            self.assertLess(profile_pic_size, 500000, 'Profile picture larger than 500kb')
            self.assertLess(thumbnail_size, 50000, 'Profile picture larger than 50kb')

        finally:
            self.cleanup_test_files()


class EditPersonTest(PeopleTest):
    def test_edit_response(self):
        response = self.client.get(reverse('people:edit', args=self.test_pk1))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('people/edit.html')

    def test_edit_content(self):
        response = self.client.get(reverse('people:edit', args=self.test_pk1))

        self.assertContains(response, 'Test person 1')

    def test_redirect_after_post_no_changes(self):
        response = self.client.post(reverse('people:edit', args=self.test_pk1), data=self.unchanged_post)

        self.assertRedirects(response, reverse('people:detail', args=self.test_pk1))

    def test_redirect_after_change(self):
        post_data = self.unchanged_post
        post_data['name'] = 'Changed'
        response = self.client.post(reverse('people:edit', args=self.test_pk1), data=post_data)

        self.assertRedirects(response, reverse('people:detail', args=self.test_pk1))

    def test_contents_changed(self):
        post_data = self.unchanged_post
        post_data['name'] = 'Changed'
        self.client.post(reverse('people:edit', args=self.test_pk1), data=post_data)

        self.assertEqual(models.Person.objects.get(pk=self.test_pk1).name, 'Changed')

    def test_contents_erased(self):
        post_data = self.unchanged_post
        post_data['clan'] = ''
        self.client.post(reverse('people:edit', args=self.test_pk1), data=post_data)

        self.assertEqual(models.Person.objects.get(pk=self.test_pk1).clan, '')

    def test_name_removed_fail(self):
        post_data = self.unchanged_post
        post_data['name'] = ''
        response = self.client.post(reverse('people:edit', args=self.test_pk1), data=post_data)

        # should respond with the original form
        self.assertContains(response, 'Test person 1')

    def test_add_picture(self):
        try:
            uploads_before = self.get_num_of_uploads()
            post_data = self.unchanged_post
            with open(self.test_pic1_path, 'rb') as file:
                file = file.read()
                test_image = SimpleUploadedFile('test_data/test_pic1.jpg', file, content_type='image')
                post_data['picture'] = test_image
                response = self.client.post(reverse('people:edit', args=self.test_pk1), post_data, follow=True)

            self.assertRedirects(response, reverse('people:detail', args=self.test_pk1))
            # test pic in response
            self.assertContains(response, 'test_pic1.jpg')
            self.run_test_uploaded_file(self.test_pk1)
            self.assertEqual(self.get_num_of_uploads(), uploads_before + 1)

        finally:
            self.cleanup_test_files()

    def test_change_picture(self):
        try:
            self.add_test_picture_file()
            uploads_before = self.get_num_of_uploads()
            replacement_image_path = os.path.join(base_settings.BASE_DIR, 'CLAHub', 'assets', 'test_data',
                                                  'test_pic2.jpg')
            with open(replacement_image_path, 'rb') as file:
                file = file.read()
                test_pic = SimpleUploadedFile('test_data/test_pic2.jpg',
                                              file, content_type='image')
                post_data = self.unchanged_post
                post_data['picture'] = test_pic
                response = self.client.post(reverse('people:edit', args=self.test_pk1), post_data, follow=True)

            self.assertRedirects(response, reverse('people:detail', args=self.test_pk1))
            # test pic in response
            self.assertContains(response, 'test_pic2.jpg')
            # test pic in .db
            profile = models.Person.objects.get(pk=self.test_pk1)
            self.assertEqual(str(profile.picture), 'people/profile_pictures/test_pic2.jpg')
            self.assertEqual(str(profile.thumbnail), 'people/thumbnails/test_pic2.jpg')
            # test pic in file system
            self.assertEqual(self.get_num_of_uploads(), uploads_before + 1)
            pic_path = os.path.join(base_settings.MEDIA_ROOT, 'people', 'profile_pictures', 'test_pic2.jpg')
            thumb_path = os.path.join(base_settings.MEDIA_ROOT, 'people', 'thumbnails', 'test_pic2.jpg')
            self.assertTrue(os.path.exists(pic_path),
                            'Picture not located on file system')
            self.assertTrue(os.path.exists(thumb_path),
                            'Picture not located on file system')
            # test old pic still there
            pic_path = os.path.join(base_settings.MEDIA_ROOT, 'people', 'profile_pictures', 'test_pic1.jpg')
            self.assertTrue(os.path.exists(pic_path),
                            'Picture not located on file system')
        finally:
            self.cleanup_test_files()

    def test_post_with_blank_picture(self):
        # The edit form passes pic = '' if the user edits a profile containing a picture and doesn't specify
        # a new picture. The picture shouldn't be overwritten by a blank
        try:
            self.add_test_picture_file()
            uploads_before = self.get_num_of_uploads()
            post_data = self.unchanged_post
            # post_data['picture'] = ''
            response = self.client.post(reverse('people:edit', args=self.test_pk1), post_data, follow=True)

            self.assertRedirects(response, reverse('people:detail', args=self.test_pk1))
            # test pic in response
            self.assertContains(response, 'test_pic1.jpg')
            self.run_test_uploaded_file(self.test_pk1)
            self.assertEqual(self.get_num_of_uploads(), uploads_before)

        finally:
            self.cleanup_test_files()

    def test_picture_clear(self):
        try:
            self.add_test_picture_file()
            uploads_before = self.get_num_of_uploads()
            post_data = self.unchanged_post
            post_data['picture-clear'] = 'on'
            response = self.client.post(reverse('people:edit', args=self.test_pk1), post_data, follow=True)

            self.assertRedirects(response, reverse('people:detail', args=self.test_pk1))
            # test pic not in response
            self.assertNotContains(response, 'test_pic1.jpg')
            # test blank in .db
            profile = models.Person.objects.get(pk=self.test_pk1)
            self.assertEqual(str(profile.picture), '')
            self.assertEqual(str(profile.thumbnail), '', 'Thumbnail not deleted when image cleared')
            # test pic still in file system
            self.assertEqual(self.get_num_of_uploads(), uploads_before)
            pic_path = os.path.join(base_settings.MEDIA_ROOT, 'people', 'profile_pictures', 'test_pic1.jpg')
            self.assertTrue(os.path.exists(pic_path),
                            'Picture not located on file system')

        finally:
            self.cleanup_test_files()

    def test_uploading_pre_existing_file(self):
        # ensure a duplicate upload isn't created
        try:
            self.add_test_picture_file()
            uploads_before = self.get_num_of_uploads()
            post_data = self.unchanged_post
            with open(self.test_pic1_path, 'rb') as file:
                file = file.read()
                test_image = SimpleUploadedFile('test_data/test_pic1.jpg', file, content_type='image')
                post_data['picture'] = test_image
                response = self.client.post(reverse('people:edit', args=self.test_pk1), post_data, follow=True)

            self.assertRedirects(response, reverse('people:detail', args=self.test_pk1))
            # test pic in response
            self.assertContains(response, 'test_pic1.jpg')
            self.run_test_uploaded_file(self.test_pk1)
            self.assertEqual(self.get_num_of_uploads(), uploads_before)

        finally:
            self.cleanup_test_files()

    def test_search(self):
        response = self.client.get(reverse('people:search') + '?search=Test')

        self.assertEqual(response.status_code, 200, 'People search GET request failed')
        self.assertContains(response, 'Test person 1')
        response = self.client.get(reverse('people:search') + '?search=Bad')
        self.assertContains(response, 'No search results')
