from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from result.api.viewsets import GameCompletedList, GameResultList, GameResultDetail
from custom_user.api.viewsets import UserAPI, GetAuthToken
from game.api.viewsets import GetGameConfigs, GetGames, GetContexts, GetProbs, GetLevel, GetPlayerProfile, \
    UpdatePlayerLevel


urlpatterns = [
    path('results/', GameResultList.as_view(), name='results'),
    path('result/<int:pk>/', GameResultDetail.as_view(), name='results_detail'),
    path('gamescompleted/', GameCompletedList.as_view(), name='games_completed'),
    path('user', UserAPI.as_view()),
    path('user/<int:pk>/', UserAPI.as_view()),
    path('getauthtoken', GetAuthToken.as_view()),
    path('getgamesconfig/', GetGameConfigs.as_view(), name='get_games_configs'),
    path('getgames/', GetGames.as_view(), name='get_games'),
    path('getcontexts/', GetContexts.as_view(), name='get_contexts'),
    path('getprobs/', GetProbs.as_view(), name='get_probs'),
    path('getlevel/', GetLevel.as_view(), name='get_level'),
    path('getplayerprofile/', GetPlayerProfile.as_view(), name='get_player_profile'),
    path('setplayerlevel/', UpdatePlayerLevel.as_view(), name='set_player_level'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
