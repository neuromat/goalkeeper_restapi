from django.test import TestCase
from django.forms import ValidationError
from .forms import UserForm

from .views import *

USER_USERNAME = 'user'
USER_PWD = 'mypassword'
USER_EMAIL = 'user@example.com'


class UserFormTests(TestCase):

    def test_user_form_is_valid(self):
        form_data = {'username': USER_USERNAME,
                     'email': USER_EMAIL,
                     'password1': USER_PWD,
                     'password2': USER_PWD}
        form = UserForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_user_form_is_invalid_without_username(self):
        form_data = {'email': USER_EMAIL,
                     'password1': USER_PWD,
                     'password2': USER_PWD}
        form = UserForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_user_form_is_invalid_without_confirm_password(self):
        form_data = {'username': USER_USERNAME,
                     'password1': USER_PWD}
        form = UserForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_user_form_is_invalid_without_password(self):
        form_data = {'username': USER_USERNAME}
        form = UserForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_user_form_is_invalid_with_different_passwords(self):
        form_data = {'username': USER_USERNAME,
                     'email': USER_EMAIL,
                     'password1': USER_PWD,
                     'password2': USER_PWD + "Test"}
        form = UserForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_clean_password(self):
        form_data = {'username': USER_USERNAME,
                     'email': USER_EMAIL,
                     'password1': USER_PWD,
                     'password2': USER_PWD}

        form = UserForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertNotEqual(form.clean_password(), USER_PWD)

    def test_clean_email_already_exists(self):
        form_data = {'username': USER_USERNAME,
                     'email': USER_EMAIL,
                     'password1': USER_PWD,
                     'password2': USER_PWD}

        form = UserForm(data=form_data)
        self.assertTrue(form.is_valid())
        form.save()

        form_data_2 = {'username': USER_USERNAME + "2",
                       'email': USER_EMAIL,
                       'password1': USER_PWD,
                       'password2': USER_PWD}
        form = UserForm(data=form_data_2)
        self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError)