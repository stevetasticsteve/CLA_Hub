from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from CE import models


class TestEditPage(TestCase):
    test_data = {
        'username': 'Tester',
        'title': 'Example CE1',
        'description_plain_text': 'A culture event happened',
        'differences': 'Last time it was different',
        'interpretation': 'It probably has meaning',
        'national_participants': 'Ulumo',
        'team_participants': 'Steve',
        'date': '2019-02-20',
        'phonetic_text': 'foᵘnɛtɪks',
        'orthographic_text': 'orthographic',
        'valid_for_DA': False,
        'tags': 'taggie',
        'question': 'Does this test work?',
        'answer': 'Yes, it does!'
    }

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        credentials = User(username='Tester')
        credentials.set_password('secure_password')
        credentials.save()

    def setUp(self):
        self.client.login(username='Tester', password='secure_password')
        ce = models.CultureEvent(title=self.test_data['title'],
                                 description_plain_text=self.test_data['description_plain_text'],
                                 differences=self.test_data['differences'],
                                 interpretation=self.test_data['interpretation'],)
        ce.save()
        ce2 = models.CultureEvent(title='CE2')
        ce2.save()
        ce.tags.add(self.test_data['tags'])
        part = models.ParticipationModel(national_participants=self.test_data['national_participants'],
                                         team_participants=self.test_data['team_participants'],
                                         date=self.test_data['date'],
                                         ce=ce)
        part.save()
        text = models.TextModel(ce=ce,
                                phonetic_text=self.test_data['phonetic_text'],
                                orthographic_text=self.test_data['orthographic_text'],
                                valid_for_DA=self.test_data['valid_for_DA'])
        text.save()
        q = models.QuestionModel(ce=ce,
                                 question=self.test_data['question'],
                                 answer=self.test_data['answer'])
        q.save()

    def test_setup(self):
        self.assertEqual(models.CultureEvent.objects.get(pk=1).title, self.test_data['title'])
        self.assertEqual(len(models.CultureEvent.objects.all()), 2)

    def test_edit_page_GET_response(self):
        response = self.client.get(reverse('CE:edit', args='1'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('CE/edit_CE.html')

    def test_CE_form_has_initial_data(self):
        response = self.client.get(reverse('CE:edit', args='1'))
        self.assertContains(response, '<form')
        # check form contents
        for data in self.test_data.values():
            # html doesn't render the valid for DA boolean, so skip it
            if data == False:
                continue
            self.assertContains(response, data)

    def test_redirect_after_post(self):
        response = self.client.post(reverse('CE:edit', args='1'),
                                    {'title': self.test_data['title'],
                                     'description_plain_text': 'A new description'},
                                    follow=True)
        self.assertTemplateUsed(response, 'CE/view_CE.html')
        self.assertRedirects(response, '/CE/1')

    def test_number_of_CEs_the_same(self):
        self.client.post(reverse('CE:edit', args='1'),
                         {'title': self.test_data['title'],
                         'description_plain_text': 'A new description'},
                         follow=True)
        self.assertEqual(len(models.CultureEvent.objects.all()), 2)

    def test_CE_model_updated_correctly_after_POST(self):
        self.client.post(reverse('CE:edit', args='1'),
                         {'title': self.test_data['title'],
                          'description_plain_text': 'A new description'},
                         follow=True)
        ce = models.CultureEvent.objects.get(pk=1)
        self.assertEqual('A new description', ce.description_plain_text)
        self.assertEqual(self.test_data['title'], ce.title)
        self.assertEqual(ce.pk, 1)

    def test_changing_CE_title(self):
        self.client.post(reverse('CE:edit', args='1'),
                         {'title': 'A new title',
                          'description_plain_text': 'A new description'},
                         follow=True)
        ce = models.CultureEvent.objects.get(pk=1)
        self.assertEqual('A new description', ce.description_plain_text)
        self.assertEqual('A new title', ce.title)
        self.assertEqual(ce.pk, 1)

    def test_edit_title_to_existing_rejected(self):
        with self.assertRaises(IntegrityError):
            response = self.client.post(reverse('CE:edit', args='1'),
                                        {'title': 'CE2',
                                        'description_plain_text': 'A new description'},
                                        follow=False)
    # todo I've caught the error, but user will only see an error screen


    # def test_valid_edit_page_POST_response_change_everything(self):
    #     # CE model should be updated, a new one shouldn't be created
    #     response = self.client.post(reverse('CE:edit', args='1'), {'title' : 'BAM',
    #                                                                'participation' : 'minimal',
    #                                                                'description' : 'pretty easy'},
    #                                 follow=True)
    #     self.assertTemplateUsed('CE/edit_CE.html')
    #     self.assertEqual(response.redirect_chain[0][1], 302, 'No redirect following POST')
    #     ce = models.CultureEvent.objects.get(pk=1)
    #     self.assertEqual(ce.title, 'BAM', 'edit not saved to db')
    #     self.assertFalse(ce.title == 'Example CE1', 'edit not saved to db')
    #     self.assertEqual(ce.last_modified_by, 'Tester', 'Last modified by not updated')
    #     self.assertEqual(response.status_code, 200, 'New page not shown')
    #     self.assertContains(response, 'BAM')
    #
    # def test_valid_edit_page_POST_response_change_description_not_title(self):
    #     # CE model should be updated, a new one shouldn't be created
    #     response = self.client.post(reverse('CE:edit', args='1'), {'title' : 'Example CE1',
    #                                                                'participation': 'minimal',
    #                                                                'description': 'pretty easy'},
    #                                 follow=True)
    #     self.assertTemplateUsed('CE/edit_CE.html')
    #     self.assertEqual(response.redirect_chain[0][1], 302, 'No redirect following POST')
    #     ce = models.CultureEvent.objects.get(pk=1)
    #     self.assertEqual(ce.title, 'Example CE1', 'edit not saved to db')
    #     self.assertEqual(ce.description, 'pretty easy', 'edit not saved to db')
    #     self.assertEqual(response.status_code, 200, 'New page not shown')
    #     self.assertContains(response, 'Example CE1')
    #     self.assertEqual(ce.last_modified_by, 'Tester', 'Last modified by not updated')
    #
    # def test_edit_page_no_changes(self):
    #     # no changes should go through, but .db unchanged
    #     ce = models.CultureEvent.objects.get(pk=1)
    #     response = self.client.post(reverse('CE:edit', args='1'), {'title': 'Example CE1',
    #                                                                'participation': 'Rhett did it',
    #                                                                'description': 'A culture event happened',
    #                                                                'differences' : 'Last time it was different'},
    #                                 follow=True)
    #     new_ce = models.CultureEvent.objects.get(pk=1)
    #     self.assertEqual(response.redirect_chain[0][1], 302, 'No redirect following POST')
    #     self.assertEqual(ce, new_ce)
    #     self.assertEqual(ce.title, new_ce.title)
    #
    # def test_edit_page_changing_to_existing_CE_title(self):
    #     # should reject changing to an existing title
    #     ce = models.CultureEvent(title='Example CE2',
    #                              description='A culture event happened',
    #                              participation='Rhett did it',
    #                              differences='Last time it was different')
    #     ce.save()
    #     response = self.client.post(reverse('CE:edit', args='2'), {'title': 'Example CE1',
    #                                                                'participation': 'Rhett did it',
    #                                                                'description': 'A culture event happened',
    #                                                                'differences': 'Last time it was different'},
    #                                 follow=True)
    #     self.assertContains(response, 'Culture event with this Title already exists')
    #     self.assertEqual(models.CultureEvent.objects.get(pk=2).title, 'Example CE2')
    #     self.assertEqual(models.CultureEvent.objects.get(pk=1).title, 'Example CE1')


