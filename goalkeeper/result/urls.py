from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import GameResultList, GameResultDetail, UserDetail, UserList


urlpatterns = [
    path('results/', GameResultList.as_view()),
    path('result/<int:pk>/', GameResultDetail.as_view()),
    path('users/', UserList.as_view()),
    path('users/<int:pk>/', UserDetail.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
