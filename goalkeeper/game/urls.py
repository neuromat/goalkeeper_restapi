from django.urls import path
from .views import context_tree, game_config_new, game_config_list, game_config_view, game_config_update,  \
    goalkeeper_game_new, goalkeeper_game_view, goalkeeper_game_update, goalkeeper_game_list, probability, \
    probability_update, select_kicker_to_filter_phase


urlpatterns = [
    # Game config
    path('config/list/', game_config_list, name='game_config_list'),
    path('config/new/', game_config_new, name='game_config_new'),
    path('config/view/<int:config_id>/', game_config_view, name='game_config_view'),
    path('config/update/<int:config_id>/', game_config_update, name='game_config_update'),

    # Goalkeeper game
    path('goalkeeper/new/', goalkeeper_game_new, name='goalkeeper_game_new'),
    path('goalkeeper/view/<int:goalkeeper_game_id>/', goalkeeper_game_view, name='goalkeeper_game_view'),
    path('goalkeeper/update/<int:goalkeeper_game_id>/', goalkeeper_game_update, name='goalkeeper_game_update'),
    path('goalkeeper/list/', goalkeeper_game_list, name='goalkeeper_game_list'),
    path('goalkeeper/context/<int:goalkeeper_game_id>/', context_tree, name='context'),
    path('goalkeeper/context/<int:goalkeeper_game_id>/probability/', probability, name='probability'),
    path('goalkeeper/context/<int:context_id>/probability/update/', probability_update, name='probability_update'),

    # Filters
    path('select_kicker_to_filter_phase', select_kicker_to_filter_phase, name='select_kicker_to_filter_phase'),
]
