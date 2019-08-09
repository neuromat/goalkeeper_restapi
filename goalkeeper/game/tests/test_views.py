from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.urls import resolve, reverse
from django.test import TestCase
from faker import Factory

from game.views import goalkeeper_game_new, goalkeeper_game_view, goalkeeper_game_update, goalkeeper_game_list, \
    context_tree, available_context, game_config_new, game_config_list, game_config_view, game_config_update, \
    check_contexts_without_probability, probability, probability_update
from game.models import Context, GameConfig, GoalkeeperGame, Level, Probability, WarmUp, Game
from .tests_api import CommonFunctionsToGameTests
from rest_framework.authtoken.models import Token

USER_USERNAME = 'user'
USER_PWD = 'mypassword'
USER_EMAIL = 'user@example.com'


class GameTest(TestCase, CommonFunctionsToGameTests):
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
        config = GameConfig.objects.create(level=level, code='bla', is_public='yes', name='Bla', created_by=self.user)
        GoalkeeperGame.objects.create(config=config, phase=0, depth=2, number_of_directions=3, number_of_plays=10,
                                      plays_to_relax=0, player_time=1.0, celebration_time=1.0, read_seq=True,
                                      final_score_board='short', play_pause=True, score_board=True, show_history=True)

    ######################
    # Home page
    ######################
    def test_home_status_code(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    ##############################
    # Filter graphics on Home page
    ##############################
    def test_select_kicker_to_filter_phase(self):
        game_config = self.create_game_configs(self.user)
        self.create_game_object(game_config, 1)

        response = self.client.get(reverse('select_kicker_to_filter_phase'), {'kicker': game_config.name})
        self.assertEquals(response.status_code, 200)
        self.assertEqual(Game.objects.count(), 2)

    ##############################
    # General
    ##############################
    def test_language_change(self):
        self.client.get(reverse('home'))
        response = self.client.get(reverse('language_change', kwargs={'language_code': 'pt-br'}),
                                   {'next': reverse('home')})
        self.assertEquals(response.status_code, 302)

    ######################
    # List game config
    ######################
    def test_game_config_list_status_code(self):
        url = reverse('game_config_list')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/config_list.html')

    def test_game_config_list_url_resolves_game_config_list_view(self):
        view = resolve('/game/config/list/')
        self.assertEquals(view.func, game_config_list)

    ######################
    # New game config
    ######################
    def test_game_config_new_status_code(self):
        url = reverse('game_config_new')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/config.html')

    def test_game_config_new_url_resolves_game_config_new_view(self):
        view = resolve('/game/config/new/')
        self.assertEquals(view.func, game_config_new)

    def test_game_config_new(self):
        level = Level.objects.first()
        url = reverse('game_config_new')
        self.data = {
            'level': level.pk,
            'code': 'flecha',
            'name': 'Flecha Loira',
            'is_public': 'no',
            'created_by': self.user,
            'action': 'save'
        }
        self.client.post(url, self.data)
        game = GameConfig.objects.filter(code='flecha')
        self.assertEqual(game.count(), 1)
        self.assertTrue(isinstance(game[0], GameConfig))

    def test_game_config_new_redirect(self):
        level = Level.objects.first()
        url = reverse('game_config_new')
        self.data = {
            'level': level.pk,
            'code': 'flecha',
            'name': 'Flecha Loira',
            'is_public': 'no',
            'created_by': self.user,
            'action': 'save',
            'next': url
        }
        self.client.post(url, self.data)
        game = GameConfig.objects.filter(code='flecha')
        self.assertEqual(game.count(), 1)
        self.assertTrue(isinstance(game[0], GameConfig))

    ######################
    # View game config
    ######################
    def test_game_config_view_status_code(self):
        config = GameConfig.objects.first()
        response = self.client.get(reverse("game_config_view", args=(config.id,)))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/config.html')

    def test_game_config_view_url_resolves_game_config_view_view(self):
        view = resolve('/game/config/view/1/')
        self.assertEquals(view.func, game_config_view)

    def test_game_config_view_can_not_remove_config_if_there_is_a_game_using_it(self):
        config = GameConfig.objects.first()
        self.data = {
            'action': 'remove'
        }
        response = self.client.post(reverse("game_config_view", args=(config.id,)), self.data)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), "This config can't be removed because there are games configured with it.")

    def test_game_config_view_remove_config(self):
        config = GameConfig.objects.first()
        GoalkeeperGame.objects.filter(config=config).delete()
        self.data = {
            'action': 'remove'
        }
        response = self.client.post(reverse("game_config_view", args=(config.id,)), self.data)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), "Kicker removed successfully.")
        self.assertEqual(len(GoalkeeperGame.objects.all()), 0)

    def test_game_config_view_fails_to_remove_config_if_game_attached(self):
        config = GameConfig.objects.first()
        self.data = {
            'action': 'remove'
        }
        response = self.client.post(reverse("game_config_view", args=(config.id,)), self.data)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), "This config can't be removed because there are games configured with it.")
        self.assertEqual(len(GoalkeeperGame.objects.all()), 1)

    ######################
    # Update game config
    ######################
    def test_game_config_update_status_code(self):
        config = GameConfig.objects.first()
        response = self.client.get(reverse("game_config_update", args=(config.id,)))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/config.html')

    def test_game_config_update_url_resolves_game_config_update_view(self):
        view = resolve('/game/config/update/1/')
        self.assertEquals(view.func, game_config_update)

    def test_game_config_update(self):
        config = GameConfig.objects.first()
        level = Level.objects.first()
        self.data = {
            'level': level.pk,
            'code': 'cambalhota',
            'name': 'cambalhota',
            'is_public': 'no',
            'created_by': self.user,
            'action': 'save'
        }
        response = self.client.post(reverse("game_config_update", args=(config.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        config_update = GameConfig.objects.filter(code='cambalhota')
        self.assertEqual(config_update.count(), 1)

    def test_game_config_update_no_changes(self):
        config = GameConfig.objects.first()
        level = Level.objects.first()
        self.data = {
            'level': level.pk,
            'code': 'bla',
            'name': 'Bla',
            'is_public': 'yes',
            'created_by': self.user,
            'action': 'save'
        }
        response = self.client.post(reverse("game_config_update", args=(config.id,)), self.data)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), "There are no changes to save.")

    ######################
    # List goalkeeper game
    ######################
    def test_goalkeeper_game_list_status_code(self):
        url = reverse('goalkeeper_game_list')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/goalkeeper_game_list.html')

    def test_goalkeeper_game_list_url_resolves_goalkeeper_game_list_view(self):
        view = resolve('/game/goalkeeper/list/')
        self.assertEquals(view.func, goalkeeper_game_list)

    ######################
    # New goalkeeper game
    ######################
    def test_goalkeeper_game_new_status_code(self):
        url = reverse('goalkeeper_game_new')
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/goalkeeper_game.html')

    def test_goalkeeper_game_new_url_resolves_goalkeeper_game_new_view(self):
        view = resolve('/game/goalkeeper/new/')
        self.assertEquals(view.func, goalkeeper_game_new)

    def test_goalkeeper_game_new(self):
        config = GameConfig.objects.first()
        url = reverse('goalkeeper_game_new')
        self.data = {
            'config': config.pk,
            'sequence': '',
            'depth': 3,
            'number_of_directions': 3,
            'number_of_plays': 10,
            'plays_to_relax': 0,
            'player_time': 1.0,
            'celebration_time': 1.0,
            'final_score_board': 'short',
            'read_seq': True,
            'play_pause': True,
            'score_board': True,
            'show_history': True,
            'create_seq_manually': 'no',
            'score': 10,
            'action': 'save'
        }
        self.client.post(url, self.data)
        game = GoalkeeperGame.objects.filter(depth=3)
        self.assertEqual(game.count(), 1)
        self.assertTrue(isinstance(game[0], GoalkeeperGame))

    def test_goalkeeper_game_new__with_sequence_created_manually(self):
        config = GameConfig.objects.first()
        url = reverse('goalkeeper_game_new')
        self.data = {
            'config': config.pk,
            'sequence': '',
            'depth': 3,
            'number_of_directions': 3,
            'number_of_plays': 10,
            'plays_to_relax': 0,
            'player_time': 1.0,
            'celebration_time': 1.0,
            'final_score_board': 'short',
            'read_seq': True,
            'play_pause': True,
            'score_board': True,
            'show_history': True,
            'create_seq_manually': 'yes',
            'score': 10,
            'sequence': '0121012',
            'action': 'save'
        }
        self.client.post(url, self.data)
        game = GoalkeeperGame.objects.filter(depth=3)
        self.assertEqual(game.count(), 1)
        self.assertTrue(isinstance(game[0], GoalkeeperGame))
        self.assertEqual(game[0].seq_step_det_or_prob, 'n'*len(game[0].sequence))

    def test_goalkeeper_game_new_phase_zero(self):
        level = Level.objects.first()
        config = GameConfig.objects.create(level=level, code='ops', is_public='yes', name='Ops', created_by=self.user)
        url = reverse('goalkeeper_game_new')
        self.data = {
            'config': config.pk,
            'sequence': '',
            'number_of_directions': 3,
            'number_of_plays': 10,
            'plays_to_relax': 0,
            'player_time': 1.0,
            'celebration_time': 1.0,
            'final_score_board': 'short',
            'read_seq': True,
            'play_pause': True,
            'score_board': True,
            'show_history': True,
            'create_seq_manually': 'no',
            'score': 10,
            'action': 'save'
        }
        self.client.post(url, self.data)
        game = GoalkeeperGame.objects.filter(config=config, phase=0)
        self.assertEqual(game.count(), 1)

    ######################
    # View goalkeeper game
    ######################
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

    def test_goalkeeper_game_view_remove_context(self):
        game = GoalkeeperGame.objects.first()
        context = Context.objects.create(goalkeeper=game, path='0', is_context='True', analyzed=False)
        self.data = {
            'action': 'remove_path-'+str(context.pk)
        }
        self.client.post(reverse("goalkeeper_game_view", args=(game.id,)), self.data)
        self.assertEqual(Context.objects.count(), 0)

    def test_goalkeeper_game_view_error_to_remove_context(self):
        game = GoalkeeperGame.objects.first()
        Context.objects.create(goalkeeper=game, path='0', is_context='True', analyzed=False)
        self.data = {
            'action': 'remove_path-0'
        }
        response = self.client.post(reverse("goalkeeper_game_view", args=(game.id,)), self.data)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), "Error trying to delete this context.")

    def test_goalkeeper_game_view_remove_context_with_is_context_not_true(self):
        game = GoalkeeperGame.objects.first()
        Context.objects.create(goalkeeper=game, path='0', is_context='Null', analyzed=False)
        Context.objects.create(goalkeeper=game, path='1', is_context='False', analyzed=False)
        context = Context.objects.create(goalkeeper=game, path='2', is_context='True', analyzed=False)
        self.data = {
            'action': 'remove_path-' + str(context.pk)
        }
        self.client.post(reverse("goalkeeper_game_view", args=(game.id,)), self.data)
        self.assertEqual(Context.objects.count(), 0)

    ########################
    # Update goalkeeper game
    ########################
    def test_goalkeeper_game_update_status_code(self):
        game = GoalkeeperGame.objects.first()
        response = self.client.get(reverse("goalkeeper_game_update", args=(game.id,)))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/goalkeeper_game.html')

    def test_goalkeeper_game_update_url_resolves_goalkeeper_game_update_view(self):
        view = resolve('/game/goalkeeper/update/1/')
        self.assertEquals(view.func, goalkeeper_game_update)

    def test_goalkeeper_game_update(self):
        config = GameConfig.objects.first()
        game = GoalkeeperGame.objects.first()
        self.data = {
            'config': config.pk,
            'sequence': '',
            'depth': 4,
            'number_of_directions': 3,
            'number_of_plays': 10,
            'plays_to_relax': 0,
            'player_time': 2.0,
            'celebration_time': 1.0,
            'final_score_board': 'short',
            'read_seq': False,
            'play_pause': True,
            'score_board': True,
            'show_history': True,
            'create_seq_manually': 'no',
            'score': 10,
            'action': 'save'
        }
        response = self.client.post(reverse("goalkeeper_game_update", args=(game.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        game_update = GoalkeeperGame.objects.filter(depth=4, read_seq=False)
        self.assertEqual(game_update.count(), 1)

    def test_goalkeeper_game_update_creating_sequence_manually(self):
        config = GameConfig.objects.first()
        game = GoalkeeperGame.objects.first()
        self.data = {
            'config': config.pk,
            'sequence': '',
            'depth': 4,
            'number_of_directions': 3,
            'number_of_plays': 10,
            'plays_to_relax': 0,
            'player_time': 2.0,
            'celebration_time': 1.0,
            'final_score_board': 'short',
            'read_seq': False,
            'play_pause': True,
            'score_board': True,
            'show_history': True,
            'create_seq_manually': 'yes',
            'sequence': '010201',
            'score': 10,
            'action': 'save'
        }
        response = self.client.post(reverse("goalkeeper_game_update", args=(game.id,)), self.data)
        self.assertEqual(response.status_code, 302)
        game_update = GoalkeeperGame.objects.filter(depth=4)
        self.assertEqual(game_update.count(), 1)
        self.assertEqual(game_update[0].seq_step_det_or_prob, 'n'*len(game_update[0].sequence))

    def test_goalkeeper_game_update_no_changes(self):
        config = GameConfig.objects.first()
        game = GoalkeeperGame.objects.first()
        self.data = {
            'config': config.pk,
            'sequence': '',
            'depth': 2,
            'number_of_directions': 3,
            'number_of_plays': 10,
            'plays_to_relax': 0,
            'player_time': 1.0,
            'celebration_time': 1.0,
            'final_score_board': 'short',
            'play_pause': True,
            'score_board': True,
            'show_history': True,
            'create_seq_manually': 'no',
            'score': 0,
            'action': 'save'
        }
        response = self.client.post(reverse("goalkeeper_game_update", args=(game.id,)), self.data)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), "There are no changes to save.")

    ########################
    # Function context tree
    ########################
    def test_context_tree_status_code(self):
        game = GoalkeeperGame.objects.first()
        response = self.client.get(reverse("context", args=(game.id,)))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/context.html')

    def test_context_tree_url_resolves_context_tree_view(self):
        view = resolve('/game/goalkeeper/context/1/')
        self.assertEquals(view.func, context_tree)

    def test_context_tree(self):
        game = GoalkeeperGame.objects.first()
        self.data = {
            'goalkeeper': game.id,
            '0': 'True',
            '1': 'True',
            '2': 'True',
            'action': 'save'
        }
        self.client.post(reverse("context", args=(game.id,)), self.data)
        self.assertEqual(Context.objects.count(), 3)
        context_list, context_not_analyzed = available_context(game.id)
        self.assertListEqual(context_list, [])
        self.assertFalse(context_not_analyzed.exists())

    def test_context_tree_depth_2(self):
        game = GoalkeeperGame.objects.first()
        self.data = {
            'goalkeeper': game.id,
            '0': 'True',
            '1': 'False',
            '2': 'True',
            'action': 'save'
        }
        self.client.post(reverse("context", args=(game.id,)), self.data)
        context_list, context_not_analyzed = available_context(game.id)
        self.assertListEqual(context_list, ['01', '11', '21'])
        self.assertTrue(context_not_analyzed.exists())
        self.data2 = {
            'goalkeeper': game.id,
            '01': 'True',
            '11': 'True',
            '21': 'True',
            'action': 'save'
        }
        self.client.post(reverse("context", args=(game.id,)), self.data2)
        self.assertEqual(Context.objects.count(), 6)

    ############################
    # Function available context
    ############################
    def test_available_context(self):
        game = GoalkeeperGame.objects.first()
        available_contexts, context_not_analyzed = available_context(game.id)
        self.assertListEqual(available_contexts, ['0', '1', '2'])
        self.assertListEqual(context_not_analyzed, [])

    def test_available_context_with_context_registered(self):
        game = GoalkeeperGame.objects.first()
        Context.objects.create(goalkeeper=game, path='0', is_context='True', analyzed=False)
        Context.objects.create(goalkeeper=game, path='1', is_context='False', analyzed=False)
        Context.objects.create(goalkeeper=game, path='2', is_context='True', analyzed=False)
        available_contexts, context_not_analyzed = available_context(game.id)
        self.assertListEqual(available_contexts, ['01', '11', '21'])
        self.assertEqual(context_not_analyzed.count(), 1)

    ############################################
    # Function check context without probability
    ############################################
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

    ############################
    # Probability
    ############################
    def test_probability_status_code(self):
        game = GoalkeeperGame.objects.first()
        response = self.client.get(reverse("probability", args=(game.id,)))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/probability.html')

    def test_probability_url_resolves_probability_view(self):
        view = resolve('/game/goalkeeper/context/1/probability/')
        self.assertEquals(view.func, probability)

    def test_probability(self):
        game = GoalkeeperGame.objects.first()
        context = Context.objects.create(goalkeeper=game, path='0', is_context='True', analyzed=False)
        self.data = {
            'context': context.path,
            'context-0-0': '',
            'context-0-1': 1,
            'context-0-2': '',
            'action': 'save'
        }
        self.client.post(reverse("probability", args=(game.id,)), self.data)
        self.assertEqual(Probability.objects.count(), 3)

    def test_probability_wrong_values(self):
        game = GoalkeeperGame.objects.first()
        context = Context.objects.create(goalkeeper=game, path='0', is_context='True', analyzed=False)
        self.data = {
            'context': context.path,
            'context-0-0': .5,
            'context-0-1': .4,
            'context-0-2': .3,
            'action': 'save'
        }
        response = self.client.post(reverse("probability", args=(game.id,)), self.data)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(len(message), 1)
        self.assertEqual(str(message[0]), "The sum of the probabilities must be equal to 1.")

    ############################
    # Update probability
    ############################
    def test_probability_update_status_code(self):
        game = GoalkeeperGame.objects.first()
        context = Context.objects.create(goalkeeper=game, path='0', is_context='True', analyzed=False)
        response = self.client.get(reverse("probability_update", args=(context.id,)))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/probability.html')

    def test_probability_update_url_resolves_probability_updatey_view(self):
        view = resolve('/game/goalkeeper/context/1/probability/update/')
        self.assertEquals(view.func, probability_update)

    def test_probability_update(self):
        game = GoalkeeperGame.objects.first()
        context = Context.objects.create(goalkeeper=game, path='0', is_context='True', analyzed=False)
        self.data = {
            'context': context.path,
            'context-0-0': .5,
            'context-0-1': 0,
            'context-0-2': .5,
            'action': 'save'
        }
        self.client.post(reverse("probability", args=(game.id,)), self.data)
        self.data_update = {
            'context': context.path,
            'context-0-0': 0,
            'context-0-1': 1,
            'context-0-2': 0,
            'action': 'save'
        }
        self.client.post(reverse("probability_update", args=(context.id,)), self.data_update)
        self.assertEqual(Probability.objects.filter(context=context, direction=1, value=1.0).count(), 1)

    def test_probability_update_wrong_values(self):
        game = GoalkeeperGame.objects.first()
        context = Context.objects.create(goalkeeper=game, path='0', is_context='True', analyzed=False)
        self.data = {
            'context': context.path,
            'context-0-0': .5,
            'context-0-1': 0,
            'context-0-2': .5,
            'action': 'save'
        }
        self.client.post(reverse("probability", args=(game.id,)), self.data)
        self.data_update = {
            'context': context.path,
            'context-0-0': 1,
            'context-0-1': 1,
            'context-0-2': 0,
            'action': 'save'
        }
        response = self.client.post(reverse("probability_update", args=(context.id,)), self.data_update)
        message = list(get_messages(response.wsgi_request))
        self.assertEqual(str(message[1]), "The sum of the probabilities must be equal to 1.")


class WarmUPTest(TestCase, CommonFunctionsToGameTests):
    def setUp(self):
        faker = Factory.create()
        self.owner = User.objects.create_user(username=faker.text(max_nb_chars=15), password=USER_PWD)
        self.token = Token.objects.create(key=faker.text(max_nb_chars=40), user=self.owner)

    def test__str__of_warm_up(self):
        game_config = self.create_game_configs(self.owner)

        warmup = self.create_game_object(game_config)

        self.assertEqual(str(warmup), game_config.name + " - " + warmup.sequence)

    def test_saving_warm_up(self):
        game_config = self.create_game_configs(self.owner)
        warmup = self.create_game_object(game_config, create=False)

        game_type_before = warmup.game_type
        warmup.save()
        game_type_after = warmup.game_type

        self.assertNotEqual(game_type_before, game_type_after)
        self.assertEqual(game_type_after, 'AQ')



    @staticmethod
    def create_game_object(game_config, phase=0, create=False):
        game = WarmUp(
            config=game_config,
            phase=phase,
            number_of_plays=100,
            min_hits=20,
            min_hits_in_seq=5,
            read_seq=False,
            play_pause=False,
            score_board=False,
            game_type='JG',
            left_key="",
            center_key="",
            right_key="",
            score=10,
        )

        if create:
            game.save()

        return game
