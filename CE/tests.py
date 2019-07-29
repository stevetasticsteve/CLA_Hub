from django.test import TestCase

class HomePageTest(TestCase):

    def test_home_page_returns_correct_html(self):
        response = self.client.get('/CE/')
        html = response.content.decode('utf8')
        self.assertIn('CE Home', html, 'CE home page not loaded')

        self.assertTemplateUsed('CE/home.html')

    def test_create_CE_btn_navigates_to_correct_url(self):
        pass
