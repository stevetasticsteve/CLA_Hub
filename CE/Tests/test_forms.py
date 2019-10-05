from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from CE import forms


class CE_EditFormTests(TestCase):

    def test_valid_data(self):
        # form should be valid
        form_data = {'title' : 'An example CE',
                     'description_plain_text' : 'We did culture',
                     'differences' : 'It went better than last time',
                     'date': '2019-08-06'}
        form = forms.CE_EditForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_title_missing_data(self):
        # title is a required field, form should be invalid
        form_data = {'description_plain_text' : 'We did culture',
                     'differences' : 'It went better than last time'}
        form = forms.CE_EditForm(data=form_data)
        self.assertFalse(form.is_valid())


class PictureUploadForm(TestCase):
    #todo test still useful, but needs refactored, form was rolled into standard form
    def test_valid_data(self):
        with open('CLAHub/assets/test_data/test_pic1.JPG', 'rb') as file:
            file = file.read()
            test_image = SimpleUploadedFile('test_data/test_pic1.JPG', file, content_type='image')
        form_data = {'title': 'Test CE',
                     'date': '2019-02-20',
                     'picture': test_image}
        form = forms.CE_EditForm(data=form_data)
        form.full_clean()
        self.assertTrue(form.is_valid())

# class ParticipationFormsetTest(TestCase):
#     def test_date_missing(self):
#         form_data = {
#             'team_participants':'Steve',
#             'national_participants':'Ulumo'
#         }
#         formset = forms.participant_formset(data=form_data)
#         for form in formset:
#             self.assertFalse(form.is_valid)

#     def test_not_a_picture_file(self):
# todo a text file counts as valid image? Rejected at model level, not form level
#         with open('readme.md', 'rb') as file:
#             file = file.read()
#             test_image = SimpleUploadedFile('readme.md', file, content_type='text')
#         form_data = {'ce': models.CultureEvent(),
#                      'picture': test_image}
#         form = forms.PictureUploadForm(data=form_data)
#         form.full_clean()
#         self.assertFalse(form.is_valid())