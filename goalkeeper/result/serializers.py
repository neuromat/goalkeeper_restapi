from django.contrib.auth.models import User
from rest_framework import serializers
from .models import GameResult
from game.models import Level
from custom_user.models import Profile


class GameResultSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = GameResult
        fields = ('id', 'game_phase', 'move', 'waited_result', 'is_random', 'option_chosen', 'correct', 'movement_time', 
                  'time_running', 'owner', 'pause_time')


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
        level, created = Level.objects.get_or_create(name=0)
        Profile.objects.create(user=user, level=level)
        return user
