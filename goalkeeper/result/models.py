from django.contrib.auth.models import User
from django.db import models

from game.models import Game


class GameResult(models.Model):
    """ An instance of this class is the result of a game movement. """
    game_phase = models.ForeignKey(Game, on_delete=models.PROTECT)
    move = models.IntegerField()
    waited_result = models.IntegerField()
    is_random = models.BooleanField()
    option_chosen = models.IntegerField()
    correct = models.BooleanField()
    movement_time = models.FloatField()
    pause_time = models.FloatField()
    time_running = models.FloatField()
    score = models.IntegerField()
    defenses = models.IntegerField()
    defenses_seq = models.IntegerField()
    user = models.ForeignKey(User, related_name='game_results', on_delete=models.CASCADE)

    def __str__(self):
        return self.game_phase.config.name + ' - ' + self.game_phase.game_type


class GameCompleted(models.Model):
    """ An instance of this class is a game completed by a user. """
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

    class Meta:
        unique_together = ['user', 'game']
