from django.test import TestCase
from django.core import exceptions
from CE import models, settings, OCM_categories


class CEModelTest(TestCase):
    def test_string_method(self):
        ce = models.CultureEvent(title='Example CE1')
        self.assertEqual(str(ce), 'Example CE1')

    def test_repeated_title_not_allowed(self):
        # CE titles should be unique
        ce = models.CultureEvent(title='Example CE1',
                                 description_plain_text='A first CE')
        ce.save()
        ce = models.CultureEvent(title='Example CE1',
                                 description_plain_text='A second CE')

        with self.assertRaises(exceptions.ValidationError):
            ce.save()

    def test_auto_hyperlink(self):
        settings.auto_cross_reference = True
        # create 1st CE
        ce = models.CultureEvent(title='Example CE1',
                                 description_plain_text='A first CE')
        ce.save()
        # create 2nd CE with a hyperlink intended
        description_two = 'A second CE, that references example ce1'
        ce = models.CultureEvent(title='Example CE2',
                                 description_plain_text=description_two)
        ce.save()
        self.assertEqual(description_two, ce.description_plain_text)
        self.assertIn('href', ce.description)

        # create 3rd CE with no hyperlinks intended
        description_three = 'A second CE, that references no other CEs'
        ce = models.CultureEvent(title='Example CE2',
                                 description_plain_text=description_three)
        self.assertEqual(description_three, ce.description_plain_text)
        self.assertNotIn('href', ce.description)

    def test_manual_hyperlink(self):
        settings.auto_cross_reference = False
        # create 1st CE
        ce = models.CultureEvent(title='Example CE1',
                                 description_plain_text='A first CE')
        ce.save()
        # create 2nd CE with a hyperlink intended
        description_two = 'A second CE, that references {example ce1}'
        ce = models.CultureEvent(title='Example CE2',
                                 description_plain_text=description_two)
        ce.save()
        self.assertEqual(description_two, ce.description_plain_text)
        self.assertIn('href', ce.description)

        # create 3rd CE with no hyperlinks intended
        description_three = 'A second CE, that doesn\'t {reference} example ce1'
        ce = models.CultureEvent(title='Example CE2',
                                 description_plain_text=description_three)
        self.assertEqual(description_three, ce.description_plain_text)
        self.assertNotIn('href', ce.description)

        # test invalid tags not shown
        self.assertIn('{reference}', ce.description_plain_text)
        self.assertNotIn('{reference}', ce.description)

    def test_no_auto_cross_reference_if_setting_disabled(self):
        settings.auto_cross_reference = False
        # create 1st CE
        ce = models.CultureEvent(title='Example CE1',
                                 description_plain_text='A first CE')
        ce.save()
        # create 2nd CE that shouldn't hyperlink
        ce = models.CultureEvent(title='Example CE2',
                                 description_plain_text='example ce1 should pass silently')
        ce.save()
        self.assertNotIn('href', ce.description, 'Html anchor auto added  despite settings')

    def test_invalid_HTML_removed(self):
        settings.auto_cross_reference = True
        # create 1st CE
        ce = models.CultureEvent(title='First CE',
                                 description_plain_text='<strong>Example CE1</strong>'
                                                        '<a href="Dodgywebsite.come">Click here</a>'
                                                        '<script>Nasty JS</script>')
        ce.save()
        # <script> removed
        self.assertIn('<script>', ce.description_plain_text)
        self.assertNotIn('<script>', ce.description)

        # <a> removed
        self.assertIn('<a href', ce.description_plain_text)
        self.assertNotIn('<a href', ce.description)

        # <strong> allowed
        settings.bleach_allowed = ['strong']
        self.assertIn('<strong>', ce.description_plain_text)
        self.assertIn('<strong>', ce.description)


class TextsModelTest(TestCase):
    def test_string_method(self):
        ce = models.CultureEvent(title='Example CE1')
        text = models.TextModel(ce=ce, phonetic_text='djaŋɡo', text_title='example text')
        self.assertEqual(str(text), 'example text')


# class PictureModelTest(TestCase):
    # def test_invalid_file_type(self):
    #     pic = models.PictureModel(picture='string')
    #     pic.save()
    #
    # def test_valid_upload(self):
    #     ce = models.CultureEvent(title='Test CE')
    #     ce.save()
    #     # image = SimpleUploadedFile('test_image.jpeg', b'file_content',
    #     #         #                                 content_type='image/jpeg')
    #     image = 'test_data/pic(1).JPG'  # requires a uploads folder in project dir
    #     pic = models.PictureModel(ce=ce, picture=image)
    #     pic.save()
    #     pic = models.PictureModel.objects.get(ce=ce)
    #     self.assertEqual(pic.picture, 'test_data/pic(1).JPG')



    # def test_string_method(self):
    #     pass

class TagTests(TestCase):
    def test_ocm_slug_dictionary(self):
        slug_list = OCM_categories._slugs
        self.assertIn('1-1', slug_list)
        self.assertEqual('Geography & Weather', slug_list['1-1'])
        self.assertIn('1-15', slug_list)
        self.assertEqual('Sky, Land & Water', slug_list['1-15'])
        self.assertIn('9-10', slug_list)
        self.assertNotIn('9-11', slug_list)

    def test_generate_OCM(self):
        OCM = OCM_categories.OCM
        self.assertEqual(OCM[0][0]['code'], '1-1')
        self.assertEqual(OCM[0][0]['slug'], '1-1-geography-weather')
        self.assertEqual(OCM[0][0]['name'], '1-1 Geography & Weather')

        self.assertEqual(OCM[2][4]['code'], '3-5')
        self.assertEqual(OCM[2][4]['name'], '3-5 National & Global Relationships')
        self.assertEqual(OCM[2][4]['slug'], '3-5-national-global-relationships')


    def test_ocm_tags_changed(self):
        # create a test CE
        ce = models.CultureEvent(title='Example CE1',
                                 description_plain_text='A first CE')
        ce.save()
        # call the custom tag parser to check it handles OCM tags, and leaves other things alone
        tags = OCM_categories.check_tags_for_OCM('What a tag, 1-1, 1-16')
        for tag in tags:
            ce.tags.add(tag)
        results = ce.tags.all().values()
        self.assertIn('What a tag', str(results))
        self.assertIn('1-16', str(results))
        self.assertIn('1-1 Geography & Weather', str(results))