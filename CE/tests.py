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
            Ces = models.CultureEvent(title=('Example culture event ' + str(i)),
                                      last_modified_by='Tester')
            Ces.save()

    def test_home_page_returns_correct_html(self):
        # home page should show recently modified CEs
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
        self.assertIn('by Tester', html, 'Last modified by not showing on home page')


class TestViewPage(TestCase):
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

    def test_view_page(self):
        # should return Example CE 1 page
        response = self.client.get(reverse('CE:view', args='1'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('CE/view_CE.html')
        html = response.content.decode('utf8')
        self.assertIn('Example CE1', html, 'Culture event not shown')
        self.assertIn('foᵘnɛtɪks', html, 'Phonetic text not')

    def test_404(self):
        # test an out of range index
        response = self.client.get(reverse('CE:view', args='2'))
        self.assertEqual(response.status_code, 404)

class TestEditPage(TestCase):
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

    def test_edit_page_GET_response(self):
        # Form should populate with database data
        response = self.client.get(reverse('CE:edit', args='1'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('CE/edit_CE.html')
        html = response.content.decode('utf8')
        self.assertIn('<form', html, 'Form not rendered')
        # check form contents
        self.assertIn('value="Example CE1"', html, 'CE title info not included in form')
        self.assertIn('Rhett did it', html, 'CE participation info not included in form')

    def test_valid_edit_page_POST_response_change_everything(self):
        # CE model should be updated, a new one shouldn't be created
        response = self.client.post(reverse('CE:edit', args='1'), {'title' : 'BAM',
                                                                   'participation' : 'minimal',
                                                                   'description' : 'pretty easy'},
                                    follow=True)
        self.assertTemplateUsed('CE/edit_CE.html')
        self.assertEqual(response.redirect_chain[0][1], 302, 'No redirect following POST')
        ce = models.CultureEvent.objects.get(pk=1)
        self.assertEqual(ce.title, 'BAM', 'edit not saved to db')
        self.assertFalse(ce.title == 'Example CE1', 'edit not saved to db')
        self.assertEqual(ce.last_modified_by, 'Tester', 'Last modified by not updated')
        self.assertEqual(response.status_code, 200, 'New page not shown')
        html = response.content.decode('utf8')
        self.assertIn('BAM', html, 'new page not rendered')

    def test_valid_edit_page_POST_response_change_description_not_title(self):
        # CE model should be updated, a new one shouldn't be created
        response = self.client.post(reverse('CE:edit', args='1'), {'title' : 'Example CE1',
                                                                   'participation': 'minimal',
                                                                   'description': 'pretty easy'},
                                    follow=True)
        self.assertTemplateUsed('CE/edit_CE.html')
        self.assertEqual(response.redirect_chain[0][1], 302, 'No redirect following POST')
        ce = models.CultureEvent.objects.get(pk=1)
        self.assertEqual(ce.title, 'Example CE1', 'edit not saved to db')
        self.assertEqual(ce.description, 'pretty easy', 'edit not saved to db')
        self.assertEqual(response.status_code, 200, 'New page not shown')
        html = response.content.decode('utf8')
        self.assertIn('Example CE1', html, 'new page not rendered')
        self.assertEqual(ce.last_modified_by, 'Tester', 'Last modified by not updated')

    def test_no_changes(self):
        # no changes should go through, but .db unchanged
        ce = models.CultureEvent.objects.get(pk=1)
        response = self.client.post(reverse('CE:edit', args='1'), {'title': 'Example CE1',
                                                                   'participation': 'Rhett did it',
                                                                   'description': 'A culture event happened',
                                                                   'differences' : 'Last time it was different'},
                                    follow=True)
        new_ce = models.CultureEvent.objects.get(pk=1)
        self.assertEqual(response.redirect_chain[0][1], 302, 'No redirect following POST')
        self.assertEqual(ce, new_ce)
        self.assertEqual(ce.title, new_ce.title)

    def test_changing_to_existing_CE_title(self):
        # should reject changing to an existing title
        ce = models.CultureEvent(title='Example CE2',
                                 description='A culture event happened',
                                 participation='Rhett did it',
                                 differences='Last time it was different')
        ce.save()
        response = self.client.post(reverse('CE:edit', args='2'), {'title': 'Example CE1',
                                                                   'participation': 'Rhett did it',
                                                                   'description': 'A culture event happened',
                                                                   'differences': 'Last time it was different'},
                                    follow=True)
        html = response.content.decode('utf8')
        self.assertIn('Culture event with this Title already exists', html, 'No title exists error message')
        self.assertEqual(models.CultureEvent.objects.get(pk=2).title, 'Example CE2')
        self.assertEqual(models.CultureEvent.objects.get(pk=1).title, 'Example CE1')


class NewCEPageTest(TestCase):
    def setUp(self):
        # have one model previously in .db
        ce = models.CultureEvent(title='Example CE1',
                                 description='A culture event happened',
                                 participation='Rhett did it',
                                 differences='Last time it was different')
        ce.save()

    def test_new_CE_page_GET_response(self):
        # blank form should be returned
        response = self.client.get(reverse('CE:new'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed('CE/new_CE.html')
        html = response.content.decode('utf8')
        self.assertIn('Create a new CE', html, 'page not rendered')
        self.assertIn('<form', html, 'form not rendered')
        self.assertIn('<label for="id_title">Title:</label>', html, 'form not rendered correctly')

    def test_valid_POST_response(self):
        # new CE should be created
        response = self.client.post(reverse('CE:new'), {
            'title' : 'A test CE',
            'description' : 'I\'m testing this CE'
        }, follow=True)
        self.assertTemplateUsed('CE/new_CE.html')
        self.assertEqual(response.redirect_chain[0][1], 302, 'No redirect following POST')
        ce = models.CultureEvent.objects.get(pk=2)
        self.assertEqual(ce.title, 'A test CE', 'new CE title not correct')
        self.assertEqual(ce.description, 'I\'m testing this CE', 'new CE description not correct')
        self.assertEqual('A test CE', ce.title, 'New CE not in database')
        self.assertEqual(response.status_code, 200, 'New page not shown')
        html = response.content.decode('utf8')
        self.assertIn('A test CE', html, 'new page not rendered')
        self.assertEqual(ce.last_modified_by, 'Tester', 'Last modified by not updated')

    def test_invalid_POST_repeated_title_response(self):
        # Form should be show again with error message
        response = self.client.post(reverse('CE:new'), {
            'title': 'Example CE1',
            'description': 'I\'m testing this CE'
        }, follow=True)
        self.assertTemplateUsed('CE/new_CE.html')
        html = response.content.decode('utf8')
        self.assertIn('Culture event with this Title already exists', html, 'No title exists error message')
        with self.assertRaises(models.CultureEvent.DoesNotExist):
            models.CultureEvent.objects.get(pk=2)

    def test_invalid_POST_no_title_response(self):
        # Form should be shown again with error message
        response = self.client.post(reverse('CE:new'), {
            'description': 'I\'m testing this CE'
        }, follow=True)
        self.assertTemplateUsed('CE/new_CE.html')
        html = response.content.decode('utf8')
        self.assertIn('This field is required', html, 'No field required error message')
        with self.assertRaises(models.CultureEvent.DoesNotExist):
            models.CultureEvent.objects.get(pk=2)

class UnloggedUserRedirect(TestCase):
    def test_redirected_from_edit_CE_page(self):
        response = self.client.get(reverse('CE:edit', args='1'), follow=True)
        self.assertTemplateUsed('CE/edit.html')
        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertEqual(response.status_code, 200,
                         'Unlogged User not redirected from edit CE page')
        self.assertRedirects(response, '/accounts/login/?next=/CE/1/edit')

    def test_redirected_from_new_CE_page(self):
        response = self.client.get(reverse('CE:new'), follow=True)
        self.assertTemplateUsed('CE/edit.html')
        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertEqual(response.status_code, 200,
                         'Unlogged User not redirected from edit CE page')
        self.assertRedirects(response, '/accounts/login/?next=/CE/new')

# Form tests
class CE_EditFormTests(TestCase):
    def test_valid_data(self):
        # form should be valid
        form_data = {'title' : 'An example CE',
                     'participation' : 'Steve was there',
                     'description' : 'We did culture',
                     'differences' : 'It went better than last time'}
        form = forms.CE_EditForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_title_missing_data(self):
        # title is a required field, form should be invalid
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
        # CE titles should be unique
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

