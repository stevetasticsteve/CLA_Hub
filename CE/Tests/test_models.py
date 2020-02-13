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
        ce = models.CultureEvent(title='Example',
                                 description_plain_text='A first CE')
        ce.save()
        # create 2nd CE with a hyperlink intended
        description_two = 'A second CE, that references example'
        ce = models.CultureEvent(title='Example CE2',
                                 description_plain_text=description_two)
        ce.save()
        self.assertEqual(description_two, ce.description_plain_text)
        self.assertIn('href', ce.description, 'no href in autolink')
        self.assertIn('<a href="example">Example</a>', ce.description, 'Anchor malformed')

        # create 3rd CE with no hyperlinks intended
        description_three = 'A second CE, that references no other CEs'
        ce = models.CultureEvent(title='Example CE2',
                                 description_plain_text=description_three)
        self.assertEqual(description_three, ce.description_plain_text)
        self.assertNotIn('href', ce.description)

    def test_auto_hyperlink_multi_word(self):
        settings.auto_cross_reference = True
        ce = models.CultureEvent(title='Reef fishing')
        ce.save()

        ce = models.CultureEvent(title='Example CE2',
                                 description_plain_text='reef fishing')
        ce.save()

        self.assertIn('href', ce.description, 'No link')
        self.assertIn('<a href="reef-fishing">Reef fishing</a>', ce.description, 'Link malformed')

    def test_auto_hyperlink_numbers(self):
        settings.auto_cross_reference = True
        ce = models.CultureEvent(title='Reef fishing 2')
        ce.save()

        ce = models.CultureEvent(title='Example CE2',
                                 description_plain_text='reef fishing 2')
        ce.save()

        self.assertIn('href', ce.description, 'No link')
        self.assertIn('<a href="reef-fishing-2">Reef fishing 2</a>', ce.description, 'Link malformed')

    def test_hyperlink_case_insensitive(self):
        settings.auto_cross_reference = True
        # create 1st CE
        ce = models.CultureEvent(title='Example CE1',
                                 description_plain_text='A first CE')
        ce.save()

        # All lower case
        # create 2nd CE with a hyperlink intended
        desc = 'A second CE, that references example ce1'
        ce = models.CultureEvent(title='Example CE2',
                                 description_plain_text=desc)
        ce.save()

        self.assertEqual(desc, ce.description_plain_text)
        self.assertIn('href', ce.description, 'All lower case doesn\'t autolink')
        ce = models.CultureEvent.objects.get(pk=2)
        # All upper case
        desc = 'A SECOND CE, THAT REFERENCES EXAMPLE CE1'
        ce.description_plain_text = desc
        ce.save()
        self.assertEqual(desc, ce.description_plain_text)
        self.assertIn('href', ce.description, 'All upper case doesn\'t autolink')
        # Mixed case
        desc = 'A second CE, that references Example CE1'
        ce.description_plain_text = desc
        ce.save()
        self.assertEqual(desc, ce.description_plain_text)
        self.assertIn('href', ce.description, 'Mixed case doesn\'t autolink')

    def test_hyperlink_accuracy(self):
        # Test to make sure auto hyperlink handles similar CE titles correctly
        ce = models.CultureEvent(title='A CE')
        ce.save()
        ce = models.CultureEvent(title='A CE longer')
        ce.save()
        ce = models.CultureEvent(title='A CE long')
        ce.save()
        ce = models.CultureEvent(title='A CE longer again')
        ce.save()
        desc = 'a ce was before a ce long, but after a ce longer and then a ce longer again happened'
        ce = models.CultureEvent(title='Test',
                                 description_plain_text=desc)
        ce.save()

        self.assertIn('href', ce.description, 'no hyperlinks')
        self.assertEqual(ce.description.count('href'), 4, 'Incorrect number of hyperlinks')

        # test for each link
        self.assertIn('<a href="a-ce">A CE</a>', ce.description, 'shortest link not present')
        self.assertIn('<a href="a-ce-long">A CE long</a>', ce.description, 'length 2 link not present')
        self.assertIn('<a href="a-ce-longer">A CE longer</a>', ce.description, 'length 3 link not present')
        self.assertIn('<a href="a-ce-longer-again">A CE longer again</a>', ce.description, 'longest link not present')

        # reverse the order stored in the .db
        desc = 'a ce longer again was before a ce longer, but not a long ce and certainly not a ce.'
        ce.description_plain_text = desc
        ce.save()
        # test for each link
        self.assertIn('<a href="a-ce">A CE</a>', ce.description, 'shortest link not present')
        self.assertIn('<a href="a-ce-long">A CE long</a>', ce.description, 'length 2 link not present')
        self.assertIn('<a href="a-ce-longer">A CE longer</a>', ce.description, 'length 3 link not present')
        self.assertIn('<a href="a-ce-longer-again">A CE longer again</a>', ce.description, 'longest link not present')

    def test_repeated_hyperlink(self):
        settings.auto_cross_reference = True
        # create 1st CE
        ce = models.CultureEvent(title='Test CE',
                                 description_plain_text='A first CE')
        ce.save()
        ce = models.CultureEvent(title='Example CE2',
                                 description_plain_text='I\'m linking test CE twice by saying test CE again')
        ce.save()

        self.assertEqual(ce.description.count('href'), 2, 'Incorrect number of hyperlinks')
        self.assertEqual(ce.description, 'I\'m linking <a href="test-ce">Test CE1</a> twice by saying '
                                         '<a href="test-ce1">Test CE</a> again',
                         'Repeated hyperlink not displaying correctly')

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
                                 description_plain_text='<strong>Some text</strong>'
                                                        '<a href="Dodgywebsite.come">Click here</a>'
                                                        '<script>Nasty JS</script>')
        ce.save()
        # <script> removed
        self.assertIn('<script>', ce.description_plain_text)
        self.assertNotIn('<script>', ce.description, '<scripts> were not removed')

        # <a> removed
        self.assertIn('<a href', ce.description_plain_text)
        self.assertNotIn('<a href', ce.description, 'An anchor tag was allowed, it shouldn\'t have been')

        # <strong> allowed
        settings.bleach_allowed = ['strong']
        self.assertIn('<strong>', ce.description_plain_text)
        self.assertIn('<strong>', ce.description, 'Allowable HTML was removed')


class TextsModelTest(TestCase):
    def test_string_method(self):
        ce = models.CultureEvent(title='Example CE1')
        text = models.Text(ce=ce, phonetic_text='djaŋɡo', text_title='example text')
        self.assertEqual(str(text), 'example text')


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