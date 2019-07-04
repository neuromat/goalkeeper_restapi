from rest_framework import generics, permissions

from result.models import GameResult
from .serializers import GameResultSerializer


class GameResultList(generics.ListCreateAPIView):
    serializer_class = GameResultSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = GameResult.objects.all()
        game_req = self.request.query_params.get('game', None)

        if game_req is not None:
            queryset = queryset.filter(game_phase=game_req)

        return queryset

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class GameResultDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = GameResult.objects.all()
    serializer_class = GameResultSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
