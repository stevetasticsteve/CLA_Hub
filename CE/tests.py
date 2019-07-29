from django.test import TestCase
from django.urls import resolve
from django.http import HttpRequest
from . import views


class HomePageTest(TestCase):

    def test_home_page_returns_correct_html(self):
        response = self.client.get('/CE/')
        html = response.content.decode('utf8')
        self.assertIn('CE Home', html, 'CE home page not loaded')

        self.assertTemplateUsed('CE/home.html')
