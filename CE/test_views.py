from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from CE import models, settings, OCM_categories

import os
import time

# A separate test class for each model or view
# a separate test method for each set of conditions you want to test
# test methods that describe their function

# view tests
class CEHomeViewTest(TestCase):
    def setUp(self):
        self.total_CEs = settings.culture_events_shown_on_home_page + 1
        for i in range(self.total_CEs):
            Ces = models.CultureEvent(title=('Example culture event ' + str(i)),
                                      last_modified_by='Tester')
            Ces.save()

    def test_home_page_returns_correct_html(self):
        # home page should show recently modified CEs
        response = self.client.get(reverse('CE:home_page'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<!doctype html>') # checks base template used
        self.assertContains(response, 'CE Home')
        self.assertTemplateUsed('CE/home.html')
        # test CE's loaded
        self.assertContains(response, 'Example culture event 2')
        # test not more loaded than settings allow
        self.assertNotContains(response, 'Example culture event ' + str(self.total_CEs))
        self.assertContains(response, 'by Tester')


class TestViewPage(TestCase):
    def setUp(self):
        ce = models.CultureEvent(title='Example CE1',
                                 description_plain_text='A culture event happened',
                                 differences='Last time it was different')
        ce.save()
        text = models.TextModel(ce=models.CultureEvent.objects.get(pk=1),
                            audio='musicFile.ogg',
                            phonetic_text='foᵘnɛtɪks',
                            orthographic_text='orthographic',
                            valid_for_DA=False)
        text.save()

    def test_view_page(self):
        # should return Example CE 1 page
        response = self.client.get(reverse('CE:view', args='1'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('CE/view_CE.html')
        self.assertContains(response, 'Example CE1')
        self.assertContains(response, 'foᵘnɛtɪks')
        self.assertContains(response, 'musicFile.ogg')

    def test_404(self):
        # test an out of range index
        response = self.client.get(reverse('CE:view', args='2'))
        self.assertEqual(response.status_code, 404)

# class TestEditPage(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         credentials = User(username='Tester')
#         credentials.set_password('secure_password')
#         credentials.save()
#
#     def setUp(self):
#         self.client.login(username='Tester', password='secure_password')
#         ce = models.CultureEvent(title='Example CE1',
#                                  description='A culture event happened',
#                                  participation='Rhett did it',
#                                  differences='Last time it was different')
#         ce.save()
#         text = models.TextModel(ce=models.CultureEvent.objects.get(pk=1),
#                             audio='musicFile.ogg',
#                             phonetic_text='foᵘnɛtɪks',
#                             orthographic_text='orthographic')
#         text.save()
#
#     def test_edit_page_GET_response(self):
#         # Form should populate with database data
#         response = self.client.get(reverse('CE:edit', args='1'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed('CE/edit_CE.html')
#         html = response.content.decode('utf8')
#         self.assertContains(response, '<form')
#         # check form contents
#         self.assertContains(response, 'value="Example CE1"')
#         self.assertContains(response, 'Rhett did it')
#
#     def test_valid_edit_page_POST_response_change_everything(self):
#         # CE model should be updated, a new one shouldn't be created
#         response = self.client.post(reverse('CE:edit', args='1'), {'title' : 'BAM',
#                                                                    'participation' : 'minimal',
#                                                                    'description' : 'pretty easy'},
#                                     follow=True)
#         self.assertTemplateUsed('CE/edit_CE.html')
#         self.assertEqual(response.redirect_chain[0][1], 302, 'No redirect following POST')
#         ce = models.CultureEvent.objects.get(pk=1)
#         self.assertEqual(ce.title, 'BAM', 'edit not saved to db')
#         self.assertFalse(ce.title == 'Example CE1', 'edit not saved to db')
#         self.assertEqual(ce.last_modified_by, 'Tester', 'Last modified by not updated')
#         self.assertEqual(response.status_code, 200, 'New page not shown')
#         self.assertContains(response, 'BAM')
#
#     def test_valid_edit_page_POST_response_change_description_not_title(self):
#         # CE model should be updated, a new one shouldn't be created
#         response = self.client.post(reverse('CE:edit', args='1'), {'title' : 'Example CE1',
#                                                                    'participation': 'minimal',
#                                                                    'description': 'pretty easy'},
#                                     follow=True)
#         self.assertTemplateUsed('CE/edit_CE.html')
#         self.assertEqual(response.redirect_chain[0][1], 302, 'No redirect following POST')
#         ce = models.CultureEvent.objects.get(pk=1)
#         self.assertEqual(ce.title, 'Example CE1', 'edit not saved to db')
#         self.assertEqual(ce.description, 'pretty easy', 'edit not saved to db')
#         self.assertEqual(response.status_code, 200, 'New page not shown')
#         self.assertContains(response, 'Example CE1')
#         self.assertEqual(ce.last_modified_by, 'Tester', 'Last modified by not updated')
#
#     def test_edit_page_no_changes(self):
#         # no changes should go through, but .db unchanged
#         ce = models.CultureEvent.objects.get(pk=1)
#         response = self.client.post(reverse('CE:edit', args='1'), {'title': 'Example CE1',
#                                                                    'participation': 'Rhett did it',
#                                                                    'description': 'A culture event happened',
#                                                                    'differences' : 'Last time it was different'},
#                                     follow=True)
#         new_ce = models.CultureEvent.objects.get(pk=1)
#         self.assertEqual(response.redirect_chain[0][1], 302, 'No redirect following POST')
#         self.assertEqual(ce, new_ce)
#         self.assertEqual(ce.title, new_ce.title)
#
#     def test_edit_page_changing_to_existing_CE_title(self):
#         # should reject changing to an existing title
#         ce = models.CultureEvent(title='Example CE2',
#                                  description='A culture event happened',
#                                  participation='Rhett did it',
#                                  differences='Last time it was different')
#         ce.save()
#         response = self.client.post(reverse('CE:edit', args='2'), {'title': 'Example CE1',
#                                                                    'participation': 'Rhett did it',
#                                                                    'description': 'A culture event happened',
#                                                                    'differences': 'Last time it was different'},
#                                     follow=True)
#         self.assertContains(response, 'Culture event with this Title already exists')
#         self.assertEqual(models.CultureEvent.objects.get(pk=2).title, 'Example CE2')
#         self.assertEqual(models.CultureEvent.objects.get(pk=1).title, 'Example CE1')


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
        self.assertEqual(len(models.TextModel.objects.all()), 0, 'A blank Text was added')

    def test_new_CE_page_invalid_POST_repeated_title_response(self):
        # Form should be show again with error message
        response = self.client.post(reverse('CE:new'), {
            'Title': 'Example CE1',
            'description_plain_text': 'I\'m testing this CE',
            'text-TOTAL_FORMS': 0,
            'text-INITIAL_FORMS': 0,
            'question-TOTAL_FORMS': 0,
            'question-INITIAL_FORMS': 0,
            'participants-TOTAL_FORMS': 1,
            'participants-INITIAL_FORMS': 1
        }, follow=True)
        #todo form error messages
        # self.assertContains(response, 'Culture event with this Title already exists')
        with self.assertRaises(models.CultureEvent.DoesNotExist):
            models.CultureEvent.objects.get(pk=2)

    def test_new_CE_page_invalid_POST_no_title_response(self):
        # Form should be shown again with error message
        # No extra CE should be added to .db
        # todo no form error message shown
        response = self.client.post(reverse('CE:new'), {
            'description_plain_text': 'I\'m testing this CE',
            'text-TOTAL_FORMS': 0,
            'text-INITIAL_FORMS': 0,
            'question-TOTAL_FORMS': 0,
            'question-INITIAL_FORMS': 0,
            'participants-TOTAL_FORMS': 1,
            'participants-INITIAL_FORMS': 1
        }, follow=True)
        self.assertTemplateUsed('CE/new_CE.html')
        # self.assertContains(response, 'This field is required')
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
                                                        'participants-INITIAL_FORMS': 2
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


class UnloggedUserRedirect(TestCase):
    def test_redirected_from_edit_CE_page(self):
        response = self.client.get(reverse('CE:edit', args='1'), follow=True)
        self.assertTemplateUsed('CE/edit.html')
        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertEqual(response.status_code, 200,
                         'Unlogged User not redirected from edit CE page')
        self.assertRedirects(response, '/accounts/login/?next=/CE/1/edit')

    def test_redirected_from_new_CE_page(self):
        response = self.client.get(reverse('CE:new'), follow=True)
        self.assertTemplateUsed('CE/edit.html')
        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertEqual(response.status_code, 200,
                         'Unlogged User not redirected from edit CE page')
        self.assertRedirects(response, '/accounts/login/?next=/CE/new')




class QuestionPageTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        credentials = User(username='Tester')
        credentials.set_password('secure_password')
        credentials.save()

    def setUp(self):
        self.client.login(username='Tester', password='secure_password')
        # have one model previously in .db
        ce = models.CultureEvent(title='An Example CE1',
                                 description_plain_text='A culture event happened',
                                 differences='Last time it was different')
        ce.save()
        participants = models.ParticipationModel(date='2019-08-05',
                                                 team_participants='Steve',
                                                 national_participants='Ulumo',
                                                 ce=ce)
        participants.save()
        questions = models.QuestionModel(question='First question',
                                         answer='First answer',
                                         asked_by='Tester',
                                         ce=ce)
        questions.save()
        time.sleep(0.1)
        ce = models.CultureEvent(title='Cats like Example CE2',
                                 description_plain_text='A culture event happened again',
                                 differences='Last time it was different')
        ce.save()
        questions = models.QuestionModel(question='Second question',
                                         asked_by='Tester',
                                         ce=ce)
        questions.save()
        participants = models.ParticipationModel(date='2019-08-06',
                                                 team_participants='Rhett',
                                                 national_participants='Ulumo',
                                                 ce=ce)
        participants.save()
        time.sleep(0.1)

        ce = models.CultureEvent(title='because I can Example CE3',
                                 description_plain_text='A culture event happened a third time',
                                 differences='Last time it was different')
        ce.save()
        questions = models.QuestionModel(question='Third question',
                                         asked_by='Tester',
                                         ce=ce)
        questions.save()
        time.sleep(0.1)
        questions = models.QuestionModel(question='Fourth question',
                                         asked_by='Tester',
                                         ce=ce)
        questions.save()
        participants = models.ParticipationModel(date='2019-08-07',
                                                 team_participants='Philip',
                                                 national_participants='Ulumo',
                                                 ce=ce)
        participants.save()


    def test_chron_question_page(self):
        response = self.client.get(reverse('CE:questions_chron'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('CE/questions_chron.html')
        self.assertContains(response, 'First question')
        # get a ordered list from .db and then check slice position of each question
        q = models.QuestionModel.objects.all().order_by('-date_created')
        # check that questions were uploaded in the right order on class initialisation
        self.assertEqual(q[0].question, 'Fourth question', 'Test data not in correct order')
        self.assertEqual(q[1].question, 'Third question', 'Test data not in correct order')
        self.assertEqual(q[2].question, 'Second question', 'Test data not in correct order')
        self.assertEqual(q[3].question, 'First question', 'Test data not in correct order')
        html = response.content.decode('utf8')
        q1_pos = html.find(q[0].question)
        q2_pos = html.find(q[1].question)
        q3_pos = html.find(q[2].question)
        q4_pos = html.find(q[3].question)
        self.assertGreater(q2_pos, q1_pos)
        self.assertGreater(q3_pos, q2_pos)
        self.assertGreater(q4_pos, q3_pos)

    def test_alphabetical_question_page(self):
        response = self.client.get(reverse('CE:questions_alph'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('CE/questions_alph.html')
        self.assertContains(response, 'An Example CE1')
        self.assertContains(response, 'because I can Example CE3')
        # get a ordered list from .db and then check slice position of each question
        q = models.QuestionModel.objects.all()
        self.assertEqual(len(q), 4, 'Wrong number of questions')
        set_ces = set([i.ce for i in q])
        set_ces = sorted(set_ces, key=lambda x: x.title.lower())
        self.assertEqual(len(set_ces), 3, 'Wrong number of unique CEs')
        # check that questions were uploaded in the right order on class initialisation
        self.assertEqual(set_ces[0].title, 'An Example CE1', 'Test data not in correct order')
        self.assertEqual(set_ces[1].title, 'because I can Example CE3', 'Test data not in correct order')
        self.assertEqual(set_ces[2].title, 'Cats like Example CE2', 'Test data not in correct order')
        html = response.content.decode('utf8')
        ce1_pos = html.find(set_ces[0].title)
        ce2_pos = html.find(set_ces[1].title)
        ce3_pos = html.find(set_ces[2].title)
        self.assertGreater(ce2_pos, ce1_pos)
        self.assertGreater(ce3_pos, ce2_pos)



class OCMHomePageTest(TestCase):

    def test_ocm_home_page_displays(self):
        response = self.client.get(reverse('CE:OCM_home'))
        self.assertTemplateUsed('CE/OCM_home.html')
        self.assertEqual(response.status_code, 200, 'OCM Home not displaying')


class test_tag_summary_page(TestCase):
    def setUp(self):
        ce = models.CultureEvent(title='Example CE1',
                                 description_plain_text='A first CE')
        ce.save()
        tags = OCM_categories.check_tags_for_OCM('1-1, 1-16')
        for tag in tags:
            ce.tags.add(tag)

    def test_tag_summary_response(self):
        response = self.client.get(reverse('CE:view_tag', kwargs={'slug':'1-1-geography-weather'}))
        self.assertTemplateUsed('CE/tag_detail_page.html')
        self.assertEqual(response.status_code, 200, 'No response')

    def test_non_OCM_tag(self):
        response = self.client.get(reverse('CE:view_tag', kwargs={'slug': '1-16'}))
        self.assertTemplateUsed('CE/tag_summary_page.html')
        self.assertEqual(response.status_code, 200, 'No response')

    def test_tag_summary_content(self):
        response = self.client.get(reverse('CE:view_tag', kwargs={'slug':'1-1-geography-weather'}))
        self.assertContains(response, 'A first CE')

    def test_404_response(self):
        response = self.client.get(reverse('CE:view_tag', kwargs={'slug': '1-900'}))
        self.assertEqual(response.status_code, 404, 'No response')

class TagListViewTest(TestCase):
    def setUp(self):
        ce = models.CultureEvent(title='Example CE1',
                                 description_plain_text='A first CE')
        ce.save()
        tags = OCM_categories.check_tags_for_OCM('1-1, 1-16, Culture')
        for tag in tags:
            ce.tags.add(tag)

        ce = models.CultureEvent(title='Example CE2',
                                 description_plain_text='A second CE')
        ce.save()
        tags = OCM_categories.check_tags_for_OCM('Culture')
        for tag in tags:
            ce.tags.add(tag)

    def test_tag_list_response(self):
        response = self.client.get(reverse('CE:list_tags'))
        self.assertEqual(response.status_code, 200, 'No response')
        self.assertTemplateUsed(response, 'CE/tag_list_page.html')

    def test_tags_in_content(self):
        response = self.client.get(reverse('CE:list_tags'))
        self.assertContains(response, 'Culture')
        self.assertContains(response, '1-1 Geography') # avoid dealing with the &
        self.assertContains(response, '1-16')

    def test_most_recent_tags_at_top(self):
        # Culture should be linked to 2 CEs, and be at top of page
        response = self.client.get(reverse('CE:list_tags'))
        html = response.content.decode('utf8')
        pos1 = html.find('Culture')
        pos2 = html.find('1-16')
        self.assertGreater(pos2, pos1)
