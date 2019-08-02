from rest_framework.test import APITestCase
from django.urls import reverse, resolve

from .api.viewsets import GameResultList, GameResultDetail, GameCompletedList
from .api.serializers import GameResultSerializer
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from .models import GameResult
from game.models import Game, GameConfig, Level, GoalkeeperGame

from faker import Factory

PASSWORD = 'psswrd'


class ResultsUrlsTestCase(APITestCase):

    # Todos os endpoints utilizam as views corretas
    def test_resolves_results_list_url(self):
        resolver = self.resolve_by_name('results')

        self.assertEqual(resolver.func.cls, GameResultList)

    def test_resolves_results_detail_url(self):
        resolver = self.resolve_by_name('results_detail', pk=1)

        self.assertEqual(resolver.func.cls, GameResultDetail)

    def test_resolves_games_completed_url(self):
        resolver = self.resolve_by_name('games_completed')

        self.assertEqual(resolver.func.cls, GameCompletedList)

    @staticmethod
    def resolve_by_name(name, **kwargs):
        url = reverse(name, kwargs=kwargs)
        return resolve(url)


class GameResultListTestCase(APITestCase):

    def setUp(self):
        faker = Factory.create()
        self.owner = User.objects.create_user(username=faker.text(max_nb_chars=15), password=PASSWORD)
        self.token = Token.objects.create(key=faker.text(max_nb_chars=40), user=self.owner)

    # Testa se os resultados da base são exatamente os mesmos que os retornados pela API
    def test_all_results(self):
        self.create_results(self.owner, 0, 20, 5)

        results = GameResult.objects.all()
        serializer = GameResultSerializer(results, many=True)

        response = self.client.get(reverse('results'))
        self.assertEqual(response.data, serializer.data)

    # Testa se os resultados de um batedor específico na base são exatamente os mesmos que os retornados pela API
    def test_results_of_specific_kicker(self):
        kicker_name = "test_kicker"
        self.create_results(self.owner, 0, 20, 5)
        self.create_results(self.owner, 0, 20, 5, kicker_name)

        results = GameResult.objects.filter(game_phase__config_id__name=kicker_name)
        serializer = GameResultSerializer(results, many=True)

        response = self.client.get(reverse('results'), {'kicker': kicker_name})
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(len(response.data), 1)

    # Testa se os resultados de uma phase específica na base são exatamente os mesmos que os retornados pela API
    def test_results_of_specific_phase(self):
        phase = 0
        self.create_results(self.owner, phase, 20, 5)
        self.create_results(self.owner, 1, 20, 5)

        results = GameResult.objects.filter(game_phase__phase=phase)
        serializer = GameResultSerializer(results, many=True)

        response = self.client.get(reverse('results'), {'phase': phase})
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(len(response.data), 1)

    # Testa se os resultados de um usuário específico na base são exatamente os mesmos que os retornados pela API
    def test_results_of_specific_user(self):
        test_user = User.objects.create_user(username="test_user", password=PASSWORD)
        Token.objects.create(key="test_user_token", user=test_user)

        self.create_results(test_user, 0, 20, 5)
        self.create_results(self.owner, 0, 20, 5)

        results = GameResult.objects.filter(user_id=self.owner)
        serializer = GameResultSerializer(results, many=True)

        response = self.client.get(reverse('results'), {'token': self.token})
        self.assertEqual(response.data, serializer.data)
        self.assertEqual(len(response.data), 1)

    # Cria os elementos necessários para que uma jogada possa ser registrada na base
    @staticmethod
    def create_results(owner, phase, min_hits, min_hits_in_seq, kicker_name=None):
        faker = Factory.create()

        # GameConfig objects
        level = Level.objects.create(name=faker.random.randint(0, 1000))
        code = faker.text(max_nb_chars=50)
        name = kicker_name or faker.text(max_nb_chars=100)
        created_by = owner
        game_config = GameConfig.objects.create(level=level, code=code, name=name, created_by=created_by)

        # Game object
        game = GoalkeeperGame.objects.create(
            config=game_config,
            phase=phase,
            number_of_plays=100,
            min_hits=min_hits,
            min_hits_in_seq=min_hits_in_seq,
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

        # Game result object
        GameResult.objects.create(
            game_phase=Game.objects.get(id=game.id),
            move=0,
            waited_result=1,
            is_random=True,
            option_chosen=1,
            correct=True,
            movement_time=1.0,
            pause_time=2.0,
            time_running=3.0,
            score=1,
            defenses=1,
            defenses_seq=0,
            user=owner
        )
