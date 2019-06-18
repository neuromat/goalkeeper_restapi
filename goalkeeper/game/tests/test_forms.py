from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.test import TestCase
from django.urls import reverse

from game.forms import GoalkeeperGameForm
from game.models import GameConfig, GoalkeeperGame, Level

USER_USERNAME = 'user'
USER_PWD = 'mypassword'
USER_EMAIL = 'user@example.com'


class GameTest(TestCase):
    def setUp(self):
        """
        Configure authentication and variables to start each test
        """

        self.user = User.objects.create_user(username=USER_USERNAME, email=USER_EMAIL, password=USER_PWD)
        self.user.is_staff = True
        self.user.save()

        logged = self.client.login(username=USER_USERNAME, password=USER_PWD)
        self.assertEqual(logged, True)

        level = Level.objects.create(name=0)
        config = GameConfig.objects.create(level=level, code='bla', is_public=True, name='Bla', created_by=self.user)
        GoalkeeperGame.objects.create(config=config, phase=0, depth=2, number_of_directions=3, plays_to_relax=0,
                                      player_time=1.0, celebration_time=1.0, read_seq=True, final_score_board='short',
                                      play_pause=True, score_board=True, show_history=True)

    def test_valid_goalkeeper_game_form(self):
        data = {
            'config': 1,
            'phase': 1,
            'depth': 3,
            'number_of_directions': 3,
            'plays_to_relax': 0,
            'player_time': 1.0,
            'celebration_time': 1.0,
            'final_score_board': 'short',
            'read_seq': True,
            'play_pause': True,
            'score_board': True,
            'show_history': True,
        }
        form = GoalkeeperGameForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_goalkeeper_game_form(self):
        data = {
            'config': 1,
            'phase': 1,
            'depth': 3,
        }
        form = GoalkeeperGameForm(data=data)
        self.assertFalse(form.is_valid())

    def test_goalkeeper_game_new_invalid_form(self):
        data = {
            'config': 1,
            'phase': 1,
            'depth': 3,
            'action': 'save'
        }
        response = self.client.post(reverse("goalkeeper_game_new"), data)
        message = list(response.context.get('messages'))[0]
        self.assertEqual(message.tags, "warning")
        self.assertTrue("Information not saved." in message.message)

    def test_goalkeeper_game_update_invalid_form(self):
        game = GoalkeeperGame.objects.first()
        data = {
            'config': 1,
            'phase': 1,
            'depth': 4,
            'action': 'save'
        }
        response = self.client.post(reverse("goalkeeper_game_update", args=(game.id,)), data)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'Information not saved.')
