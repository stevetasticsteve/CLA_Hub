from django.test import TestCase
from django.urls import reverse
from django.db.utils import IntegrityError
from CE import models, settings, forms

# A separate test class for each model or view
# a seperate test method for each set of conditions you want to test
# test methods that describe their function

# view tests
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

    def test_edit(self):
        response = self.client.get(reverse('CE:edit', args='1'))
        self.assertEqual(response.status_code, 200)
        html = response.content.decode('utf8')
        self.assertIn('<form', html, 'Form not rendered')
        # check form contents
        self.assertIn('value="Example CE1"', html, 'CE title info not included in form')
        self.assertIn('Rhett did it', html, 'CE participation info not included in form')
        # test POST response
        # response = self.client.post(reverse('CE:edit', args='1'), {'title' : 'BAM',
        #                                                            'participation' : 'minimal',
        #                                                            'description' : 'pretty easy'})
        # # todo test not going through because form isn't valid
        # print('CE title = ' + models.CultureEvent.objects.get(pk=1).title)
        # self.assertEqual(response.status_code, 200)

# Form tests

class CE_EditFormTests(TestCase):
    def test_valid_data(self):
        form_data = {'title' : 'An example CE',
                     'participation' : 'Steve was there',
                     'description' : 'We did culture',
                     'differences' : 'It went better than last time'}
        form = forms.CE_EditForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_title_missing_data(self):
        form_data = {'participation' : 'Steve was there',
                     'description' : 'We did culture',
                     'differences' : 'It went better than last time'}
        form = forms.CE_EditForm(data=form_data)
        self.assertFalse(form.is_valid())


# Model tests

class CEModelTest(TestCase):
    def test_string_method(self):
        ce = models.CultureEvent(title='Example CE1')
        self.assertEqual(str(ce), 'Example CE1')


    def test_repeated_title_not_allowed(self):
        ce = models.CultureEvent(title='Example CE1',
                                 description='A first CE')
        ce.save()
        ce = models.CultureEvent(title='Example CE1',
                                 description='A second CE')

        with self.assertRaises(IntegrityError):
            ce.save()


class TextsModelTest(TestCase):
    def test_string_method(self):
        ce = models.CultureEvent(title='Example CE1')
        text = models.Texts(ce_id=ce, phonetic_text='djaŋɡo')
        self.assertEqual(str(text), 'Text for Example CE1')

