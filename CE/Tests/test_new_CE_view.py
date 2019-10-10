from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core import exceptions
from CE import models

import os

class NewCEPageTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        credentials = User(username='Tester')
        credentials.set_password('secure_password')
        credentials.save()

    def setUp(self):
        self.client.login(username='Tester', password='secure_password')
        # have one model previously in .db
        ce = models.CultureEvent(title='Example CE1',
                                 description_plain_text='A culture event happened',
                                 differences='Last time it was different')
        ce.save()
        participants = models.ParticipationModel(date='2019-08-05',
                                                 team_participants='Steve',
                                                 national_participants='Ulumo',
                                                 ce=ce)
        participants.save()
        texts = models.TextModel(ce=ce,
                                 phonetic_text='Phonetics written here',
                                 valid_for_DA=False)
        texts.save()

    def full_valid_POST(self, follow):
        posted_data = {
            'title': 'A test CE',
            'description_plain_text': 'I\'m testing this CE',
            'tags': 'Some tags written here 1-1',
            'interpretation': 'I feel good about this',
            'variation': 'last time it was different',
            'participants-0-date': '2019-04-20',
            'participants-0-national_participants': 'Ulumo',
            'participants-0-team_participants': 'Rhett',
            'text-TOTAL_FORMS': 0,
            'text-INITIAL_FORMS': 0,
            'question-TOTAL_FORMS': 0,
            'question-INITIAL_FORMS': 0,
            'participants-TOTAL_FORMS': 1,
            'participants-INITIAL_FORMS': 1
        }
        response = self.client.post(reverse('CE:new'), posted_data , follow=follow)

        return response, posted_data

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

    def test_redirect_after_POST(self):
        response, _ = self.full_valid_POST(follow=False)
        self.assertTemplateUsed('CE/new_CE.html')
        self.assertEqual(response.status_code, 302)

    def test_redirects_to_new_CE_after_POST(self):
        response, _ = self.full_valid_POST(follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('CE/view_CE.html')
        self.assertRedirects(response, '/CE/2')

    def test_confirmation_message_after_POST(self):
        response, _ = self.full_valid_POST(follow=True)
        self.assertContains(response, 'New CE created')

    def test_new_CE_Page_in_db_after_POST(self):
        response, posted_data = self.full_valid_POST(follow=True)
        ce = models.CultureEvent.objects.get(pk=2)
        self.assertEqual(ce.title, posted_data['title'], 'new CE title not correct')
        self.assertEqual(ce.description_plain_text, posted_data['description_plain_text'],
                         'new CE description not correct')
        self.assertEqual(ce.last_modified_by, 'Tester',
                         'Last modified by not updated')
        self.assertEqual(len(models.TextModel.objects.all()), 1, 'A blank Text was added')

    def test_new_CE_page_invalid_POST_repeated_title_response(self):
        # Form should be show again with error message
        response = self.client.post(reverse('CE:new'), {
            'title': 'Example CE1',
            'description_plain_text': 'I\'m testing this CE',
            'text-TOTAL_FORMS': 0,
            'text-INITIAL_FORMS': 0,
            'question-TOTAL_FORMS': 0,
            'question-INITIAL_FORMS': 0,
            'participants-TOTAL_FORMS': 1,
            'participants-INITIAL_FORMS': 1
        }, follow=True)
        self.assertContains(response, 'CE already exists')
        with self.assertRaises(models.CultureEvent.DoesNotExist):
            models.CultureEvent.objects.get(pk=2)

    def test_new_CE_page_invalid_POST_no_title_response(self):
        # Form should be shown again with error message
        # No extra CE should be added to .db
        response = self.client.post(reverse('CE:new'), {
            'description_plain_text': 'I\'m testing this CE',
            'text-TOTAL_FORMS': 0,
            'text-INITIAL_FORMS': 0,
            'question-TOTAL_FORMS': 0,
            'question-INITIAL_FORMS': 0,
            'participants-TOTAL_FORMS': 1,
            'participants-INITIAL_FORMS': 1
        }, follow=True)
        self.assertEqual(response.status_code, 200)
        with self.assertRaises(models.CultureEvent.DoesNotExist):
            models.CultureEvent.objects.get(pk=2)

    def test_new_CE_page_saves_single_picture(self):
        # todo refactor - probably as new class. Extensive set up and tear down neccesarry as uploads go into project dir
        # clean up if existing test failed and left a file there
        if os.path.exists('uploads/CultureEventFiles/2/images/test_pic1.jpg'):
            os.remove('uploads/CultureEventFiles/2/images/test_pic1.jpg')
        with open('CLAHub/assets/test_data/test_pic1.JPG', 'rb') as file:
            file = file.read()
            test_image = SimpleUploadedFile('test_data/test_pic1.JPG', file, content_type='image')
            response = self.client.post(reverse('CE:new'), {'title': 'Test CE',
                                                            'participants-0-date': '2019-03-20',
                                                            'participants-0-national_participants': 'Ulumo',
                                                            'participants-0-team_participants': 'Philip',
                                                            'picture': test_image,
                                                            'text-TOTAL_FORMS': 0,
                                                            'text-INITIAL_FORMS': 0,
                                                            'question-TOTAL_FORMS': 0,
                                                            'question-INITIAL_FORMS': 0,
                                                            'participants-TOTAL_FORMS': 1,
                                                            'participants-INITIAL_FORMS': 1
                                                            })
        self.assertRedirects(response, '/CE/2')
        new_ce = models.CultureEvent.objects.get(pk=2)
        self.assertEqual('Test CE', new_ce.title, 'New CE not saved to db')
        new_pic = models.PictureModel.objects.get(ce=new_ce)
        self.assertEqual('CultureEventFiles/2/images/test_pic1.jpg',
                         str(new_pic.picture), 'New CE not saved to db')

        self.assertTrue(os.path.exists('uploads/CultureEventFiles/2/images'), 'upload folder doesn\'t exist')
        folder_contents = os.listdir('uploads/CultureEventFiles/2/images')
        self.assertIn('test_pic1.jpg', folder_contents, 'Uploaded picture not in upload folder')
        # check smaller than 1Mb
        self.assertTrue(os.path.getsize('uploads/CultureEventFiles/2/images/test_pic1.jpg') < 1000000, 'picture too big')
        # check Foreign key is correct
        self.assertEqual(new_ce, new_pic.ce, 'Foreign key not correct')

        # check image displayed on view page
        response = self.client.get(reverse('CE:view', args='2'))
        self.assertContains(response, 'Test CE')
        self.assertContains(response, '<div id="carouselExampleIndicators"')
        self.assertContains(response, '<img src="/uploads/CultureEventFiles/2/images/test_pic1.jpg')

        # clean up after test - test uploads go onto actual file system program uses
        if len(folder_contents) == 1:
            # no user pictures, folder was created for test
            os.remove('uploads/CultureEventFiles/2/images/test_pic1.jpg')
            os.removedirs('uploads/CultureEventFiles/2/images')
        elif len(folder_contents) > 1:
            # users have uploaded pictures themselves
            os.remove('uploads/CultureEventFiles/2/images/test_pic1.jpg')

    def test_new_CE_page_can_save_text_and_audio(self):
        # clean up if existing test failed and left a file there
        if os.path.exists('uploads/CultureEventFiles/2/audio/test_audio1.mp3'):
            os.remove('uploads/CultureEventFiles/2/audio/test_audio1.mp3')
        test_phonetics = 'fʌni foᵘnɛtɪk sɪmbɔlz ŋ tʃ ʒ'
        test_orthography = 'orthography'
        with open('CLAHub/assets/test_data/test_audio1.mp3', 'rb') as file:
            file = file.read()
            test_audio = SimpleUploadedFile('test_data/test_audio1.mp3', file, content_type='audio')
            response = self.client.post(reverse('CE:new'), {'title': 'Test CE',
                                                            'participants-0-date': '2019-03-20',
                                                            'participants-0-national_participants': 'Ulumo',
                                                            'participants-0-team_participants': 'Philip',
                                                            'text-0-phonetic_text': test_phonetics,
                                                            'text-0-orthographic_text': test_orthography,
                                                            'text-0-phonetic_standard': '1',
                                                            'text-0-audio': test_audio,
                                                            'text-0-valid_for_DA': False,
                                                            'text-0-discourse_type': '',
                                                            'text-TOTAL_FORMS': 1,
                                                            'text-INITIAL_FORMS': 0,
                                                            'question-TOTAL_FORMS': 0,
                                                            'question-INITIAL_FORMS': 0,
                                                            'participants-TOTAL_FORMS': 1,
                                                            'participants-INITIAL_FORMS': 1
                                                            })
        self.assertRedirects(response, '/CE/2')
        new_ce = models.CultureEvent.objects.get(pk=2)
        self.assertEqual('Test CE', new_ce.title, 'New CE not saved to db')
        new_text = models.TextModel.objects.get(ce=new_ce)
        self.assertEqual('CultureEventFiles/2/audio/test_audio1.mp3',
                         str(new_text.audio), 'New text not saved to db')

        self.assertTrue(os.path.exists('uploads/CultureEventFiles/2/audio'), 'upload folder doesn\'t exist')
        folder_contents = os.listdir('uploads/CultureEventFiles/2/audio')
        self.assertIn('test_audio1.mp3', folder_contents, 'Uploaded audio not in upload folder')
        # check Foreign key is correct
        self.assertEqual(new_ce, new_text.ce, 'Foreign key not correct')
        self.assertEqual(test_phonetics, new_text.phonetic_text, 'Phonetics not correct')
        self.assertEqual(test_orthography, new_text.orthographic_text, 'Orthography not correct')

        # check audio displayed on view page
        response = self.client.get(reverse('CE:view', args='2'))
        self.assertContains(response, 'Test CE')
        self.assertContains(response,
                            '<audio controls> <source src="/uploads/CultureEventFiles/2/audio/test_audio1.mp3"></audio>')
        # clean up after test - test uploads go onto actual file system program uses
        if len(folder_contents) == 1:
            # no user audio, folder was created for test
            os.remove('uploads/CultureEventFiles/2/audio/test_audio1.mp3')
            os.removedirs('uploads/CultureEventFiles/2/audio')
        elif len(folder_contents) > 1:
            # users have uploaded pictures themselves
            os.remove('uploads/CultureEventFiles/2/audio/test_audio1.mp3')

    def test_can_add_single_text_if_phonetic_standard_missing(self):
        response = self.client.post(reverse('CE:new'), {'title': 'Test CE',
                                                        'participants-0-date': '2019-03-20',
                                                        'participants-0-national_participants': 'Ulumo',
                                                        'participants-0-team_participants': 'Philip',
                                                        'text-0-phonetic_text': 'Wam',
                                                        'text-0-orthographic_text': 'Bam',
                                                        'text-0-phonetic_standard': '1',
                                                        'text-TOTAL_FORMS': 1,
                                                        'text-INITIAL_FORMS': 0,
                                                        'question-TOTAL_FORMS': 0,
                                                        'question-INITIAL_FORMS': 0,
                                                        'participants-TOTAL_FORMS': 1,
                                                        'participants-INITIAL_FORMS': 1
                                                        })

        self.assertRedirects(response, '/CE/2')
        new_ce = models.CultureEvent.objects.get(pk=2)
        self.assertEqual('Test CE', new_ce.title, 'New CE not saved to db')

        texts = models.TextModel.objects.filter(ce=new_ce)
        self.assertEqual(len(texts), 1, 'New text not added')
        self.assertEqual(texts[0].orthographic_text, 'Bam')
        self.assertEqual(texts[0].phonetic_standard, '1')

    def test_can_add_single_text(self):
        response = self.client.post(reverse('CE:new'), {'title': 'Test CE',
                                                        'participants-0-date': '2019-03-20',
                                                        'participants-0-national_participants': 'Ulumo',
                                                        'participants-0-team_participants': 'Philip',
                                                        'text-0-phonetic_text': 'Wam',
                                                        'text-0-orthographic_text': 'Bam',
                                                        'text-0-phonetic_standard': '1',
                                                        'text-0-valid_for_DA': False,
                                                        'text-0-discourse_type': '',
                                                        'text-TOTAL_FORMS': 1,
                                                        'text-INITIAL_FORMS': 0,
                                                        'question-TOTAL_FORMS': 0,
                                                        'question-INITIAL_FORMS': 0,
                                                        'participants-TOTAL_FORMS': 1,
                                                        'participants-INITIAL_FORMS': 1
                                                        })
        self.assertRedirects(response, '/CE/2')
        new_ce = models.CultureEvent.objects.get(pk=2)
        self.assertEqual('Test CE', new_ce.title, 'New CE not saved to db')

        texts = models.TextModel.objects.filter(ce=new_ce)
        self.assertEqual(len(texts), 1, 'New text not added')
        self.assertEqual(texts[0].orthographic_text, 'Bam')
        self.assertEqual(texts[0].phonetic_standard, '1')

    def test_can_add_multiple_texts(self):
        response = self.client.post(reverse('CE:new'), {'title': 'Test CE',
                                                        'participants-0-date': '2019-03-20',
                                                        'participants-0-national_participants': 'Ulumo',
                                                        'participants-0-team_participants': 'Philip',
                                                        'text-0-phonetic_text': 'Wam',
                                                        'text-0-orthographic_text': 'Bam',
                                                        'text-0-phonetic_standard': '1',
                                                        'text-0-valid_for_DA': False,
                                                        'text-0-discourse_type': '',
                                                        'text-1-phonetic_text': 'number 2',
                                                        'text-1-orthographic_text': 'second',
                                                        'text-1-phonetic_standard': '2',
                                                        'text-1-valid_for_DA': False,
                                                        'text-1-discourse_type': '1',
                                                        'text-TOTAL_FORMS': 2,
                                                        'text-INITIAL_FORMS': 0,
                                                        'question-TOTAL_FORMS': 0,
                                                        'question-INITIAL_FORMS': 0,
                                                        'participants-TOTAL_FORMS': 1,
                                                        'participants-INITIAL_FORMS': 1
                                                        })
        self.assertRedirects(response, '/CE/2')
        new_ce = models.CultureEvent.objects.get(pk=2)
        self.assertEqual('Test CE', new_ce.title, 'New CE not saved to db')

        texts = models.TextModel.objects.filter(ce=new_ce)
        self.assertEqual(len(texts), 2, 'There aren\'t two texts in the db')
        self.assertEqual(texts[1].phonetic_text, 'number 2')
        self.assertEqual(texts[0].orthographic_text, 'Bam')
        self.assertEqual(texts[0].phonetic_standard, '1')

    def test_blank_text_not_saved(self):
        response = self.client.post(reverse('CE:new'), {'title': 'Test CE',
                                                        'participants-0-date': '2019-03-20',
                                                        'participants-0-national_participants': 'Ulumo',
                                                        'participants-0-team_participants': 'Philip',
                                                        'text-0-phonetic_text': '',
                                                        'text-0-orthographic_text': '',
                                                        'text-0-phonetic_standard': '',
                                                        'text-0-valid_for_DA': False,
                                                        'text-0-discourse_type': '',
                                                        'text-TOTAL_FORMS': 1,
                                                        'text-INITIAL_FORMS': 0,
                                                        'question-TOTAL_FORMS': 0,
                                                        'question-INITIAL_FORMS': 0,
                                                        'participants-TOTAL_FORMS': 1,
                                                        'participants-INITIAL_FORMS': 1
                                                        })
        self.assertRedirects(response, '/CE/2')
        new_ce = models.CultureEvent.objects.get(pk=2)
        self.assertEqual('Test CE', new_ce.title, 'New CE not saved to db')

        texts = models.TextModel.objects.filter(ce=new_ce)
        self.assertEqual(len(texts), 0, 'Blank text has been added')

    def test_single_question_submit(self):
        question = 'Does this work?'
        answer = 'I hope so!'
        response = self.client.post(reverse('CE:new'), {'title': 'Test CE',
                                                            'participants-0-date': '2019-03-20',
                                                            'participants-0-national_participants': 'Ulumo',
                                                            'participants-0-team_participants': 'Philip',
                                                            'text-TOTAL_FORMS': 0,
                                                            'text-INITIAL_FORMS': 0,
                                                            'question-TOTAL_FORMS': 1,
                                                            'question-INITIAL_FORMS': 0,
                                                            'question-0-question': question,
                                                            'question-0-answer': answer,
                                                            'participants-TOTAL_FORMS': 1,
                                                            'participants-INITIAL_FORMS': 1
                                                            })
        self.assertRedirects(response, '/CE/2')
        q = models.QuestionModel.objects.all()
        self.assertEqual(len(q), 1)
        self.assertEqual(q[0].question, question)
        self.assertEqual(q[0].answer, answer)
        self.assertEqual(q[0].asked_by, 'Tester')
        self.assertEqual(q[0].last_modified_by, 'Tester')

    def test_incomplete_question_sumbit(self):
        question = 'Does this work?'
        response = self.client.post(reverse('CE:new'), {'title': 'Test CE',
                                                        'participants-0-date': '2019-03-20',
                                                        'participants-0-national_participants': 'Ulumo',
                                                        'participants-0-team_participants': 'Philip',
                                                        'text-TOTAL_FORMS': 0,
                                                        'text-INITIAL_FORMS': 0,
                                                        'question-TOTAL_FORMS': 1,
                                                        'question-INITIAL_FORMS': 0,
                                                        'question-0-question': question,
                                                        'participants-TOTAL_FORMS': 1,
                                                        'participants-INITIAL_FORMS': 1
                                                        })
        self.assertRedirects(response, '/CE/2')
        q = models.QuestionModel.objects.all()
        self.assertEqual(len(q), 1)
        self.assertEqual(q[0].question, question)
        self.assertEqual(q[0].answer, '')
        self.assertEqual(q[0].asked_by, 'Tester')
        self.assertEqual(q[0].last_modified_by, 'Tester')

    def test_multiple_question_submit(self):
        question = 'Does this work?'
        answer = 'I hope so!'
        response = self.client.post(reverse('CE:new'), {'title': 'Test CE',
                                                        'participants-0-date': '2019-03-20',
                                                        'participants-0-national_participants': 'Ulumo',
                                                        'participants-0-team_participants': 'Philip',
                                                        'text-TOTAL_FORMS': 0,
                                                        'text-INITIAL_FORMS': 0,
                                                        'question-TOTAL_FORMS': 3,
                                                        'question-INITIAL_FORMS': 0,
                                                        'question-0-question': question,
                                                        'question-0-answer': answer,
                                                        'question-1-question': question,
                                                        'question-1-answer': answer,
                                                        'question-2-question': question,
                                                        'question-2-answer': answer,
                                                        'participants-TOTAL_FORMS': 1,
                                                        'participants-INITIAL_FORMS': 1
                                                        })
        self.assertRedirects(response, '/CE/2')
        q = models.QuestionModel.objects.all()
        self.assertEqual(len(q), 3)
        for thing in q:
            self.assertEqual(thing.question, question)
            self.assertEqual(thing.answer, answer)
            self.assertEqual(thing.asked_by, 'Tester')
            self.assertEqual(thing.last_modified_by, 'Tester')

    def test_blank_questions_submitted(self):
        response = self.client.post(reverse('CE:new'), {'title': 'Test CE',
                                                        'participants-0-date': '2019-03-20',
                                                        'participants-0-national_participants': 'Ulumo',
                                                        'participants-0-team_participants': 'Philip',
                                                        'text-TOTAL_FORMS': 0,
                                                        'text-INITIAL_FORMS': 0,
                                                        'question-TOTAL_FORMS': 2,
                                                        'question-INITIAL_FORMS': 0,
                                                        'participants-TOTAL_FORMS': 1,
                                                        'participants-INITIAL_FORMS': 1
                                                        })
        self.assertRedirects(response, '/CE/2')
        q = models.QuestionModel.objects.all()
        self.assertEqual(len(q), 0)

    def test_tags_added_to_db(self):
        self.full_valid_POST(follow=True)
        ce = models.CultureEvent.objects.get(pk=2)
        self.assertIn('Some', str(ce.tags.all().values()))
        self.assertIn('1-1-geography-weather', str(ce.tags.all().values()))
        response = self.client.get(reverse('CE:view_tag', kwargs={'slug':'here'}))
        self.assertEqual(response.status_code, 200, 'Tag view page not showing')

    def test_multiple_participations(self):
        response = self.client.post(reverse('CE:new'), {'title': 'Test CE',
                                                        'participants-0-date': '2019-03-20',
                                                        'participants-0-national_participants': 'Ulumo',
                                                        'participants-0-team_participants': 'Philip',
                                                        'participants-1-date': '2019-03-21',
                                                        'participants-1-national_participants': 'Kavaluku',
                                                        'participants-1-team_participants': 'Steve',
                                                        'text-TOTAL_FORMS': 0,
                                                        'text-INITIAL_FORMS': 0,
                                                        'question-TOTAL_FORMS': 0,
                                                        'question-INITIAL_FORMS': 0,
                                                        'participants-TOTAL_FORMS': 2,
                                                        'participants-INITIAL_FORMS': 0
                                                        })
        self.assertRedirects(response, '/CE/2')
        ce = models.CultureEvent.objects.get(pk=2)
        part = models.ParticipationModel.objects.filter(ce=ce)
        self.assertEqual(len(part), 2)
        self.assertEqual(part[0].team_participants, 'Philip')
        self.assertEqual(part[1].team_participants, 'Steve')

    def test_blank_participants(self):
        # shouldn't create a Participants db row
        response = self.client.post(reverse('CE:new'), {'title': 'Test CE',
                                                        'participants-0-date': '',
                                                        'participants-0-national_participants': '',
                                                        'participants-0-team_participants': '',
                                                        'text-TOTAL_FORMS': 0,
                                                        'text-INITIAL_FORMS': 0,
                                                        'question-TOTAL_FORMS': 0,
                                                        'question-INITIAL_FORMS': 0,
                                                        'participants-TOTAL_FORMS': 1,
                                                        'participants-INITIAL_FORMS': 1
                                                        })
        self.assertRedirects(response, '/CE/2')
        ce = models.CultureEvent.objects.get(pk=2)
        part = models.ParticipationModel.objects.filter(ce=ce)
        self.assertEqual(len(part), 0)
