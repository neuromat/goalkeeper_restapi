from django.urls import path
from .views import goalkeeper_game_new, goalkeeper_game_view, goalkeeper_game_update, goalkeeper_game_list, context


urlpatterns = [
    path('goalkeeper/new/', goalkeeper_game_new, name='goalkeeper_game_new'),
    path('goalkeeper/view/<int:goalkeeper_game_id>/', goalkeeper_game_view, name='goalkeeper_game_view'),
    path('goalkeeper/update/<int:goalkeeper_game_id>/', goalkeeper_game_update, name='goalkeeper_game_update'),
    path('goalkeeper/list/', goalkeeper_game_list, name='goalkeeper_game_list'),
    path('goalkeeper/context/<int:goalkeeper_game_id>/', context, name='context'),
]
