from rest_framework import serializers

from result.models import GameResult


class GameResultSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = GameResult
        fields = ('id', 'game_phase', 'move', 'waited_result', 'is_random', 'option_chosen', 'correct', 'movement_time', 
                  'time_running', 'owner', 'pause_time')
