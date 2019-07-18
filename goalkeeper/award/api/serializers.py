from rest_framework import serializers

from award.models import AwardUser


class AwardUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = AwardUser
        fields = ('id', 'user', 'award_detail', 'game')
