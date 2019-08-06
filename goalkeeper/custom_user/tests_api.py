from rest_framework.test import APITestCase, APIClient
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
import json

from .api.viewsets import UserAPI, GetAuthToken
from .api.serializers import UserSerializer
from .models import Profile
from faker import Factory

USERNAME = "teste"
PASSWORD = 'psswrd12'
EMAIL = "teste@email.com"

class CustomUserTestCase(APITestCase):

    # Todos os endpoints utilizam as views corretas
    def test_resolves_user_url(self):
        resolver = self.resolve_by_name('user')

        self.assertEqual(resolver.func.cls, UserAPI)

    def test_resolves_user_detail_url(self):
        resolver = self.resolve_by_name('user', pk=1)

        self.assertEqual(resolver.func.cls, UserAPI)

    def test_resolves_get_auth_token_url(self):
        resolver = self.resolve_by_name('get_auth_token')

        self.assertEqual(resolver.func.cls, GetAuthToken)

    @staticmethod
    def resolve_by_name(name, **kwargs):
        url = reverse(name, kwargs=kwargs)
        return resolve(url)


class UserAPITestCase(APITestCase):
    @staticmethod
    def user_data_json():
        return json.dumps({'username': USERNAME, 'email': EMAIL, 'password': PASSWORD, 'id': None})

    def test_post_creates_new_user(self):
        response = self.client.post(reverse('user'), data=self.user_data_json(), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 1)

    def test_success_in_delete_user(self):
        faker = Factory.create()
        user = User.objects.create_user(username=USERNAME, email=EMAIL, password=PASSWORD)
        user2 = User.objects.create_user(username=faker.text(max_nb_chars=15), password=PASSWORD)

        self.client.login(username=user2.username, password=PASSWORD)

        self.assertEqual(User.objects.count(), 2)
        response = self.client.delete(
            reverse('user', kwargs={'pk': user.id}),
            data=self.user_data_json(),
            content_type='application/json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(User.objects.count(), 1)

    def test_failure_in_delete_user(self):
        faker = Factory.create()
        user = User.objects.create_user(username=USERNAME, email=EMAIL, password=PASSWORD+"teste")
        user2 = User.objects.create_user(username=faker.text(max_nb_chars=15), password=PASSWORD)

        self.client.login(username=user2.username, password=PASSWORD)

        self.assertEqual(User.objects.count(), 2)
        response = self.client.delete(
            reverse('user', kwargs={'pk': user.id}),
            data=self.user_data_json(),
            content_type='application/json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(User.objects.count(), 2)


class GetAuthTokenTestCase(APITestCase):
    @staticmethod
    def login_data_json():
        return json.dumps({'username': USERNAME, 'password': PASSWORD})

    def test_post_creates_new_token(self):
        User.objects.create_user(username=USERNAME, password=PASSWORD)

        tokens_before = Token.objects.count()
        response = self.client.post(
            reverse('get_auth_token'),
            data=self.login_data_json(),
            content_type='application/json')
        tokens_after = Token.objects.count()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(tokens_before, tokens_after-1)