from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User


class PeopleHomeTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        credentials = User(username='Tester')
        credentials.set_password('secure_password')
        credentials.save()

    def setUp(self):
        self.client.login(username='Tester', password='secure_password')

    def test_home_get_response(self):
        response = self.client.get(reverse('people:home'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('people/home.html')

    def test_home_page_content(self):
        response = self.client.get(reverse('people:home'))

        self.assertContains(response, 'People Home')

