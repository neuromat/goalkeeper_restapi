from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import GameResultList, GameResultDetail, UserAPI, GetAuthToken
from game.views import GetGameConfigs


urlpatterns = [
    path('results/', GameResultList.as_view()),
    path('result/<int:pk>/', GameResultDetail.as_view()),
    path('user', UserAPI.as_view()),
    path('user/<int:pk>/', UserAPI.as_view()),
    path('getauthtoken', GetAuthToken.as_view()),
    path('getgames/', GetGameConfigs.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)