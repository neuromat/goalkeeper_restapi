from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.urls import resolve, reverse
from django.test import TestCase

from game.views import goalkeeper_game_new, goalkeeper_game_view, goalkeeper_game_update, goalkeeper_game_list, \
    context_tree, available_context, game_config_new, game_config_list, game_config_view, game_config_update, \
    check_contexts_without_probability
from game.models import Context, GameConfig, GoalkeeperGame, Level, Probability

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

    def test_game_config_list_status_code(self):
        url = reverse('game_config_list')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/config_list.html')

    def test_game_config_list_url_resolves_game_config_list_view(self):
        view = resolve('/game/config/list/')
        self.assertEquals(view.func, game_config_list)

    def test_game_config_new_status_code(self):
        url = reverse('game_config_new')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/config.html')

    def test_game_config_new_url_resolves_game_config_new_view(self):
        view = resolve('/game/config/new/')
        self.assertEquals(view.func, game_config_new)

    # Review this test!
    # def test_game_config_new(self):
    #     url = reverse('game_config_new')
    #     self.data = {
    #         'level': 1,
    #         'code': 'flecha',
    #         'name': 'Flecha Loira',
    #         'action': 'save'
    #     }
    #     self.client.post(url, self.data)
    #     game = GameConfig.objects.filter(code='flecha')
    #     self.assertEqual(game.count(), 1)
    #     self.assertTrue(isinstance(game[0], GameConfig))

    def test_game_config_view_status_code(self):
        config = GameConfig.objects.first()
        response = self.client.get(reverse("game_config_view", args=(config.id,)))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/config.html')

    def test_game_config_view_url_resolves_game_config_view_view(self):
        view = resolve('/game/config/view/1/')
        self.assertEquals(view.func, game_config_view)

    def test_game_config_update_status_code(self):
        config = GameConfig.objects.first()
        response = self.client.get(reverse("game_config_update", args=(config.id,)))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/config.html')

    def test_game_config_update_url_resolves_game_config_update_view(self):
        view = resolve('/game/config/update/1/')
        self.assertEquals(view.func, game_config_update)

    def test_goalkeeper_game_list_status_code(self):
        url = reverse('goalkeeper_game_list')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/goalkeeper_game_list.html')

    def test_goalkeeper_game_list_url_resolves_goalkeeper_game_list_view(self):
        view = resolve('/game/goalkeeper/list/')
        self.assertEquals(view.func, goalkeeper_game_list)

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

    def test_context_tree_status_code(self):
        game = GoalkeeperGame.objects.first()
        response = self.client.get(reverse("context", args=(game.id,)))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/context.html')

    def test_context_tree_url_resolves_context_tree_view(self):
        view = resolve('/game/goalkeeper/context/1/')
        self.assertEquals(view.func, context_tree)

    def test_available_context(self):
        game = GoalkeeperGame.objects.first()
        available_contexts, context_not_analyzed = available_context(game.id)
        self.assertListEqual(available_contexts, ['0', '1', '2'])
        self.assertListEqual(context_not_analyzed, [])

    def test_context_tree(self):
        game = GoalkeeperGame.objects.first()
        self.data = {'goalkeeper': game.id, '0': 'True', '1': 'True', '2': 'True', 'action': 'save'}
        self.client.post(reverse("context", args=(game.id,)), self.data)
        self.assertEqual(Context.objects.count(), 3)
        context_list, context_not_analyzed = available_context(game.id)
        self.assertListEqual(context_list, [])
        self.assertFalse(context_not_analyzed.exists())

    def test_check_contexts_without_probability(self):
        game = GoalkeeperGame.objects.first()
        Context.objects.create(goalkeeper=game, path='0', is_context='True', analyzed=False)
        Context.objects.create(goalkeeper=game, path='1', is_context='True', analyzed=False)
        response = check_contexts_without_probability(game.id)
        self.assertEqual(response, '0')

    def test_check_contexts_without_probability_none(self):
        game = GoalkeeperGame.objects.first()
        response = check_contexts_without_probability(game.id)
        self.assertIsNone(response)
