from django.contrib.auth.models import User
from django.db import models

from game.models import Game


class AwardType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class AwardDetail(models.Model):
    award_type = models.ForeignKey(AwardType, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    score = models.PositiveIntegerField()

    def __str__(self):
        return str(self.number) + ' ' + self.award_type.name

    class Meta:
        unique_together = ['award_type', 'number']


class AwardUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    award_detail = models.ForeignKey(AwardDetail, on_delete=models.CASCADE, blank=True, null=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, blank=True, null=True)
