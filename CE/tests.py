from django.test import TestCase
from django.urls import reverse
from CE import models, settings

class CEHomeViewTest(TestCase):
    def setUp(self):
        self.total_CEs = settings.culture_events_shown_on_home_page + 1
        for i in range(self.total_CEs):
            Ces = models.CultureEvent(title=('Example culture event ' + str(i)))
            Ces.save()

    def test_home_page_returns_correct_html(self):
        response = self.client.get(reverse('CE:home_page'))
        self.assertEqual(response.status_code, 200)
        html = response.content.decode('utf8')
        self.assertTrue(html.startswith('<!doctype html>')) # checks base template used
        self.assertIn('CE Home', html, 'CE home page not loaded')
        self.assertTemplateUsed('CE/home.html')
        # test CE's loaded
        self.assertIn('Example culture event 2', html, 'Recent culture events not loaded')
        # test not more loaded than settings allow
        self.assertNotIn('Example culture event ' + str(self.total_CEs),
                         html, 'Too many CEs loaded')

class CEViewTest(TestCase):
    def setUp(self):
        ce = models.CultureEvent(title='Example CE1',
                                 description='A culture event happened',
                                 participation='Rhett did it',
                                 differences='Last time it was different')
        ce.save()
        text = models.Texts(ce_id=models.CultureEvent.objects.get(pk=1),
                            audio='musicFile.ogg',
                            phonetic_text='foᵘnɛtɪks',
                            orthographic_text='orthographic')
        text.save()
    def test_view(self):
        response = self.client.get(reverse('CE:view', args='1'))
        self.assertEqual(response.status_code, 200)
        html = response.content.decode('utf8')
        self.assertIn('Example CE1', html, 'Culture event not shown')
        self.assertIn('foᵘnɛtɪks', html, 'Phonetic text not')
        # test an out of range index
        response = self.client.get(reverse('CE:view', args='2'))
        self.assertEqual(response.status_code, 404)


