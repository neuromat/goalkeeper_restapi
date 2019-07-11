from rest_framework import generics, permissions

from result.models import GameResult
from .serializers import GameResultSerializer


class GameResultList(generics.ListCreateAPIView):
    serializer_class = GameResultSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = GameResult.objects.all()
        kicker = self.request.query_params.get('kicker', None)
        phase = self.request.query_params.get('phase', None)

        if kicker is not None:
            queryset = queryset.filter(game_phase__config__name=kicker)

        if phase is not None:
            queryset = queryset.filter(game_phase__phase=phase)

        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class GameResultDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = GameResult.objects.all()
    serializer_class = GameResultSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
