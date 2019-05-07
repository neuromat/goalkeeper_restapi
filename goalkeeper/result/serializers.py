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
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
