from rest_framework import generics, permissions
from rest_framework.authtoken.models import Token

from custom_user.models import Level, Profile
from game.api.serializers import GameConfigSerializer, GameSerializer, ContextSerializer, ProbSerializer, \
    LevelSerializer, PlayerLevelSerializer
from game.models import Context, Game, GameConfig, GoalkeeperGame, Probability


class GetPlayerLevel(generics.ListAPIView):
    serializer_class = PlayerLevelSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    http_method_names = ['get', 'head']

    def get_queryset(self):
        queryset = Profile.objects.all()
        token_req = self.request.query_params.get('token', None)
        token = Token.objects.filter(key=token_req).first()

        if token is not None:
            queryset = queryset.filter(user=token.user)

        return queryset


class UpdatePlayerLevel(generics.ListAPIView):
    serializer_class = PlayerLevelSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    http_method_names = ['get', 'head']

    def get_queryset(self):
        queryset = Profile.objects.all()
        token_req = self.request.query_params.get('token', None)
        token = Token.objects.filter(key=token_req).first()

        level_req = self.request.query_params.get('nivel', None)
        level = Level.objects.filter(id=level_req).first()

        if token is not None:
            profile = Profile.objects.get(user=token.user)

            if level is not None:
                new_level = level
            else:
                new_level = Level.objects.filter(name=profile.level.name + 1).first()

            if new_level is not None:
                profile.level = new_level
                profile.save()
                queryset = queryset.filter(id=profile.id)
        return queryset


class GetLevel(generics.ListCreateAPIView):
    serializer_class = LevelSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    http_method_names = ['get', 'head']

    def get_queryset(self):
        queryset = Level.objects.all()
        id_req = self.request.query_params.get('id', None)
        name_req = self.request.query_params.get('name', None)

        if id_req is not None:
            queryset = queryset.filter(id=id_req)

        if name_req is not None:
            queryset = queryset.filter(name=name_req)

        return queryset.order_by('id')


# With ?level=<int:level X> at the URL we can filter only games of level X
class GetGameConfigs(generics.ListCreateAPIView):
    serializer_class = GameConfigSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    http_method_names = ['get', 'head']

    def get_queryset(self):
        queryset = GameConfig.objects.all()
        level_id_req = self.request.query_params.get('level', None)
        level_name = Level.objects.get(id=level_id_req).name if level_id_req else None
        # Get all the levels below the requested
        if level_name is not None:
            levels = Level.objects.filter(name__lte=level_name)
            queryset = queryset.filter(level__in=levels)

        config_name_req = self.request.query_params.get('name', None)
        if config_name_req is not None:
            queryset = queryset.filter(name=config_name_req)

        # Filter out those that have at least one phase created
        games_ids = Game.objects.values_list("config_id", flat=True)
        queryset = queryset.filter(pk__in=games_ids)

        # Filter out those that are not public
        queryset = queryset.filter(is_public='yes')

        return queryset.order_by('id')


class GetGames(generics.ListCreateAPIView):
    serializer_class = GameSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    http_method_names = ['get', 'head']

    def get_queryset(self):
        queryset = GoalkeeperGame.objects.all()

        config_id = self.request.query_params.get('config_id', None)
        if config_id is not None:
            queryset = queryset.filter(game_type="JG", config=config_id)

        phase = self.request.query_params.get('phase', None)
        if phase is not None:
            queryset = queryset.filter(phase=phase)

        id = self.request.query_params.get('id', None)
        if id is not None:
            queryset = queryset.filter(id=id)

        return queryset.order_by("phase")


class GetContexts(generics.ListCreateAPIView):
    serializer_class = ContextSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    http_method_names = ['get', 'head']

    def get_queryset(self):
        game_id_req = self.request.query_params.get('game', None)
        queryset = Context.objects.filter(goalkeeper=game_id_req, is_context=True) if game_id_req else None

        return queryset.order_by('id')


class GetProbs(generics.ListCreateAPIView):
    serializer_class = ProbSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    http_method_names = ['get', 'head']

    def get_queryset(self):
        context_id_req = self.request.query_params.get('context', None)
        queryset = Probability.objects.filter(context=context_id_req) if context_id_req else None

        direction = self.request.query_params.get('direction', None)

        if direction is not None:
            queryset = queryset.filter(direction=direction)

        return queryset.order_by('direction')
