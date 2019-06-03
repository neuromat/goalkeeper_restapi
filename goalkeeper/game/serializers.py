from rest_framework import serializers
from .models import GameConfig


class GameConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameConfig

        fields = ('id', 'institution', 'level', 'code', 'is_public', 'name')
