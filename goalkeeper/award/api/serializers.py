from rest_framework import serializers

from award.models import AwardDetail, AwardUser


class AwardUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = AwardUser
        fields = '__all__'


class AwardDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = AwardDetail
        fields = '__all__'
