from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User

import CE.settings


class test_login(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        credentials = User(username='Tester')
        credentials.set_password('secure_password')
        credentials.save()

    def test_unlogged_user_redirected_from_new_CE_page(self):
        response = self.client.get(reverse('CE:new'), follow=True)
        self.assertTemplateUsed('CE/edit.html')
        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertEqual(response.status_code, 200,
                         'Unlogged User not redirected from edit CE page')
        self.assertRedirects(response, '/accounts/login/?next=/CE/new')

    def test_unlogged_user_can_access_home_page(self):
        response = self.client.get(reverse('CE:home_page'))
        self.assertEqual(response.status_code, 200)

    def test_unlogged_user_redirected_if_login_everywhere(self):
        # check the conditional login decorator works if login everywhere is true
        CE.settings.login_everywhere = True #todo this style of adjusting settings doesnt work
        response = self.client.get(reverse('CE:home_page'), follow=True)
        self.assertRedirects(response, '/accounts/login/?next=/CE')