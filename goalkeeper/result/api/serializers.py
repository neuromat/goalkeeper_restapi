from rest_framework import serializers

from result.models import GameCompleted, GameResult


class GameResultSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = GameResult
        fields = ('id', 'game_phase', 'move', 'waited_result', 'is_random', 'option_chosen', 'correct', 'movement_time', 
                  'time_running', 'user', 'pause_time', 'score', 'defenses', 'defenses_seq')


class GameCompletedSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = GameCompleted
        fields = ('user', 'game')
