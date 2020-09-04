from django.test import TestCase

from people import models


class PeopleModelTest(TestCase):
    def setUp(self):
        person1 = models.Person(name='Steve', village='1')
        person1.save()

    def test_family_description_hyperlinks(self):
        person2 = models.Person(name='Gerdine', village='1',
                                family_plain_text='Husband : 1')
        person2.save()

        person2 = models.Person.objects.get(pk=2)
        self.assertIn('Steve', person2.family)
        self.assertIn('<a', person2.family)
        self.assertEqual('Husband : 1', person2.family_plain_text)

    def test_out_of_range_family_hyperlink(self):
        person2 = models.Person(name='Gerdine', village='1',
                                family_plain_text='Husband : 3')
        person2.save()

        person2 = models.Person.objects.get(pk=2)
        self.assertNotIn('<a', person2.family)
        self.assertEqual(person2.family, 'Husband : 3')

    def test_multiple_hyperlinks(self):
        for i in range(20):
            person = models.Person(name='Person %d' % i, village='1')
            person.save()

        person = models.Person.objects.get(pk=2)
        person.family_plain_text = 'Children 2, 12'
        person.save()
        self.assertIn('<a href="2"', person.family)
        self.assertIn('<a href="12"', person.family)

        person = models.Person.objects.get(pk=2)
        person.family_plain_text = 'Children 12, 2'
        person.save()

        self.assertIn('<a href="2"', person.family)
        self.assertIn('<a href="12"', person.family)

    def test_repeated_pk(self):
        person2 = models.Person(name='Gerdine', village='1',
                                family_plain_text='Husband: 1, Bestie: 1')
        person2.save()

        self.assertEqual(models.Person.objects.get(pk=2).family,
                         'Husband:<a href="1"> Steve</a>, Bestie:<a href="1"> Steve</a>')

    def test_no_space_no_match(self):
        person2 = models.Person(name='Gerdine', village='1',
                                family_plain_text='Husband :1')
        person2.save()

        self.assertNotIn('<a href', models.Person.objects.get(pk=2).family)

    def test_repeated_integer_correct_match(self):
        """If family had both 2 and 22 as intended links the 2 in 22 was being replaced"""
        for i in range(30):
            person = models.Person(name='Person %d' % i, village='1')
            person.save()
        person = models.Person.objects.get(pk=2)

        person.family_plain_text = 'Children 22, 2'
        person.save()
        self.assertIn('<a href="2"', person.family, 'family hyperlinks aren\'t working (largest first)')
        self.assertIn('<a href="22"', person.family, 'family hyperlinks aren\'t working (largest first)')

        person.family_plain_text = 'Children 2, 22'
        person.save()
        self.assertIn('<a href="2"', person.family, 'family hyperlinks aren\'t working (smallest first)')
        self.assertIn('<a href="22"', person.family, 'family hyperlinks aren\'t working (smallest first)')
