import os

from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from CE import models
from CE.Tests.test_base_class import CETestBaseClass


class NewCEPageTest(CETestBaseClass):

    # Basic functionality
    def test_new_CE_page_GET_response(self):
        # blank form should be returned
        response = self.client.get(reverse('CE:new'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('CE/new_CE.html')
        self.assertContains(response, 'Create a new CE')
        self.assertContains(response, '<form')
        self.assertContains(response, '<label for="id_title">CE title:</label>')

    def test_text_form_is_blank(self):
        response = self.client.get(reverse('CE:new'))
        self.assertNotContains(response, 'Phonetics written here')

    def test_redirects_to_new_CE_after_POST(self):
        response = self.client.post(reverse('CE:new'), self.new_post, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('CE/view_CE.html')
        self.assertRedirects(response, reverse('CE:view', args=self.new_ce_pk))

    def test_confirmation_message_after_POST(self):
        response = self.client.post(reverse('CE:new'), self.new_post, follow=True)
        self.assertContains(response, 'New CE created')

    def test_new_CE_Page_in_db_after_POST(self):
        self.client.post(reverse('CE:new'), self.new_post)

        # check ce exists in .db
        ce = models.CultureEvent.objects.get(pk=self.new_ce_pk)
        # check ce details in .db
        self.assertEqual(ce.title, self.new_post['title'], 'new CE title not correct')
        self.assertEqual(ce.description_plain_text, self.new_post['description_plain_text'],
                         'new CE description not correct')
        self.assertEqual(ce.last_modified_by, 'Tester',
                         'Last modified by not updated')

    def test_new_CE_page_invalid_POST_repeated_title_response(self):
        # Form should be show again with error message
        post_data = self.new_post
        post_data['title'] = models.CultureEvent.objects.get(pk=1).title
        response = self.client.post(reverse('CE:new'), post_data)

        self.assertContains(response, 'CE already exists')
        with self.assertRaises(models.CultureEvent.DoesNotExist):
            models.CultureEvent.objects.get(pk=self.new_ce_pk)

        # test that it's case insensitive
        post_data = self.new_post
        post_data['title'] = models.CultureEvent.objects.get(pk=1).title.lower()
        response = self.client.post(reverse('CE:new'), post_data)
        self.assertContains(response, 'CE already exists')

        post_data = self.new_post
        post_data['title'] = models.CultureEvent.objects.get(pk=1).title.upper()
        response = self.client.post(reverse('CE:new'), post_data)
        self.assertContains(response, 'CE already exists')

    def test_new_CE_page_invalid_POST_no_title_response(self):
        # Form should be shown again with error message
        # No extra CE should be added to .db
        post_data = self.new_post
        del post_data['title']
        response = self.client.post(reverse('CE:new'), post_data)
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(models.CultureEvent.DoesNotExist):
            models.CultureEvent.objects.get(pk=self.new_ce_pk)

    # Images
    def test_new_CE_page_saves_single_picture(self):
        try:
            post_data = self.new_post
            with open(self.test_pic1_path, 'rb') as file:
                file = file.read()
                test_image = SimpleUploadedFile('test_data/test_pic1.jpg', file, content_type='image')
                post_data['picture'] = test_image
                response = self.client.post(reverse('CE:new'), post_data)

            # test data correct in .db
            self.assertRedirects(response, reverse('CE:view', args=self.new_ce_pk))
            new_ce = models.CultureEvent.objects.get(pk=self.new_ce_pk)
            self.assertEqual(self.new_post['title'], new_ce.title, 'New CE title not correct')
            new_pic = models.Picture.objects.get(ce=new_ce)
            self.assertEqual('CultureEventFiles/{id}/images/test_pic1.jpg'.format(id=self.new_ce_pk),
                             str(new_pic.picture), 'New CE not saved to db')

            # test file uploaded to folder
            new_pic_folder = os.path.join(self.upload_folder, self.new_ce_pk, 'images')
            self.assertTrue(os.path.exists(new_pic_folder), 'upload folder doesn\'t exist')
            folder_contents = os.listdir(new_pic_folder)
            self.assertIn('test_pic1.jpg', folder_contents, 'Uploaded picture not in upload folder')
            # check smaller than 1Mb
            self.assertTrue(os.path.getsize(os.path.join(new_pic_folder, 'test_pic1.jpg')) < 1000000, 'picture too big')
            # check Foreign key is correct
            self.assertEqual(new_ce, new_pic.ce, 'Foreign key not correct')

            # check image displayed on view page
            response = self.client.get(reverse('CE:view', args=self.new_ce_pk))
            self.assertContains(response, 'Test CE')
            self.assertContains(response, '<div id="CE_pictures"')
            self.assertContains(response,
                                '<img src="/uploads/CultureEventFiles/%s/images/test_pic1.jpg' % self.new_ce_pk)
        finally:
            self.cleanup_test_files(int(self.new_ce_pk))

    # Texts
    def test_new_CE_page_can_save_text_with_audio(self):
        try:
            post_data = self.new_post
            post_data['text-0-phonetic_text'] = 'fʌni foᵘnɛtɪk sɪmbɔlz ŋ tʃ ʒ'
            post_data['text-0-orthographic_text'] = 'Orthograpic'
            post_data['text-TOTAL_FORMS'] = 1
            with open(self.test_audio1_path, 'rb') as file:
                file = file.read()
                test_audio = SimpleUploadedFile('test_data/test_audio1.mp3', file, content_type='audio')
                post_data['text-0-audio'] = test_audio
                response = self.client.post(reverse('CE:new'), post_data)

            # Test redirect
            self.assertRedirects(response, reverse('CE:view', args=self.new_ce_pk))
            # Test new CE contents in .db
            new_ce = models.CultureEvent.objects.get(pk=self.new_ce_pk)
            self.assertEqual(self.new_post['title'], new_ce.title, 'New CE data incorrect')
            # Test text model updated
            new_text = models.Text.objects.get(ce=new_ce)
            self.assertEqual('CultureEventFiles/{id}/audio/test_audio1.mp3'.format(id=self.new_ce_pk),
                             str(new_text.audio), 'New text not saved to db')
            # Test uploaded files in directory
            new_audio_folder = os.path.join(self.upload_folder, self.new_ce_pk, 'audio')
            self.assertTrue(os.path.exists(new_audio_folder), 'upload folder doesn\'t exist')
            folder_contents = os.listdir(new_audio_folder)
            self.assertIn('test_audio1.mp3', folder_contents, 'Uploaded audio not in upload folder')
            # check Foreign key is correct
            self.assertEqual(new_ce, new_text.ce, 'Foreign key not correct')
            self.assertEqual('fʌni foᵘnɛtɪk sɪmbɔlz ŋ tʃ ʒ', new_text.phonetic_text,
                             'Phonetics not correct')
            self.assertEqual('Orthograpic', new_text.orthographic_text, 'Orthography not correct')

            # check audio displayed on view page
            response = self.client.get(reverse('CE:view', args=self.new_ce_pk))
            self.assertContains(response, 'Test CE')
            self.assertContains(response,
                                '<audio controls> '
                                '<source src="/uploads/CultureEventFiles/%s/audio/test_audio1.mp3">'
                                '</audio>' % self.new_ce_pk)
        finally:
            self.cleanup_test_files(int(self.new_ce_pk))

    def test_can_add_single_text_if_phonetic_standard_missing(self):
        post_data = self.new_post
        post_data['text-TOTAL_FORMS'] = 1
        post_data['text-0-phonetic_text'] = 'Phonetics'
        post_data['text-0-orthographic_text'] = 'Orthographic'
        response = self.client.post(reverse('CE:new'), post_data)

        # test new CE added to .db
        self.assertRedirects(response, reverse('CE:view', args=self.new_ce_pk))
        new_ce = models.CultureEvent.objects.get(pk=self.new_ce_pk)
        self.assertEqual(post_data['title'], new_ce.title, 'New CE not saved to db')

        # test new text in .db
        texts = models.Text.objects.filter(ce=new_ce)
        self.assertEqual(len(texts), 1, 'New text not added')
        self.assertEqual(texts[0].orthographic_text, post_data['text-0-orthographic_text'])
        self.assertEqual(texts[0].phonetic_standard, '1', 'Text not marked as unchecked')
        self.assertEqual(texts[0].last_modified_by, 'Tester', 'User info not captured')

    def test_can_add_single_text(self):
        post_data = self.new_post
        post_data['text-TOTAL_FORMS'] = 1
        post_data['text-0-phonetic_text'] = 'phonetic'
        post_data['text-0-orthographic_text'] = 'orthographic'
        post_data['text-0-phonetic_standard'] = '1'
        response = self.client.post(reverse('CE:new'), post_data)

        self.assertRedirects(response, reverse('CE:view', args=self.new_ce_pk))
        new_ce = models.CultureEvent.objects.get(pk=self.new_ce_pk)
        self.assertEqual(post_data['title'], new_ce.title, 'New CE not saved to db')

        # check text in .db
        texts = models.Text.objects.filter(ce=new_ce)
        self.assertEqual(len(texts), 1, 'New text not added')
        self.assertEqual(texts[0].orthographic_text, post_data['text-0-orthographic_text'])
        self.assertEqual(texts[0].phonetic_standard, '1')

    def test_can_add_multiple_texts(self):
        post_data = self.new_post
        post_data['text-TOTAL_FORMS'] = 2
        post_data['text-0-phonetic_text'] = 'phonetic1'
        post_data['text-0-orthographic_text'] = 'orthographic1'
        post_data['text-0-phonetic_standard'] = '1'
        post_data['text-1-phonetic_text'] = 'phonetic2'
        post_data['text-1-orthographic_text'] = 'orthographic2'
        post_data['text-1-phonetic_standard'] = '1'
        response = self.client.post(reverse('CE:new'), post_data)

        self.assertRedirects(response, reverse('CE:view', args=self.new_ce_pk))
        new_ce = models.CultureEvent.objects.get(pk=self.new_ce_pk)
        self.assertEqual(post_data['title'], new_ce.title, 'New CE not saved to db')

        texts = models.Text.objects.filter(ce=new_ce)
        self.assertEqual(len(texts), 2, 'There aren\'t two texts in the db')
        self.assertEqual(texts[1].phonetic_text, post_data['text-1-phonetic_text'])
        self.assertEqual(texts[0].orthographic_text, post_data['text-0-orthographic_text'])
        self.assertEqual(texts[0].phonetic_standard, '1')

    def test_blank_text_not_saved(self):
        post_data = self.new_post
        post_data['text-TOTAL_FORMS'] = 1
        post_data['text-0-phonetic_text'] = ''
        post_data['text-0-orthographic_text'] = ''
        response = self.client.post(reverse('CE:new'), post_data)

        # test new CE in .db
        self.assertRedirects(response, reverse('CE:view', args=self.new_ce_pk))
        new_ce = models.CultureEvent.objects.get(pk=self.new_ce_pk)
        self.assertEqual('Test CE', new_ce.title, 'New CE not saved to db')

        # test no new text
        texts = models.Text.objects.filter(ce=new_ce)
        self.assertEqual(len(texts), 0, 'Blank text has been added')

    # Questions
    def test_single_question_submit(self):
        num_q = len(models.Question.objects.all())
        post_data = self.new_post
        post_data['question-0-question'] = 'Does this work?'
        post_data['question-0-answer'] = 'I hope so!'
        post_data['question-TOTAL_FORMS'] = 1
        response = self.client.post(reverse('CE:new'), post_data)
        self.assertRedirects(response, reverse('CE:view', args=self.new_ce_pk))
        self.assertEqual(len(models.Question.objects.all()), num_q + 1)
        q = models.Question.objects.filter(ce=self.new_ce_pk)
        self.assertEqual(q[0].question, post_data['question-0-question'])
        self.assertEqual(q[0].answer, post_data['question-0-answer'])
        self.assertEqual(q[0].asked_by, 'Tester')
        self.assertEqual(q[0].last_modified_by, 'Tester')

    def test_question_submit_without_answer(self):
        post_data = self.new_post
        post_data['question-0-question'] = 'Q1'
        post_data['question-0-answer'] = ''
        post_data['question-TOTAL_FORMS'] = 1
        self.client.post(reverse('CE:new'), post_data)

        # check contents of question in .db
        ce = models.CultureEvent.objects.get(pk=self.new_ce_pk)
        q = models.Question.objects.get(ce=ce)
        self.assertEqual(q.question, post_data['question-0-question'])
        self.assertEqual(q.answer, '')
        self.assertEqual(q.asked_by, 'Tester')
        self.assertEqual(q.last_modified_by, 'Tester')

    def test_multiple_question_submit(self):
        num_q = len(models.Question.objects.all())
        post_data = self.new_post
        post_data['question-TOTAL_FORMS'] = 3
        post_data['question-0-question'] = 'Q1'
        post_data['question-0-answer'] = 'A1'
        post_data['question-1-question'] = 'Q2'
        post_data['question-1-answer'] = 'A2'
        post_data['question-2-question'] = 'Q3'
        post_data['question-2-answer'] = 'A3'
        response = self.client.post(reverse('CE:new'), post_data)

        self.assertRedirects(response, reverse('CE:view', args=self.new_ce_pk))
        # test questions in .db
        q = models.Question.objects.all()
        self.assertEqual(len(models.Question.objects.all()), num_q + 3)

        # test content of questions
        ce = models.CultureEvent.objects.get(pk=self.new_ce_pk)
        q = models.Question.objects.filter(ce=ce)
        self.assertEqual(len(q), 3)
        for thing in q:
            self.assertTrue(thing.question.startswith('Q'))
            self.assertTrue(thing.answer.startswith('A'))
            self.assertEqual(thing.asked_by, 'Tester')
            self.assertEqual(thing.last_modified_by, 'Tester')

    def test_blank_questions_submitted(self):
        post_data = self.new_post
        post_data['question-TOTAL_FORMS'] = 2
        post_data['question-0-question'] = ''
        response = self.client.post(reverse('CE:new'), post_data)

        self.assertRedirects(response, reverse('CE:view', args=self.new_ce_pk))
        q = models.Question.objects.all()
        self.assertEqual(len(q), 3)

    # Tags
    def test_tags_added_to_db(self):
        post_data = self.new_post
        post_data['tags'] = 'taggie, 1-1'
        self.client.post(reverse('CE:new'), post_data)

        ce = models.CultureEvent.objects.get(pk=self.new_ce_pk)
        self.assertIn('taggie', str(ce.tags.all().values()))
        self.assertIn('1-1-geography-weather', str(ce.tags.all().values()))

        # test tag displayed on tag page
        response = self.client.get(reverse('CE:view_tag', kwargs={'slug': 'taggie'}))
        self.assertEqual(response.status_code, 200, 'Tag view page not showing')

    # Visits
    def test_can_add_multiple_visits(self):
        post_data = self.new_post
        post_data['visit-TOTAL_FORMS'] = 2
        post_data['visit-0-date'] = '2019-03-20'
        post_data['visit-0-nationals_present'] = 'Ulumo'
        post_data['visit-0-team_present'] = 'Steve'
        post_data['visit-1-date'] = '2019-03-21'
        post_data['visit-1-nationals_present'] = 'Kavaluku'
        post_data['visit-1-team_present'] = 'Rhett'
        response = self.client.post(reverse('CE:new'), post_data)

        # test ce in .db
        self.assertRedirects(response, reverse('CE:view', args=self.new_ce_pk))
        ce = models.CultureEvent.objects.get(pk=self.new_ce_pk)

        # test visits in .db
        visit = models.Visit.objects.filter(ce=ce)
        self.assertEqual(len(visit), 2)
        self.assertEqual(visit[0].team_present, 'Steve')
        self.assertEqual(visit[1].team_present, 'Rhett')

    def test_blank_visit(self):
        # shouldn't create a visit db row
        post_data = self.new_post
        post_data['visit-0-date'] = ''
        post_data['visit-0-nationals_present'] = ''
        post_data['visit-0-team_present'] = ''
        response = self.client.post(reverse('CE:new'), post_data)

        self.assertRedirects(response, reverse('CE:view', args=self.new_ce_pk))
        ce = models.CultureEvent.objects.get(pk=self.new_ce_pk)
        visit = models.Visit.objects.filter(ce=ce)
        self.assertEqual(len(visit), 0)
