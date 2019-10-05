
# class TestEditPage(TestCase):
#     @classmethod
#     def setUpClass(cls):
#         super().setUpClass()
#         credentials = User(username='Tester')
#         credentials.set_password('secure_password')
#         credentials.save()
#
#     def setUp(self):
#         self.client.login(username='Tester', password='secure_password')
#         ce = models.CultureEvent(title='Example CE1',
#                                  description='A culture event happened',
#                                  participation='Rhett did it',
#                                  differences='Last time it was different')
#         ce.save()
#         text = models.TextModel(ce=models.CultureEvent.objects.get(pk=1),
#                             audio='musicFile.ogg',
#                             phonetic_text='foᵘnɛtɪks',
#                             orthographic_text='orthographic')
#         text.save()
#
#     def test_edit_page_GET_response(self):
#         # Form should populate with database data
#         response = self.client.get(reverse('CE:edit', args='1'))
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed('CE/edit_CE.html')
#         html = response.content.decode('utf8')
#         self.assertContains(response, '<form')
#         # check form contents
#         self.assertContains(response, 'value="Example CE1"')
#         self.assertContains(response, 'Rhett did it')
#
#     def test_valid_edit_page_POST_response_change_everything(self):
#         # CE model should be updated, a new one shouldn't be created
#         response = self.client.post(reverse('CE:edit', args='1'), {'title' : 'BAM',
#                                                                    'participation' : 'minimal',
#                                                                    'description' : 'pretty easy'},
#                                     follow=True)
#         self.assertTemplateUsed('CE/edit_CE.html')
#         self.assertEqual(response.redirect_chain[0][1], 302, 'No redirect following POST')
#         ce = models.CultureEvent.objects.get(pk=1)
#         self.assertEqual(ce.title, 'BAM', 'edit not saved to db')
#         self.assertFalse(ce.title == 'Example CE1', 'edit not saved to db')
#         self.assertEqual(ce.last_modified_by, 'Tester', 'Last modified by not updated')
#         self.assertEqual(response.status_code, 200, 'New page not shown')
#         self.assertContains(response, 'BAM')
#
#     def test_valid_edit_page_POST_response_change_description_not_title(self):
#         # CE model should be updated, a new one shouldn't be created
#         response = self.client.post(reverse('CE:edit', args='1'), {'title' : 'Example CE1',
#                                                                    'participation': 'minimal',
#                                                                    'description': 'pretty easy'},
#                                     follow=True)
#         self.assertTemplateUsed('CE/edit_CE.html')
#         self.assertEqual(response.redirect_chain[0][1], 302, 'No redirect following POST')
#         ce = models.CultureEvent.objects.get(pk=1)
#         self.assertEqual(ce.title, 'Example CE1', 'edit not saved to db')
#         self.assertEqual(ce.description, 'pretty easy', 'edit not saved to db')
#         self.assertEqual(response.status_code, 200, 'New page not shown')
#         self.assertContains(response, 'Example CE1')
#         self.assertEqual(ce.last_modified_by, 'Tester', 'Last modified by not updated')
#
#     def test_edit_page_no_changes(self):
#         # no changes should go through, but .db unchanged
#         ce = models.CultureEvent.objects.get(pk=1)
#         response = self.client.post(reverse('CE:edit', args='1'), {'title': 'Example CE1',
#                                                                    'participation': 'Rhett did it',
#                                                                    'description': 'A culture event happened',
#                                                                    'differences' : 'Last time it was different'},
#                                     follow=True)
#         new_ce = models.CultureEvent.objects.get(pk=1)
#         self.assertEqual(response.redirect_chain[0][1], 302, 'No redirect following POST')
#         self.assertEqual(ce, new_ce)
#         self.assertEqual(ce.title, new_ce.title)
#
#     def test_edit_page_changing_to_existing_CE_title(self):
#         # should reject changing to an existing title
#         ce = models.CultureEvent(title='Example CE2',
#                                  description='A culture event happened',
#                                  participation='Rhett did it',
#                                  differences='Last time it was different')
#         ce.save()
#         response = self.client.post(reverse('CE:edit', args='2'), {'title': 'Example CE1',
#                                                                    'participation': 'Rhett did it',
#                                                                    'description': 'A culture event happened',
#                                                                    'differences': 'Last time it was different'},
#                                     follow=True)
#         self.assertContains(response, 'Culture event with this Title already exists')
#         self.assertEqual(models.CultureEvent.objects.get(pk=2).title, 'Example CE2')
#         self.assertEqual(models.CultureEvent.objects.get(pk=1).title, 'Example CE1')


