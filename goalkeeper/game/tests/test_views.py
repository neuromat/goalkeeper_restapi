from django.contrib.auth.models import User
from django.urls import resolve, reverse
from django.test import TestCase

from game.views import goalkeeper_game_new, goalkeeper_game_view, goalkeeper_game_update
from game.models import GameConfig, GoalkeeperGame, Institution, Level

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

        institution = Institution.objects.create(name='NeuroMat')
        level = Level.objects.create(name=0)
        config = GameConfig.objects.create(institution=institution, code='teste', is_public=True, name='Teste')
        GoalkeeperGame.objects.create(config=config, level=level, phase=0, depth=2, number_of_directions=3,
                                      plays_to_relax=0, player_time=1.0, celebration_time=1.0, read_seq=True,
                                      final_score_board='short', play_pause=True, score_board=True, show_history=True)

    def test_goalkeeper_game_new_status_code(self):
        url = reverse('goalkeeper_game_new')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/goalkeeper_game.html')

    def test_goalkeeper_game_new_url_resolves_goalkeeper_game_new_view(self):
        view = resolve('/game/goalkeeper/new/')
        self.assertEquals(view.func, goalkeeper_game_new)

    def test_goalkeeper_game_new(self):
        url = reverse('goalkeeper_game_new')
        self.data = {
            'config': 1,
            'level': 1,
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
            'action': 'save'
        }
        self.client.post(url, self.data)
        game = GoalkeeperGame.objects.filter(depth=3)
        self.assertEqual(game.count(), 1)
        self.assertTrue(isinstance(game[0], GoalkeeperGame))

    def test_goalkeeper_game_view_status_code(self):
        game = GoalkeeperGame.objects.first()
        response = self.client.get(reverse("goalkeeper_game_view", args=(game.id,)))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/goalkeeper_game.html')

    def test_goalkeeper_game_view_url_resolves_goalkeeper_game_view_view(self):
        view = resolve('/game/goalkeeper/view/1/')
        self.assertEquals(view.func, goalkeeper_game_view)

    def test_goalkeeper_game_view_remove(self):
        game = GoalkeeperGame.objects.first()
        self.data = {
            'action': 'remove'
        }
        response = self.client.post(reverse("goalkeeper_game_view", args=(game.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(GoalkeeperGame.objects.count(), 0)

    def test_goalkeeper_game_update_status_code(self):
        game = GoalkeeperGame.objects.first()
        response = self.client.get(reverse("goalkeeper_game_update", args=(game.id,)))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/goalkeeper_game.html')

    def test_goalkeeper_game_update_url_resolves_goalkeeper_game_update_view(self):
        view = resolve('/game/goalkeeper/update/1/')
        self.assertEquals(view.func, goalkeeper_game_update)

    def test_goalkeeper_game_update(self):
        game = GoalkeeperGame.objects.first()
        self.data = {
            'config': 1,
            'level': 1,
            'phase': 1,
            'depth': 4,
            'number_of_directions': 3,
            'plays_to_relax': 0,
            'player_time': 2.0,
            'celebration_time': 1.0,
            'final_score_board': 'short',
            'read_seq': False,
            'play_pause': True,
            'score_board': True,
            'show_history': True,
            'action': 'save'
        }
        response = self.client.post(reverse("goalkeeper_game_update", args=(game.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        game_update = GoalkeeperGame.objects.filter(depth=4, read_seq=False)
        self.assertEqual(game_update.count(), 1)
