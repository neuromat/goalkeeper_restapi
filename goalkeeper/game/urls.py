from django.urls import path
from .views import goalkeeper_game_new, goalkeeper_game_view, goalkeeper_game_update


urlpatterns = [
    path('goalkeeper/new/', goalkeeper_game_new, name='goalkeeper_game_new'),
    path('goalkeeper/view/<int:goalkeeper_game_id>/', goalkeeper_game_view, name='goalkeeper_game_view'),
    path('goalkeeper/update/<int:goalkeeper_game_id>/', goalkeeper_game_update, name='goalkeeper_game_update'),
]
