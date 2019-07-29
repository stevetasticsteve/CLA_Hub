from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest
from . import views


class HomePageTest(TestCase):

    def test_home_page_returns_correct_html(self):
        response = self.client.get('/CE/')
        html = response.content.decode('utf8')
        self.assertIn('<title>Home page</title>', html)
        self.assertTrue(html.strip().endswith('</html>'))

        self.assertTemplateUsed('CE/home.html')
