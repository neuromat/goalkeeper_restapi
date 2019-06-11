from rest_framework import serializers
from .models import GameConfig, GoalkeeperGame, Context, Probability


class GameConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameConfig

        fields = ('id', 'institution', 'level', 'code', 'is_public', 'name')


class GameSerializer(serializers.ModelSerializer):
    class Meta:
        model = GoalkeeperGame

        fields = ('id', 'config', 'number_of_directions', 'number_of_plays', 'min_plays', 'min_hits_in_seq', 'sequence',
                  'read_seq', 'plays_to_relax', 'play_pause', 'play_pause_key', 'player_time', 'celebration_time',
                  'score_board', 'final_score_board', 'game_type', 'left_key', 'center_key', 'right_key', 'phase',
                  'depth', 'seq_step_det_or_prob', 'show_history', 'send_markers_eeg', 'port_eeg_serial')


class ContextSerializer(serializers.ModelSerializer):
    class Meta:
        model = Context

        fields = ('id', 'path', 'goalkeeper')


class ProbSerializer(serializers.ModelSerializer):
    class Meta:
        model = Probability

        fields = ('id', 'context', 'direction', 'value')
