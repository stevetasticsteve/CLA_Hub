import datetime
import os
import shutil

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from CE import models
from CE.Tests.test_base_class import CETestBaseClass


class TestEditPage(CETestBaseClass):
    def test_edit_page_GET_response(self):
        response = self.client.get(reverse('CE:edit', args=self.test_ce1_pk))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('CE/edit_CE.html')

    def test_CE_form_has_initial_data(self):
        response = self.client.get(reverse('CE:edit', args=self.test_ce1_pk))
        self.assertContains(response, '<form')
        # check form contents
        for data in self.test_data.values():
            # html doesn't render the valid for DA boolean, so skip it
            if not data:
                continue
            self.assertContains(response, data)

    def test_redirect_after_post(self):
        response = self.client.post(reverse('CE:edit', args=self.test_ce1_pk),
                                    data=self.standard_post, follow=True)
        self.assertRedirects(response, reverse('CE:view', args=self.test_ce1_pk))

    def test_number_of_CEs_the_same(self):
        num_CEs = len(models.CultureEvent.objects.all())
        self.client.post(reverse('CE:edit', args=self.test_ce1_pk),
                         data=self.standard_post, follow=True)
        self.assertEqual(len(models.CultureEvent.objects.all()), num_CEs)

    def test_CE_model_updated_correctly_after_POST(self):
        post_data = self.standard_post
        post_data['description_plain_text'] = 'A new description'
        self.client.post(reverse('CE:edit', args=self.test_ce1_pk), data=post_data, follow=True)

        ce = models.CultureEvent.objects.get(pk=self.test_ce1_pk)
        self.assertEqual('A new description', ce.description_plain_text)
        self.assertEqual(self.test_data['title'], ce.title)
        self.assertEqual(ce.pk, int(self.test_ce1_pk))

    def test_changing_CE_title(self):
        post_data = self.standard_post
        post_data['title'] = 'A new title'

        self.client.post(reverse('CE:edit', args=self.test_ce1_pk), data=post_data, follow=True)
        ce = models.CultureEvent.objects.get(pk=self.test_ce1_pk)
        self.assertEqual('A new title', ce.title)
        self.assertEqual(ce.pk, int(self.test_ce1_pk))

    def test_edit_title_to_existing_rejected(self):
        post_data = self.standard_post
        post_data['title'] = 'TestCE2'
        response = self.client.post(reverse('CE:edit', args=self.test_ce1_pk),
                                    data=post_data, follow=True)
        # assert title hasn't changed
        self.assertNotEqual(models.CultureEvent.objects.get(pk=self.test_ce1_pk).title,
                            'TestCE2')
        self.assertContains(response, 'CE already exists')

    def test_edit_single_text(self):
        post_data = self.standard_post
        post_data['text-0-phonetic_text'] = 'Changed'
        post_data['text-0-id'] = self.test_text1_pk
        post_data['text-0-ce'] = self.test_ce1_pk
        post_data['text-1-id'] = self.test_text2_pk
        post_data['text-1-ce'] = self.test_ce1_pk
        response = self.client.post(reverse('CE:edit', args=self.test_ce1_pk),
                                    data=post_data, follow=True)

        self.assertRedirects(response, reverse('CE:view', args=self.test_ce1_pk))
        self.assertEqual(models.Text.objects.get(pk=self.test_text1_pk).phonetic_text, 'Changed',
                         'Text 1 not updated on POST')
        self.assertEqual(models.Text.objects.get(pk=self.test_text2_pk).phonetic_text,
                         self.test_data['phonetic_text'], 'Text 2 mistakenly changed')

    def test_edit_second_text(self):
        post_data = self.standard_post
        post_data['text-1-phonetic_text'] = 'Changed'
        post_data['text-0-id'] = self.test_text1_pk
        post_data['text-0-ce'] = self.test_ce1_pk
        post_data['text-1-id'] = self.test_text2_pk
        post_data['text-1-ce'] = self.test_ce1_pk
        response = self.client.post(reverse('CE:edit', args=self.test_ce1_pk),
                                    data=post_data, follow=True)

        self.assertRedirects(response, reverse('CE:view', args=self.test_ce1_pk))
        self.assertEqual(models.Text.objects.get(pk=self.test_text2_pk).phonetic_text, 'Changed',
                         'Text 2 not updated on POST')
        self.assertEqual(models.Text.objects.get(pk=self.test_text1_pk).phonetic_text,
                         self.test_data['phonetic_text'], 'Text 1 mistakenly changed')

    def test_edit_both_texts(self):
        post_data = self.standard_post
        post_data['text-0-phonetic_text'] = 'Changed1'
        post_data['text-1-phonetic_text'] = 'Changed2'
        post_data['text-0-id'] = self.test_text1_pk
        post_data['text-0-ce'] = self.test_ce1_pk
        post_data['text-1-id'] = self.test_text2_pk
        post_data['text-1-ce'] = self.test_ce1_pk
        response = self.client.post(reverse('CE:edit', args=self.test_ce1_pk),
                                    data=post_data, follow=True)

        self.assertRedirects(response, reverse('CE:view', args=self.test_ce1_pk))
        self.assertEqual(models.Text.objects.get(pk=self.test_text1_pk).phonetic_text, 'Changed1',
                         'Text 1 not updated on POST')
        self.assertEqual(models.Text.objects.get(pk=self.test_text2_pk).phonetic_text, 'Changed2',
                         'Text 2 not updated on POST')

    def test_user_adds_empty_text(self):
        # ensure blank formsets are rejected
        post_data = self.standard_post
        post_data['text-TOTAL_FORMS'] = 3
        post_data['text-0-id'] = self.test_text1_pk
        post_data['text-0-ce'] = self.test_ce1_pk
        post_data['text-1-id'] = self.test_text2_pk
        post_data['text-1-ce'] = self.test_ce1_pk
        response = self.client.post(reverse('CE:edit', args=self.test_ce1_pk), data=post_data, follow=True)

        # test there is no extra text in DB
        self.assertRedirects(response, reverse('CE:view', args=self.test_ce1_pk))
        extra_pk = str(int(self.test_text2_pk) + 1)
        with self.assertRaises(models.Text.DoesNotExist):
            models.Text.objects.get(pk=extra_pk)

        # test remaining texts are unchanged
        self.assertEqual(models.Text.objects.get(pk=self.test_text1_pk).phonetic_text,
                         self.test_data['phonetic_text'])
        self.assertEqual(models.Text.objects.get(pk=self.test_text2_pk).phonetic_text,
                         self.test_data['phonetic_text'])

    def test_user_adds_new_text(self):
        num_texts = len(models.Text.objects.all())
        post_data = self.standard_post
        post_data['text-TOTAL_FORMS'] = 3
        post_data['text-0-id'] = self.test_text1_pk
        post_data['text-0-ce'] = self.test_ce1_pk
        post_data['text-1-id'] = self.test_text2_pk
        post_data['text-1-ce'] = self.test_ce1_pk
        post_data['text-2-phonetic_text'] = 'New'
        response = self.client.post(reverse('CE:edit', args=self.test_ce1_pk),
                                    data=post_data, follow=True)

        new_text_pk = str(int(self.test_text2_pk) + 1)
        self.assertRedirects(response, reverse('CE:view', args=self.test_ce1_pk))
        self.assertEqual(len(models.Text.objects.all()), num_texts + 1)
        self.assertEqual(models.Text.objects.get(pk=new_text_pk).phonetic_text, 'New')

    def test_user_can_add_audio(self):
        num_texts = len(models.Text.objects.all())
        try:
            with open(self.test_audio1_path, 'rb') as file:
                file = file.read()
                test_audio = SimpleUploadedFile('test_data/test_audio1.mp3',
                                                file, content_type='audio')
            post_data = self.standard_post
            post_data['text-0-id'] = self.test_text1_pk
            post_data['text-0-ce'] = self.test_ce1_pk
            post_data['text-1-id'] = self.test_text2_pk
            post_data['text-1-ce'] = self.test_ce1_pk
            post_data['text-0-audio'] = test_audio
            response = self.client.post(reverse('CE:edit', args=self.test_ce1_pk),
                                        data=post_data, follow=True)

            # test audio in db
            self.assertRedirects(response, reverse('CE:view', args=self.test_ce1_pk))
            self.assertEqual(len(models.Text.objects.all()), num_texts)
            self.assertEqual(models.Text.objects.get(pk=self.test_text1_pk).audio,
                             'CultureEventFiles/{id}/audio/test_audio1.mp3'.format(id=self.test_ce1_pk))

            # test mp3 in uploads
            new_audio_folder = os.path.join(self.upload_folder, self.test_ce1_pk, 'audio')
            self.assertTrue(os.path.exists(new_audio_folder), 'upload folder doesn\'t exist')
            folder_contents = os.listdir(new_audio_folder)
            self.assertIn('test_audio1.mp3', folder_contents, 'Uploaded audio not in upload folder')

            # test displayed on view page
            response = self.client.get(reverse('CE:view', args=self.test_ce1_pk))
            self.assertContains(response,
                                '<audio controls> <source src="/uploads/CultureEventFiles/%s/'
                                'audio/test_audio1.mp3"></audio>' % self.test_ce1_pk)

        finally:
            self.cleanup_test_files(int(self.test_ce1_pk))

    def test_user_can_change_audio(self):
        num_texts = len(models.Text.objects.all())
        try:
            # add audio file to uploads
            test_folder = os.path.join(self.upload_folder, self.test_ce1_pk, 'audio')
            try:
                os.makedirs(test_folder)
            except FileExistsError:  # don't need to create it
                pass
            shutil.copy(self.test_audio1_path, test_folder)
            # add audio to test text
            text = models.Text.objects.get(pk=self.test_text1_pk)
            text.audio = 'CultureEventFiles/{id}/audio/test_audio1.mp3'.format(id=self.test_ce1_pk)
            text.save()
            with open(self.test_audio2_path, 'rb') as file:
                file = file.read()
                test_audio = SimpleUploadedFile('test_data/test_audio2.mp3',
                                                file, content_type='audio')
            post_data = self.standard_post
            post_data['text-0-id'] = self.test_text1_pk
            post_data['text-0-ce'] = self.test_ce1_pk
            post_data['text-1-id'] = self.test_text2_pk
            post_data['text-1-ce'] = self.test_ce1_pk
            post_data['text-0-audio'] = test_audio
            response = self.client.post(reverse('CE:edit', args=self.test_ce1_pk),
                                        data=post_data, follow=True)

            # test audio in db
            self.assertRedirects(response, reverse('CE:view', args=self.test_ce1_pk))
            self.assertEqual(len(models.Text.objects.all()), num_texts)
            self.assertEqual(models.Text.objects.get(pk=self.test_text1_pk).audio,
                             'CultureEventFiles/{id}/audio/test_audio2.mp3'.format(id=self.test_ce1_pk))

            # test mp3 in uploads
            new_audio_folder = os.path.join(self.upload_folder, self.test_ce1_pk, 'audio')
            self.assertTrue(os.path.exists(new_audio_folder), 'upload folder doesn\'t exist')
            folder_contents = os.listdir(new_audio_folder)
            self.assertIn('test_audio2.mp3', folder_contents, 'Uploaded audio not in upload folder')

            # test displayed on view page
            response = self.client.get(reverse('CE:view', args=self.test_ce1_pk))
            self.assertContains(response,
                                '<audio controls> <source src="/uploads/CultureEventFiles/%s/'
                                'audio/test_audio2.mp3"></audio>' % self.test_ce1_pk)

        finally:
            self.cleanup_test_files(int(self.test_ce1_pk))

    def test_can_edit_first_visit_form(self):
        num_visits = len(models.Visit.objects.all())
        post_data = self.standard_post
        post_data['visit-0-team_present'] = 'Changed'
        post_data['visit-0-nationals_present'] = 'Changed'
        post_data['visit-0-date'] = '2019-10-11'
        post_data['visit-TOTAL_FORMS'] = 1
        post_data['visit-0-id'] = self.test_visit_pk
        post_data['visit-0-ce'] = self.test_ce1_pk
        response = self.client.post(reverse('CE:edit', args=self.test_ce1_pk),
                                    data=post_data, follow=True)

        self.assertRedirects(response, reverse('CE:view', args=self.test_ce1_pk))
        self.assertEqual(len(models.Visit.objects.all()), num_visits)
        self.assertEqual(models.Visit.objects.get(pk=self.test_visit_pk).nationals_present, 'Changed',
                         'Visit 1 not updated on POST')
        self.assertEqual(models.Visit.objects.get(pk=self.test_visit_pk).team_present, 'Changed',
                         'visit 1 not updated on POST')
        self.assertEqual(models.Visit.objects.get(pk=self.test_visit_pk).date, datetime.date(2019, 10, 11),
                         'visit 1 not updated on POST')

    def test_can_add_picture(self):
        try:
            before_uploads = self.get_number_of_uploaded_images(self.test_ce1_pk)
            post_data = self.standard_post
            with open(self.test_pic1_path, 'rb') as file:
                file = file.read()
                picture = SimpleUploadedFile(name='test_pic1.jpg', content=file, content_type='image')
                post_data['picture'] = picture
                response = self.client.post(reverse('CE:edit', args=self.test_ce1_pk),
                                            data=post_data, follow=True)

            self.assertRedirects(response, reverse('CE:view', args=self.test_ce1_pk))
            # test pic in .db
            picture = models.Picture.objects.filter(ce=self.test_ce1_pk)
            self.assertEqual(len(picture), 1)
            self.assertEqual(str(picture[0].picture), 'CultureEventFiles/%s/images/test_pic1.jpg' % self.test_ce1_pk)
            # test pic on file system
            self.assertEqual(self.get_number_of_uploaded_images(self.test_ce1_pk), before_uploads + 1)
            self.assertTrue(os.path.exists(os.path.join(self.test_ce1_upload_path, 'images', 'test_pic1.jpg')))
        finally:
            self.cleanup_test_files(self.test_ce1_pk)

    def test_preexisting_pic_ignored(self):
        try:
            with open(self.test_pic1_path, 'rb') as file:
                file = file.read()
                picture = SimpleUploadedFile(name='test_pic1.jpg', content=file, content_type='image')
                ce = models.CultureEvent.objects.get(pk=self.test_ce1_pk)
                new_pic = models.Picture(ce=ce,
                                         picture=picture)
                new_pic.save()

            post_data = self.standard_post
            with open(self.test_pic1_path, 'rb') as file:
                file = file.read()
                picture = SimpleUploadedFile(name='test_pic1.jpg', content=file, content_type='image')
                post_data['picture'] = picture
                response = self.client.post(reverse('CE:edit', args=self.test_ce1_pk),
                                            data=post_data, follow=True)

            self.assertRedirects(response, reverse('CE:view', args=self.test_ce1_pk))
            # test pic in .db
            picture = models.Picture.objects.filter(ce=self.test_ce1_pk)
            # test no extra files created in .db
            self.assertEqual(len(picture), 1, 'Duplicated uploaded files are being created')

        finally:
            self.cleanup_test_files(self.test_ce1_pk)

    def test_can_edit_question(self):
        post_data = self.standard_post
        post_data['question-0-question'] = 'NewQuestion'
        response = self.client.post(reverse('CE:edit', args=self.test_ce1_pk),
                                    data=post_data, follow=True)

        self.assertRedirects(response, reverse('CE:view', args=self.test_ce1_pk))
        self.assertContains(response, 'NewQuestion')
        questions = models.Question.objects.filter(ce_id=self.test_ce1_pk)
        self.assertEqual(questions[0].question, 'NewQuestion')
        self.assertEqual(len(questions), 1)

    def test_can_edit_answer(self):
        post_data = self.standard_post
        post_data['question-0-answer'] = 'NewAnswer'
        response = self.client.post(reverse('CE:edit', args=self.test_ce1_pk),
                                    data=post_data, follow=True)

        self.assertRedirects(response, reverse('CE:view', args=self.test_ce1_pk))
        self.assertContains(response, 'NewAnswer')
        questions = models.Question.objects.filter(ce_id=self.test_ce1_pk)
        self.assertEqual(questions[0].answer, 'NewAnswer')
        self.assertEqual(len(questions), 1)

    def test_can_add_unanswered_question(self):
        post_data = self.standard_post
        post_data['question-1-question'] = 'NewQuestion'
        post_data['question-1-ce'] = self.test_ce1_pk
        post_data['question-1-id'] = 3
        post_data['question-1-answer'] = ''
        post_data['question-TOTAL_FORMS'] = 2
        response = self.client.post(reverse('CE:edit', args=self.test_ce1_pk),
                                    data=post_data, follow=True)

        self.assertRedirects(response, reverse('CE:view', args=self.test_ce1_pk))
        self.assertContains(response, 'NewQuestion')
        self.assertContains(response, self.test_data['question'])
        questions = models.Question.objects.filter(ce_id=self.test_ce1_pk)
        self.assertEqual(len(questions), 2)
        self.assertEqual((questions[0].question), self.test_data['question'])
        self.assertEqual(questions[1].question, 'NewQuestion')
        self.assertEqual(questions[1].answer, '')

    def test_added_question_has_asked_by(self):
        post_data = self.standard_post
        post_data['question-1-question'] = 'NewQuestion'
        post_data['question-1-ce'] = self.test_ce1_pk
        post_data['question-1-id'] = 3
        post_data['question-1-answer'] = ''
        post_data['question-TOTAL_FORMS'] = 2
        self.client.post(reverse('CE:edit', args=self.test_ce1_pk),
                         data=post_data, follow=True)

        question = models.Question.objects.filter(ce_id=self.test_ce1_pk)[1]
        self.assertEqual(question.last_modified_by, 'Tester')
        self.assertEqual(question.question, 'NewQuestion')
        self.assertEqual(question.asked_by, 'Tester')
