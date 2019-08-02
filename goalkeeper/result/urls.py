from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from result.api.viewsets import GameCompletedList, GameResultList, GameResultDetail
from custom_user.api.viewsets import UserAPI, GetAuthToken
from game.api.viewsets import GetGameConfigs, GetGames, GetContexts, GetProbs, GetLevel, GetPlayerLevel, \
    UpdatePlayerLevel


urlpatterns = [
    path('results/', GameResultList.as_view(), name='results'),
    path('result/<int:pk>/', GameResultDetail.as_view(), name='results_detail'),
    path('gamescompleted/', GameCompletedList.as_view(), name='games_completed'),
    path('user', UserAPI.as_view()),
    path('user/<int:pk>/', UserAPI.as_view()),
    path('getauthtoken', GetAuthToken.as_view()),
    path('getgamesconfig/', GetGameConfigs.as_view()),
    path('getgames/', GetGames.as_view()),
    path('getcontexts/', GetContexts.as_view()),
    path('getprobs/', GetProbs.as_view()),
    path('getlevel/', GetLevel.as_view()),
    path('getplayerlevel/', GetPlayerLevel.as_view()),
    path('setplayerlevel/', UpdatePlayerLevel.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
