from rest_framework.test import APITestCase, APIClient, force_authenticate
from django.urls import reverse, resolve
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from game.api.viewsets import GetGameConfigs, GetGames, GetContexts, GetProbs, GetLevel, GetPlayerProfile,\
    UpdatePlayerLevel
from game.api.serializers import PlayerLevelSerializer, LevelSerializer, GameConfigSerializer, GameSerializer, \
    ContextSerializer, ProbSerializer
from game.models import Level, GameConfig, Game, WarmUp, GoalkeeperGame, Context, Probability
from custom_user.models import Profile


from faker import Factory

PASSWORD = 'psswrd'

# path('getgamesconfig/', GetGameConfigs.as_view(), name='get_games_configs'),
# path('getgames/', GetGames.as_view(), name='get_games'),
# path('getcontexts/', GetContexts.as_view(), name='get_contexts'),
# path('getprobs/', GetProbs.as_view(), name='get_probs'),
# path('getlevel/', GetLevel.as_view(), name='get_level'),
# path('getplayerprofile/', GetPlayerProfile.as_view(), name='get_player_profile'),
# path('setplayerlevel/', UpdatePlayerLevel.as_view(), name='set_player_level'),


class CommonFunctionsToGameTests(object):
    @staticmethod
    def create_game_configs(user, level_name=0, is_public='yes', name=None, create=True):
        faker = Factory.create()

        level, created = Level.objects.get_or_create(name=level_name)

        gameconfig = GameConfig(
            level=level,
            code=faker.text(max_nb_chars=50),
            name=name or faker.text(max_nb_chars=100),
            is_public=is_public,
            created_by=user)

        if create:
            gameconfig.save()

        return gameconfig

    @staticmethod
    def create_game_object(game_config, phase=0):
        game = GoalkeeperGame.objects.create(
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
            seq_step_det_or_prob="",
            show_history=False,
            send_markers_eeg="",
            port_eeg_serial=""
        )

        return game

    @staticmethod
    def create_profile(user, level_name=0):
        level, created = Level.objects.get_or_create(name=level_name)

        profile = Profile.objects.create(user=user, level=level)
        return profile

    @staticmethod
    def create_context(game):
        faker = Factory.create()

        context = Context.objects.create(goalkeeper=game,
                                         path=faker.text(max_nb_chars=5),
                                         is_context=True)
        return context

    @staticmethod
    def create_probability_of_a_context(context, direction):
        probability = Probability.objects.create(context=context, direction=direction, value=0.2)

        return probability


class GameUrlsTestCase(APITestCase):

    # Todos os endpoints utilizam as views corretas
    def test_resolves_games_configs_url(self):
        resolver = self.resolve_by_name('get_games_configs')

        self.assertEqual(resolver.func.cls, GetGameConfigs)

    def test_resolves_get_games_url(self):
        resolver = self.resolve_by_name('get_games')

        self.assertEqual(resolver.func.cls, GetGames)

    def test_resolves_get_contexts_url(self):
        resolver = self.resolve_by_name('get_contexts')

        self.assertEqual(resolver.func.cls, GetContexts)

    def test_resolves_get_probs_url(self):
        resolver = self.resolve_by_name('get_probs')

        self.assertEqual(resolver.func.cls, GetProbs)

    def test_resolves_get_levels_url(self):
        resolver = self.resolve_by_name('get_level')

        self.assertEqual(resolver.func.cls, GetLevel)

    def test_resolves_get_player_profile_url(self):
        resolver = self.resolve_by_name('get_player_profile')

        self.assertEqual(resolver.func.cls, GetPlayerProfile)

    def test_resolves_set_player_level_url(self):
        resolver = self.resolve_by_name('set_player_level')

        self.assertEqual(resolver.func.cls, UpdatePlayerLevel)

    @staticmethod
    def resolve_by_name(name, **kwargs):
        url = reverse(name, kwargs=kwargs)
        return resolve(url)


# Games Configs are only shown if they have Games set and are public
class GameConfigsTestCase(APITestCase, CommonFunctionsToGameTests):
    def setUp(self):
        faker = Factory.create()
        self.owner = User.objects.create_user(username=faker.text(max_nb_chars=15), password=PASSWORD)
        self.token = Token.objects.create(key=faker.text(max_nb_chars=40), user=self.owner)

    def test_fail_to_get_all_games_configs_when_none_of_them_have_games_set(self):
        self.create_game_configs(self.owner)

        response = self.client.get(reverse('get_games_configs'))
        self.assertEqual(len(response.data), 0)
        self.assertEqual(GameConfig.objects.count(), 1)

    def test_fail_to_get_all_games_configs_when_none_of_them_are_public(self):
        game_config = self.create_game_configs(self.owner, is_public='no')
        self.create_game_object(game_config)

        response = self.client.get(reverse('get_games_configs'))
        self.assertEqual(len(response.data), 0)
        self.assertEqual(GameConfig.objects.count(), 1)

    def test_fail_to_get_all_games_configs_when_they_have_games_set_but_are_not_public(self):
        game_config = self.create_game_configs(self.owner, is_public='no')
        self.create_game_object(game_config)

        response = self.client.get(reverse('get_games_configs'))
        self.assertEqual(len(response.data), 0)
        self.assertEqual(GameConfig.objects.count(), 1)

    def test_get_all_games_configs_when_they_have_games_set_and_are_public(self):
        game_config = self.create_game_configs(self.owner)
        self.create_game_object(game_config)

        response = self.client.get(reverse('get_games_configs'))
        self.assertEqual(len(response.data), 1)
        self.assertEqual(GameConfig.objects.count(), 1)

    def test_get_games_configs_with_levels_less_or_equal_a_specific_level(self):
        level_test = 1
        game_config_1 = self.create_game_configs(self.owner)
        self.create_game_object(game_config_1)

        game_config_2 = self.create_game_configs(self.owner, level_name=level_test)
        self.create_game_object(game_config_2)

        results = GameConfig.objects.filter(level__name__lte=level_test).order_by('id')
        serializer = GameConfigSerializer(results, many=True)

        level_test_id = Level.objects.get(name=level_test).id

        response = self.client.get(reverse('get_games_configs'), {'level': level_test_id})
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(len(response.data), 2)

    def test_get_games_configs_with_specific_name(self):
        name_test = "kicker_test"
        game_config_1 = self.create_game_configs(self.owner, name=name_test)
        self.create_game_object(game_config_1)

        game_config_2 = self.create_game_configs(self.owner)
        self.create_game_object(game_config_2)

        results = GameConfig.objects.filter(name=name_test)
        serializer = GameConfigSerializer(results, many=True)

        response = self.client.get(reverse('get_games_configs'), {'name': name_test})
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(len(response.data), 1)

    def test__str__of_game_config(self):
        game_config = self.create_game_configs(self.owner, create=False)

        self.assertEqual(str(game_config), game_config.name)


class GamesTestCase(APITestCase, CommonFunctionsToGameTests):
    def setUp(self):
        faker = Factory.create()
        self.owner = User.objects.create_user(username=faker.text(max_nb_chars=15), password=PASSWORD)
        self.token = Token.objects.create(key=faker.text(max_nb_chars=40), user=self.owner)

    def test_get_all_games(self):
        game_config = self.create_game_configs(self.owner)
        self.create_game_object(game_config)

        response = self.client.get(reverse('get_games'))
        self.assertEqual(len(response.data), 1)
        self.assertEqual(Game.objects.count(), 1)

    def test_get_all_games_of_a_specific_opponent(self):
        game_config1 = self.create_game_configs(self.owner)
        self.create_game_object(game_config1)

        game_config2 = self.create_game_configs(self.owner)
        self.create_game_object(game_config2)

        response = self.client.get(reverse('get_games'), {'config_id': game_config1.id})
        self.assertEqual(len(response.data), 1)
        self.assertEqual(Game.objects.count(), 2)

    def test_get_all_games_of_a_specific_phase(self):
        phase_test = 1
        game_config1 = self.create_game_configs(self.owner)
        self.create_game_object(game_config1, phase_test)

        game_config2 = self.create_game_configs(self.owner)
        self.create_game_object(game_config2, 0)

        response = self.client.get(reverse('get_games'), {'phase': phase_test})
        self.assertEqual(len(response.data), 1)
        self.assertEqual(Game.objects.count(), 2)

    def test_get_a_specific_game_by_id(self):
        game_config1 = self.create_game_configs(self.owner)
        self.create_game_object(game_config1)

        id_test = Game.objects.last().id

        game_config2 = self.create_game_configs(self.owner)
        self.create_game_object(game_config2)

        response = self.client.get(reverse('get_games'), {'id': id_test})
        self.assertEqual(len(response.data), 1)
        self.assertEqual(Game.objects.count(), 2)

    def test__str__of_game(self):
        game_config = self.create_game_configs(self.owner)
        self.create_game_object(game_config)

        game_test = Game.objects.last()

        self.assertEqual(str(game_test), game_config.name + ' - ' + game_test.game_type)


class LevelTestCase(APITestCase):
    def setUp(self):
        self.level, created = Level.objects.get_or_create(name=0)

    def test_get_specific_level_by_id(self):
        Level.objects.get_or_create(name=1)

        response = self.client.get(reverse('get_level'), {'id': self.level.id})
        self.assertEqual(len(response.data), 1)
        self.assertEqual(Level.objects.count(), 2)

    def test_get_specific_level_by_name(self):
        Level.objects.get_or_create(name=1)

        response = self.client.get(reverse('get_level'), {'name': self.level.name})
        self.assertEqual(len(response.data), 1)
        self.assertEqual(Level.objects.count(), 2)

    def test__str__of_game(self):
        self.assertEqual(str(self.level), str(self.level.name))


class PlayerProfileTestCase(APITestCase, CommonFunctionsToGameTests):
    def setUp(self):
        faker = Factory.create()
        self.owner = User.objects.create_user(username=faker.text(max_nb_chars=15), password=PASSWORD)
        self.token = Token.objects.create(key=faker.text(max_nb_chars=40), user=self.owner)
        self.profile = self.create_profile(self.owner)

    def test_get_all_profiles(self):
        faker = Factory.create()
        user2 = User.objects.create_user(username=faker.text(max_nb_chars=15), password=PASSWORD)

        self.create_profile(user2)

        response = self.client.get(reverse('get_player_profile'))
        self.assertEqual(len(response.data), 2)
        self.assertEqual(Profile.objects.count(), 2)

    def test_get_specific_profile_by_token(self):
        faker = Factory.create()
        user2 = User.objects.create_user(username=faker.text(max_nb_chars=15), password=PASSWORD)
        Token.objects.create(key=faker.text(max_nb_chars=40), user=user2)

        self.create_profile(user2)

        response = self.client.get(reverse('get_player_profile'), {'token': self.token})
        self.assertEqual(len(response.data), 1)
        self.assertEqual(Profile.objects.count(), 2)

    def test__str__of_profile(self):
        self.assertEqual(str(self.profile), str(self.owner.username))

    def test_return_profiles_instead_of_update_level_if_the_required_params_are_not_passed(self):
        level_before = self.profile.level.name

        response = self.client.get(reverse('set_player_level'))

        level_after = Profile.objects.last().level.name

        self.assertEqual(len(response.data), 1)
        self.assertEqual(Profile.objects.count(), 1)
        self.assertEqual(level_before, level_after)

    def test_update_level_of_player_to_the_next_level(self):
        level_before = self.profile.level.name

        response = self.client.get(reverse('set_player_level'), {'token': self.token})

        level_after = Profile.objects.last().level.name

        self.assertEqual(len(response.data), 1)
        self.assertEqual(level_before + 1, level_after)

    def test_update_level_of_player_to_a_specific_level(self):
        new_level, created = Level.objects.get_or_create(name=2)

        response = self.client.get(reverse('set_player_level'), {'token': self.token, 'nivel': new_level.id})

        level_id_after = Level.objects.get(id=response.data[0]["level"])

        self.assertEqual(len(response.data), 1)
        self.assertEqual(new_level, level_id_after)


class ContextsTestCase(APITestCase, CommonFunctionsToGameTests):
    def setUp(self):
        faker = Factory.create()
        self.owner = User.objects.create_user(username=faker.text(max_nb_chars=15), password=PASSWORD)
        self.game_config = self.create_game_configs(self.owner)
        self.game = self.create_game_object(self.game_config)
        self.create_context(self.game)

    def test_get_all_contexts_of_a_game(self):
        game2 = self.create_game_object(self.game_config, 1)
        self.create_context(game2)

        response = self.client.get(reverse('get_contexts'), {'game': self.game.id})
        self.assertEqual(len(response.data), 1)
        self.assertEqual(Context.objects.count(), 2)

    def test_fail_to_get_contexts_if_game_id_is_not_passed(self):
        game2 = self.create_game_object(self.game_config, 1)
        self.create_context(game2)

        response = self.client.get(reverse('get_contexts'))
        self.assertEqual(len(response.data), 0)
        self.assertEqual(Context.objects.count(), 2)


class ProbabilitiesTestCase(APITestCase, CommonFunctionsToGameTests):
    def setUp(self):
        faker = Factory.create()
        self.owner = User.objects.create_user(username=faker.text(max_nb_chars=15), password=PASSWORD)
        self.game_config = self.create_game_configs(self.owner)
        self.game = self.create_game_object(self.game_config)
        self.context = self.create_context(self.game)
        self.create_probability_of_a_context(self.context, 0)
        self.create_probability_of_a_context(self.context, 1)

    def test_get_all_probabilities_of_a_context(self):
        context2 = self.create_context(self.game)
        self.create_probability_of_a_context(context2, 0)

        response = self.client.get(reverse('get_probs'), {'context': self.context.id})
        self.assertEqual(len(response.data), 2)
        self.assertEqual(Probability.objects.count(), 3)

    def test_fail_to_get_probabilities_when_not_passing_context(self):
        response = self.client.get(reverse('get_probs'))
        self.assertEqual(len(response.data), 0)
        self.assertEqual(Probability.objects.count(), 2)

    def test_get_probability_of_a_context_in_a_specific_direction(self):
        response = self.client.get(reverse('get_probs'), {'context': self.context.id, 'direction': 0})
        self.assertEqual(len(response.data), 1)
        self.assertEqual(Probability.objects.count(), 2)
