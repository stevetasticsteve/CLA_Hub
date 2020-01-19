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