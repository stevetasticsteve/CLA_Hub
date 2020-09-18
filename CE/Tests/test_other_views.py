from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from CE import models, settings, OCM_categories

import time

# A separate test class for each model or view
# a separate test method for each set of conditions you want to test
# test methods that describe their function


class CEHomeAndAlphabeticalTest(TestCase):
    def setUp(self):
        self.total_CEs = settings.culture_events_shown_on_home_page + 3
        for i in range(settings.culture_events_shown_on_home_page + 1):
            Ces = models.CultureEvent(title=('Example culture event ' + str(i)),
                                      last_modified_by='Tester')
            Ces.save()

    def test_home_page_get_response(self):
        response = self.client.get(reverse('CE:home_page'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('CE/home.html')

    def test_home_page_contents(self):
        response = self.client.get(reverse('CE:home_page'))

        self.assertContains(response, '<!doctype html>') # checks base template used
        self.assertContains(response, 'CE Home')
        # test CE's loaded
        self.assertContains(response, 'Example culture event 2')
        # test not more loaded than settings allow
        self.assertNotContains(response, 'Example culture event ' + str(self.total_CEs))
        self.assertContains(response, 'by Tester')

    def test_CE_alphabetical_page_response(self):
        response = self.client.get(reverse('CE:alphabetical'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('CE/alphabetical.html')

    def test_CE_alphabetical_page_contents(self):
        response = self.client.get(reverse('CE:alphabetical'))

        self.assertEqual(len(response.context['CEs']), self.total_CEs)


class TestViewPage(TestCase):
    def setUp(self):
        ce = models.CultureEvent(title='Example CE1',
                                 description_plain_text='A culture event happened',
                                 differences='Last time it was different')
        ce.save()
        text = models.Text(ce=models.CultureEvent.objects.get(pk=3),
                           audio='musicFile.ogg',
                           phonetic_text='foᵘnɛtɪks',
                           orthographic_text='orthographic')
        text.save()

    def test_view_page(self):
        # should return Example CE 1 page
        response = self.client.get(reverse('CE:view', args='3'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('CE/view_CE.html')
        self.assertContains(response, 'Example CE1')
        self.assertContains(response, 'foᵘnɛtɪks')
        self.assertContains(response, 'musicFile.ogg')

    def test_markdown_enabled(self):
        markdown_text = '''
# This is markdown text
* list item 1
* list item 2
* list item 3

**text in bold**'''
        ce = models.CultureEvent.objects.get(pk=1)
        ce.description_plain_text = markdown_text
        ce.interpretation = '## Markdown'
        ce.save()
        response = self.client.get(reverse('CE:view', args='1'))

        self.assertContains(response, '<h1>This is markdown text</h1>')
        self.assertContains(response, '<ul>\n<li>list item 1</li>\n<li>list item 2</li>\n<li>list item 3</li>\n</ul>')
        self.assertContains(response, '<p><strong>text in bold</strong></p>')
        self.assertContains(response, '<h2>Markdown</h2>')



    def test_404(self):
        # test an out of range index
        response = self.client.get(reverse('CE:view', args='9'))
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
        visits = models.Visit(date='2019-08-05',
                              team_present='Steve',
                              nationals_present='Ulumo',
                              ce=ce)
        visits.save()
        questions = models.Question(question='First question',
                                    answer='First answer',
                                    asked_by='Tester',
                                    ce=ce)
        questions.save()
        time.sleep(0.1)
        ce = models.CultureEvent(title='Cats like Example CE2',
                                 description_plain_text='A culture event happened again',
                                 differences='Last time it was different')
        ce.save()
        questions = models.Question(question='Second question',
                                    asked_by='Tester',
                                    ce=ce)
        questions.save()
        visits = models.Visit(date='2019-08-06',
                              team_present='Rhett',
                              nationals_present='Ulumo',
                              ce=ce)
        visits.save()
        time.sleep(0.1)

        ce = models.CultureEvent(title='because I can Example CE3',
                                 description_plain_text='A culture event happened a third time',
                                 differences='Last time it was different')
        ce.save()
        questions = models.Question(question='Third question',
                                    asked_by='Tester',
                                    ce=ce)
        questions.save()
        time.sleep(0.1)
        questions = models.Question(question='Fourth question',
                                    asked_by='Tester',
                                    ce=ce)
        questions.save()
        visits = models.Visit(date='2019-08-07',
                              team_present='Philip',
                              nationals_present='Ulumo',
                              ce=ce)
        visits.save()


    def test_chron_question_page(self):
        response = self.client.get(reverse('CE:questions_chron'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('CE/questions_chron.html')
        self.assertContains(response, 'First question')
        # get a ordered list from .db and then check slice position of each question
        q = models.Question.objects.all().order_by('-date_created')
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
        q = models.Question.objects.all()
        self.assertEqual(len(q), 6, 'Wrong number of questions')
        set_ces = set([i.ce for i in q])
        set_ces = sorted(set_ces, key=lambda x: x.title.lower())
        self.assertEqual(len(set_ces), 4, 'Wrong number of unique CEs')
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
    def setUp(self):
        ce = models.CultureEvent(title='Example CE1',
                                 description_plain_text='A first CE')
        ce.save()
        tags = OCM_categories.check_tags_for_OCM('1-1, 1-16')
        for tag in tags:
            ce.tags.add(tag)

    def test_ocm_home_page_displays(self):
        response = self.client.get(reverse('CE:OCM_home'))
        self.assertTemplateUsed('CE/OCM_home.html')
        self.assertEqual(response.status_code, 200, 'OCM Home not displaying')

    def test_hyperlink_and_badge_present_for_tagged(self):
        response = self.client.get(reverse('CE:OCM_home'))
        self.assertContains(response, '<a href="tag/1-1-geography-weather">')
        self.assertContains(response, '<span class="badge badge-primary badge-pill">1</span>')

    def test_hyperlink_and_badge_absent_for_untagged(self):
        response = self.client.get(reverse('CE:OCM_home'))
        self.assertNotContains(response, '<a href="tag/1-2-settlements-communities">')

    def test_search(self):
        response = self.client.get(reverse('CE:search_CE') + '?search=Example')

        self.assertEqual(response.status_code, 200, 'CE search GET request failed')
        self.assertContains(response, 'Example CE1')
        response = self.client.get(reverse('CE:search_CE') + '?search=Bad')
        self.assertContains(response, 'No search results')


class TagSummaryPageTest(TestCase):
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
        response = self.client.get(reverse('CE:view_tag', kwargs={'slug': '1-2-settlements-and-communities'}))
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
        self.assertTemplateUsed(response, 'CE/all_tags.html')

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

    def test_tag_search(self):
        response = self.client.get(reverse('CE:tags_search') + '?search=1-1')

        self.assertEqual(response.status_code, 200, 'CE search GET request failed')
        self.assertContains(response, '1-1 Geography')
        response = self.client.get(reverse('CE:tags_search') + '?search=Bad')
        self.assertContains(response, 'No search results')


class TextViewAndGenreTest(TestCase):
    def setUp(self):
        ce = models.CultureEvent(title='Example CE1',
                                 description_plain_text='A first CE')
        ce.save()
        self.text1 = models.Text(text_title='Text 1',
                                 last_modified_by='Tester',
                                 phonetic_standard='1',
                                 discourse_type='1',
                                 orthographic_text='Ortho1',
                                 ce=ce)
        self.text1.save()
        self.text2 = models.Text(text_title='Text 2',
                                 last_modified_by='Tester',
                                 phonetic_standard='2',
                                 discourse_type='2',
                                 orthographic_text='Ortho2',
                                 ce=ce)
        self.text2.save()

    def test_text_home_get_response(self):
        response = self.client.get(reverse('CE:texts_home'))
        self.assertEqual(response.status_code, 200, 'Not a 200 response')
        self.assertTemplateUsed('CE/texts.html')

    def test_text_home_contents(self):
        self.assertEqual(len(models.Text.objects.all()), 3, 'setup not functioning')
        response = self.client.get(reverse('CE:texts_home'))

        self.assertContains(response, self.text1.orthographic_text)
        self.assertContains(response, self.text2.orthographic_text)
        self.assertContains(response, self.text1.ce)

    def test_text_genre_with_data_get_response(self):
        response = self.client.get(reverse('CE:text_genre', args='1'))
        self.assertEqual(response.status_code, 200, 'Not a 200 response')
        self.assertTemplateUsed('CE/texts_genre.html')

    def test_text_genre_with_data_content(self):
        response = self.client.get(reverse('CE:text_genre', args='1'))

        self.assertContains(response, self.text1.orthographic_text)
        self.assertNotContains(response, self.text2.orthographic_text)

    def test_text_genre_no_data_get_response(self):
        response = self.client.get(reverse('CE:text_genre', args='5'))
        self.assertEqual(response.status_code, 200, 'Not a 200 response')
        self.assertTemplateUsed('CE/texts_genre.html')

    def test_text_genre_no_data_content(self):
        response = self.client.get(reverse('CE:text_genre', args='5'))

        self.assertContains(response, 'No texts yet')

    def test_text_genre_outOfRange_response(self):
        self.client.get(reverse('CE:text_genre', args='9'))
        self.assertTemplateUsed('404.html')

    def test_text_search(self):
        response = self.client.get(reverse('CE:text_search') + '?search=t')

        self.assertEqual(response.status_code, 200, 'CE search GET request failed')
        self.assertContains(response, 'Text 1')
        response = self.client.get(reverse('CE:text_search') + '?search=Bad')
        self.assertContains(response, 'No search results')


