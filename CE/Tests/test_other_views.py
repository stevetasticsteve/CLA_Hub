from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from CE import models, settings, OCM_categories

import time

# A separate test class for each model or view
# a separate test method for each set of conditions you want to test
# test methods that describe their function


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
