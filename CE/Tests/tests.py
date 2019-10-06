from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from unittest import skip

import CLAHub.base_settings

class TestLogin(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        credentials = User(username='Tester')
        credentials.set_password('secure_password')
        credentials.save()

    def test_unlogged_user_redirected_from_new_CE_page(self):
        response = self.client.get(reverse('CE:new'), follow=True)
        self.assertTemplateUsed('CE/new_CE.html')
        self.assertEqual(response.redirect_chain[0][1], 302)
        self.assertEqual(response.status_code, 200,
                         'Unlogged User not redirected from new CE page')
        self.assertRedirects(response, '/accounts/login/?next=/CE/new')

    def test_logged_user_can_access_new_CE_page(self):
        self.client.login(username='Tester', password='secure_password')
        response = self.client.get(reverse('CE:new'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['user'].username, 'Tester')

    def test_unlogged_user_can_access_home_page(self):
        self.assertFalse(CLAHub.base_settings.LOGIN_EVERYWHERE)
        response = self.client.get(reverse('CE:home_page'))
        self.assertEqual(response.status_code, 200)

    @skip
    def test_unlogged_user_redirected_if_login_everywhere(self):
        # check the conditional login decorator works if login everywhere is true
        CLAHub.base_settings.LOGIN_EVERYWHERE = True
        self.assertTrue(CLAHub.base_settings.LOGIN_EVERYWHERE, 'Test settings incorrect')
        response = self.client.get(reverse('CE:home_page'), follow=True)
        # self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=/CE/')
        #todo can't get redirect to work

    def test_logged_user_can_access_homepage_if_login_everywhere(self):
        pass



