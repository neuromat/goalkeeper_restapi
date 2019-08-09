from django.test import TestCase
from django.forms import ValidationError
from faker import Factory
from .forms import UserForm

from .views import *

USER_PWD = 'MyUnC0MmoNP@ssW0rD'


class UserFormTests(TestCase):
    def test_user_form_is_valid(self):
        form_data = {'username': self.create_faker_username(),
                     'email': self.create_faker_email(),
                     'password1': USER_PWD,
                     'password2': USER_PWD,
                     'password': USER_PWD}
        form = UserForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_user_form_is_invalid_without_username(self):
        form_data = {'email': self.create_faker_email(),
                     'password1': USER_PWD,
                     'password2': USER_PWD,
                     'password': USER_PWD}
        form = UserForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_user_form_is_invalid_without_confirm_password(self):
        form_data = {'username': self.create_faker_username(),
                     'password1': USER_PWD,
                     'password': USER_PWD}
        form = UserForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_user_form_is_invalid_without_password(self):
        form_data = {'username': self.create_faker_username()}
        form = UserForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_user_form_is_invalid_with_different_passwords(self):
        form_data = {'username': self.create_faker_username(),
                     'email': self.create_faker_email(),
                     'password1': USER_PWD,
                     'password2': USER_PWD + "Test",
                     'password': USER_PWD}
        form = UserForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_clean_password(self):
        form_data = {'username': self.create_faker_username(),
                     'email': self.create_faker_email(),
                     'password1': USER_PWD,
                     'password2': USER_PWD,
                     'password': USER_PWD}

        form = UserForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertNotEqual(form.clean_password(), USER_PWD)

    def test_clean_email_already_exists(self):
        form_data = {'username': self.create_faker_username(),
                     'email': self.create_faker_email(),
                     'password1': USER_PWD,
                     'password2': USER_PWD,
                     'password': USER_PWD}

        form = UserForm(data=form_data)
        self.assertTrue(form.is_valid())
        form.save()

        form_data_2 = {'username': self.create_faker_username() + "2",
                       'email': form_data.get("email"),
                       'password1': USER_PWD,
                       'password2': USER_PWD,
                       'password': USER_PWD}
        form2 = UserForm(data=form_data_2)
        self.assertFalse(form2.is_valid())
        self.assertRaises(ValidationError)

    @staticmethod
    def create_faker_email():
        faker = Factory.create()
        return faker.email()

    @staticmethod
    def create_faker_username():
        faker = Factory.create()
        return faker.word()
