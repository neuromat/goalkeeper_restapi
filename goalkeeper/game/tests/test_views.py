from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.urls import resolve, reverse
from django.test import TestCase

from game.views import goalkeeper_game_new, goalkeeper_game_view, goalkeeper_game_update, goalkeeper_game_list, \
    context_tree, available_context, game_config_new
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

    def test_game_config_new_status_code(self):
        url = reverse('game_config_new')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/config.html')

    def test_game_config_new_url_resolves_game_config_new_view(self):
        view = resolve('/game/config/new/')
        self.assertEquals(view.func, game_config_new)

    def test_game_config_new(self):
        url = reverse('game_config_new')
        self.data = {
            'config': 1,
            'phase': 1,
            'depth': 3,
            'action': 'save'
        }
        self.client.post(url, self.data)
        game = GoalkeeperGame.objects.filter(depth=3)
        self.assertEqual(game.count(), 1)
        self.assertTrue(isinstance(game[0], GoalkeeperGame))

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
        self.assertTemplateUsed(response, 'game/probability.html')

    def test_context_tree_url_resolves_context_tree_view(self):
        view = resolve('/game/goalkeeper/context/1/')
        self.assertEquals(view.func, context_tree)

    def test_available_context(self):
        game = GoalkeeperGame.objects.first()
        available_contexts = available_context(game.id)
        self.assertListEqual(available_contexts, ['0', '1', '2'])

    def test_new_context_tree(self):
        game = GoalkeeperGame.objects.first()
        self.data = {
            'goalkeeper': game.id,
            'path': '0',
            'context-0': 1,
            'context-1': 0,
            'context-2': 0,
            'action': 'save'
        }
        response = self.client.post(reverse("context", args=(game.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        new_context = Context.objects.filter(path='0')
        self.assertEqual(new_context.count(), 1)
        probabilities = Probability.objects.filter(context=new_context[0].id)
        self.assertEqual(probabilities.count(), 3)

    def test_context_tree_wrong_probabilities(self):
        game = GoalkeeperGame.objects.first()
        self.data = {
            'goalkeeper': game.id,
            'path': '0',
            'context-0': .5,
            'context-1': .5,
            'context-2': .3,
            'action': 'save'
        }
        response = self.client.post(reverse("context", args=(game.id,)), self.data)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), 'The sum of the probabilities must be equal to 1.')

    def test_context_tree_completed(self):
        """
        Testing the following full context tree:
        2  - {0: 0.3, 1: 0.3 , 2: 0.4}
        20 - {0: 1, 1: 0 , 2: 0}
        00 - {0: 0, 1: 1 , 2: 0}
        21 - {0: 0.5, 1: 0 , 2: 0.5}
        01 - {0: 0, 1: 0 , 2: 1}
        10 - {0: 0, 1: 0 , 2: 1}
        """
        game = GoalkeeperGame.objects.first()

        self.data1 = {'goalkeeper': game.id, 'path': '2', 'context-0': 0.3, 'context-1': 0.3, 'context-2': 0.4,
                      'action': 'save'}
        self.client.post(reverse("context", args=(game.id,)), self.data1)
        available_contexts = available_context(game.id)
        self.assertListEqual(available_contexts, ['0', '1', '20', '21'])

        self.data2 = {'goalkeeper': game.id, 'path': '20', 'context-0': 1, 'context-1': 0, 'context-2': 0,
                      'action': 'save'}
        self.client.post(reverse("context", args=(game.id,)), self.data2)
        available_contexts = available_context(game.id)
        self.assertListEqual(available_contexts, ['00', '1', '200', '21'])

        self.data3 = {'goalkeeper': game.id, 'path': '00', 'context-0': 0, 'context-1': 1, 'context-2': 0,
                      'action': 'save'}
        self.client.post(reverse("context", args=(game.id,)), self.data3)
        available_contexts = available_context(game.id)
        self.assertListEqual(available_contexts, ['001', '01', '1', '21'])

        self.data4 = {'goalkeeper': game.id, 'path': '21', 'context-0': .5, 'context-1': 0, 'context-2': .5,
                      'action': 'save'}
        self.client.post(reverse("context", args=(game.id,)), self.data4)
        available_contexts = available_context(game.id)
        self.assertListEqual(available_contexts, ['001', '01', '10', '210'])

        self.data5 = {'goalkeeper': game.id, 'path': '01', 'context-0': 0, 'context-1': 0, 'context-2': 1,
                      'action': 'save'}
        self.client.post(reverse("context", args=(game.id,)), self.data5)
        available_contexts = available_context(game.id)
        self.assertListEqual(available_contexts, ['10', '210'])

        self.data6 = {'goalkeeper': game.id, 'path': '10', 'context-0': 0, 'context-1': 0, 'context-2': 1,
                      'action': 'save'}
        response = self.client.post(reverse("context", args=(game.id,)), self.data6, follow=True)
        self.assertRedirects(response, '/game/goalkeeper/view/1/')
        available_contexts = available_context(game.id)
        self.assertListEqual(available_contexts, [])

    def test_remove_path_from_goalkeeper_game_view(self):
        game = GoalkeeperGame.objects.first()
        Context.objects.create(goalkeeper=game, path='0')
        self.assertEqual(Context.objects.count(), 1)
        self.data = {
            'goalkeeper': game,
            'action': 'remove_path-1'
        }
        self.client.post(reverse("goalkeeper_game_view", args=(game.id,)), self.data)
        self.assertEqual(Context.objects.count(), 0)

    def test_remove_path_from_context_tree(self):
        game = GoalkeeperGame.objects.first()
        Context.objects.create(goalkeeper=game, path='0')
        self.assertEqual(Context.objects.count(), 1)
        self.data = {
            'goalkeeper': game,
            'action': 'remove_path-1'
        }
        self.client.post(reverse("context", args=(game.id,)), self.data)
        self.assertEqual(Context.objects.count(), 0)
