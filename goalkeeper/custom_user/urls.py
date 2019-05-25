from django.urls import path
from .views import user_list, new_user, update_user


urlpatterns = [
    path('search', user_list, name='user_list'),
    path('new', new_user, name='new_user'),
    path('edit/<int:user_id>', update_user, name='update_user'),
]
