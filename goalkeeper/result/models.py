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
    score = models.IntegerField(default=0)
    defenses = models.IntegerField(default=0)
    defensesseq = models.IntegerField(default=0)
    owner = models.ForeignKey('auth.User', related_name='game_results', on_delete=models.CASCADE)

    def __str__(self):
        return self.game_phase.config.name + ' - ' + self.game_phase.game_type
