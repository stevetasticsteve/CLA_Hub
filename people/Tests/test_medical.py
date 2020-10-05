from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from people import models


class MedicalTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        credentials = User(username='Tester')
        credentials.set_password('secure_password')
        credentials.save()

    def setUp(self):
        self.client.login(username='Tester', password='secure_password')
        test_person = models.Person(
            name='Test Person 1',
            village=1,
            medical='notes recorded here'
        )
        test_person.save()
        for t in range(1, 5):
            event = models.MedicalAssessment(
                short='Event {t}'.format(t=t),
                subjective='Subjective {t}'.format(t=t),
                objective='Objective {t}'.format(t=t),
                assessment='Assessment {t}'.format(t=t),
                plan='Plan {t}'.format(t=t),
                person=test_person
            )
            event.save()

    def test_not_logged_in_redirect(self):
        self.client.logout()
        response = self.client.get(reverse('people:medical', args='1'))

        self.assertEqual(response.status_code, 302)

    def test_medical_profile_response(self):
        response = self.client.get(reverse('people:medical', args='1'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('people/medical_profile.html')

    def test_medical_profile_contents(self):
        response = self.client.get(reverse('people:medical', args='1'))

        # Test database info displayed
        self.assertContains(response, 'Test Person 1')
        self.assertContains(response, 'notes recorded here')
        self.assertContains(response, 'Event 1')
        self.assertContains(response, 'Event 4')
        self.assertContains(response, 'Subjective 1')
        self.assertContains(response, 'Subjective 4')

        # Test hyperlinks displayed
        self.assertContains(response, '<a href="/people/medical/1/edit/1">')
        self.assertContains(response, '<a href="/people/medical/1/edit/4">')
        self.assertContains(response, '<a href="/people/1">')
        self.assertContains(response, '<a href="/people/medical/1/notes"')
        self.assertContains(response, '<a href="/people/medical/1/add"')

    def test_markdown_profile_contents(self):
        person = models.Person.objects.get(pk=1)
        person.medical = ('# Heading in Markdown')
        person.save()
        event = models.MedicalAssessment.objects.get(pk=1)
        event.subjective = '## Sub'
        event.objective = '### Ob'
        event.assessment = '#### Ass'
        event.plan = '**Plan**'
        event.save()
        response = self.client.get(reverse('people:medical', args='1'))

        self.assertContains(response, '<h1>Heading in Markdown</h1>')
        self.assertContains(response, '<h2>Sub</h2>')
        self.assertContains(response, '<h3>Ob</h3>')
        self.assertContains(response, '<h4>Ass</h4>')
        self.assertContains(response, '<strong>Plan</strong>')

    def test_medical_notes_response(self):
        response = self.client.get(reverse('people:edit_medical_notes', args='1'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('people/medical_edit.html')

    def test_medical_notes_contents(self):
        response = self.client.get(reverse('people:edit_medical_notes', args='1'))

        self.assertContains(response, 'Test Person 1')
        self.assertContains(response, 'notes recorded here')

    def test_medical_notes_post(self):
        self.assertEqual('notes recorded here', models.Person.objects.get(pk=1).medical)
        self.client.post(reverse('people:edit_medical_notes', args='1'), {'medical': 'New medical notes'})

        self.assertEqual('New medical notes', models.Person.objects.get(pk=1).medical, 'Medical notes not posted')

    def test_new_assessment_response(self):
        response = self.client.get(reverse('people:new_assessment', args='1'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('people/soap_new.html')

    def test_new_assessment_contents(self):
        response = self.client.get(reverse('people:new_assessment', args='1'))

        self.assertContains(response, 'Test Person 1')
        self.assertContains(response, '<form')

    def test_new_assessment_post(self):
        self.assertEqual(len(models.MedicalAssessment.objects.all()), 4)
        self.client.post(reverse('people:new_assessment', args='1'), {
            'short': 'Event 5',
            'subjective': 'Subjective 5',
            'objective': 'Objective 5',
            'assessment': 'Assessment 5',
            'plan': 'Plan 5'
        })

        self.assertEqual(len(models.MedicalAssessment.objects.all()), 5, 'Assessment not added')
        self.assertEqual(models.MedicalAssessment.objects.get(pk=5).short, 'Event 5')

    def test_edit_assessment_response(self):
        response = self.client.get(reverse('people:edit_assessment', args=('1', '1')))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('people/soap_edit.html')

    def test_edit_assessment_contents(self):
        response = self.client.get(reverse('people:edit_assessment', args=('1', '1')))

        self.assertContains(response, 'Event 1')
        self.assertContains(response, 'Subjective 1')
        self.assertContains(response, '<form')

        response = self.client.get(reverse('people:edit_assessment', args=('1', '2')))

        self.assertContains(response, 'Event 2')
        self.assertContains(response, 'Subjective 2')
        self.assertContains(response, '<form')

    def test_edit_assessment_post(self):
        self.assertEqual(len(models.MedicalAssessment.objects.all()), 4)

        self.client.post(reverse('people:edit_assessment', args=('1', '1')), {
            'short': 'Brand new Event 1',
            'subjective': 'Subjective 1',
            'objective': 'Objective 1',
            'assessment': 'Assessment 1',
            'plan': 'Plan 1'
        })

        self.assertEqual(len(models.MedicalAssessment.objects.all()), 4, 'Extra object added')
        self.assertEqual(models.MedicalAssessment.objects.get(pk=1).short, 'Brand new Event 1')
