from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, permissions

from result.models import GameCompleted, GameResult
from .serializers import GameCompletedSerializer, GameResultSerializer
from rest_framework.authtoken.models import Token


class GameResultList(generics.ListCreateAPIView):
    serializer_class = GameResultSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = GameResult.objects.all()
        kicker = self.request.query_params.get('kicker', None)
        phase = self.request.query_params.get('phase', None)
        user_token = self.request.query_params.get('token', None)

        if kicker is not None:
            queryset = queryset.filter(game_phase__config__name=kicker)

        if phase is not None:
            queryset = queryset.filter(game_phase__phase=phase)

        if user_token is not None:
            token = Token.objects.filter(key=user_token).first()
            queryset = queryset.filter(user=token.user)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class GameResultDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = GameResult.objects.all()
    serializer_class = GameResultSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class GameCompletedList(generics.ListCreateAPIView):
    serializer_class = GameCompletedSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = GameCompleted.objects.all()

        user_token = self.request.query_params.get('token', None)
        if user_token is not None:
            token = Token.objects.filter(key=user_token).first()
            queryset = queryset.filter(user=token.user)

        return queryset.order_by("game")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
