from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions
from rest_framework.viewsets import ModelViewSet

from award.models import AwardUser
from .serializers import AwardUserSerializer


class AwardUserList(ModelViewSet):
    queryset = AwardUser.objects.all()
    serializer_class = AwardUserSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('user', 'award_detail', 'game')
