from django.urls import path
from .views import context_tree, game_config_new, game_config_list, game_config_view,  goalkeeper_game_new, goalkeeper_game_view, \
    goalkeeper_game_update, goalkeeper_game_list


urlpatterns = [
    # Game config
    path('config/list/', game_config_list, name='game_config_list'),
    path('config/new/', game_config_new, name='game_config_new'),
    path('config/view/<int:config_id>/', game_config_view, name='game_config_view'),

    # Goalkeeper game
    path('goalkeeper/new/', goalkeeper_game_new, name='goalkeeper_game_new'),
    path('goalkeeper/view/<int:goalkeeper_game_id>/', goalkeeper_game_view, name='goalkeeper_game_view'),
    path('goalkeeper/update/<int:goalkeeper_game_id>/', goalkeeper_game_update, name='goalkeeper_game_update'),
    path('goalkeeper/list/', goalkeeper_game_list, name='goalkeeper_game_list'),
    path('goalkeeper/context/<int:goalkeeper_game_id>/', context_tree, name='context'),
]
