from django.contrib.auth.models import User
from rest_framework import generics, permissions, status
from rest_framework.generics import CreateAPIView, DestroyAPIView
from rest_framework.response import Response
from .models import GameResult
from .serializers import GameResultSerializer, UserSerializer


class GameResultList(generics.ListCreateAPIView):
    queryset = GameResult.objects.all()
    serializer_class = GameResultSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class GameResultDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = GameResult.objects.all()
    serializer_class = GameResultSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class UserAPI(DestroyAPIView, CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def perform_destroy(self, instance):
        user = User.objects.get(username=self.request.data['username'], email=self.request.data['email'])
        if user.check_password(self.request.data['password']) is False:
            return Response('You are not authorized to do that.', status=status.HTTP_401_UNAUTHORIZED)
        instance.delete()
