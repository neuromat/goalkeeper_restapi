from django.contrib.auth.models import User
from rest_framework import serializers
from .models import GameResult


class GameResultSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = GameResult
        fields = ('id', 'game_phase', 'move', 'waited_result', 'is_random', 'option_chosen', 'correct', 'movement_time', 
                  'time_running', 'owner')


class UserSerializer(serializers.ModelSerializer):
    results = serializers.PrimaryKeyRelatedField(many=True, queryset=GameResult.objects.all())

    class Meta:
        model = User
        fields = ('id', 'username', 'game_results')
