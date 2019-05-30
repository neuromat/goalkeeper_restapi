from django.db import models
from django.utils.translation import ugettext_lazy as _

FINAL_SCORE = (
    ('long', _('Long')),
    ('short', _('Short')),
    ('none', _('None')),
)


class Institution(models.Model):
    """ An instance of this class is an institution that uses the game to collect data for research. """
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('Institution')
        verbose_name_plural = _('Institutions')
        ordering = ('name',)


class Level(models.Model):
    """ An instance of this class is used to identify the level of a participant and also the level of the opponent. """
    name = models.IntegerField(unique=True)

    def __str__(self):
        return str(self.name)


class GameConfig(models.Model):
    """ An instance of this class is an opponent. """
    institution = models.ForeignKey(Institution, on_delete=models.PROTECT)
    level = models.ForeignKey(Level, on_delete=models.PROTECT)
    code = models.CharField(max_length=50)
    is_public = models.BooleanField()
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ['institution', 'code']
        verbose_name = _('Game configuration')
        verbose_name_plural = _('Game configurations')
        ordering = ('name',)


class Game(models.Model):
    config = models.ForeignKey(GameConfig, on_delete=models.PROTECT)
    number_of_directions = models.IntegerField(default=3)
    number_of_plays = models.IntegerField(blank=True, null=True)
    min_plays = models.IntegerField(blank=True, null=True)
    min_hits_in_seq = models.IntegerField(blank=True, null=True)
    sequence = models.CharField(max_length=255, blank=True)
    read_seq = models.BooleanField()
    plays_to_relax = models.IntegerField(default=0)
    play_pause = models.BooleanField()
    play_pause_key = models.CharField(max_length=10, blank=True)
    player_time = models.FloatField(default=1.0)
    celebration_time = models.FloatField(default=1.0)
    score_board = models.BooleanField()
    final_score_board = models.CharField(max_length=5, choices=FINAL_SCORE, default='short')
    game_type = models.CharField(max_length=2)
    left_key = models.CharField(max_length=20, blank=True)
    center_key = models.CharField(max_length=20, blank=True)
    right_key = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.config.name + ' - ' + self.game_type


class WarmUp(Game):
    """ An instance of this class is a Warm Up game. """

    def __str__(self):
        return self.config.name + ' - ' + str(self.sequence)

    # Sets the type of the game.
    def save(self, *args, **kwargs):
        if self.pk is None:
            self.game_type = 'AQ'
        super(WarmUp, self).save(*args, **kwargs)


class MemoryGame(Game):
    """ An instance of this class is a Memory game. """
    phase = models.IntegerField()

    def __str__(self):
        return self.config.name + ' - ' + str(self.phase)

    # Sets the type of the game.
    def save(self, *args, **kwargs):
        if self.pk is None:
            self.game_type = 'JM'
        super(MemoryGame, self).save(*args, **kwargs)


class GoalkeeperGame(Game):
    """ An instance of this class is a Goalkeeper game. """
    phase = models.IntegerField()
    depth = models.IntegerField()
    seq_step_det_or_prob = models.CharField(max_length=255, blank=True)
    show_history = models.BooleanField()
    send_markers_eeg = models.CharField(max_length=30, blank=True)
    port_eeg_serial = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.config.name + ' - ' + str(self.phase)

    # Sets the type of the game.
    def save(self, *args, **kwargs):
        if self.pk is None:
            self.game_type = 'JG'
        super(GoalkeeperGame, self).save(*args, **kwargs)


class Context(models.Model):
    """ An instance of this class is a context tree. """
    goalkeeper = models.ForeignKey(GoalkeeperGame, on_delete=models.PROTECT)
    path = models.CharField(max_length=5)


class Probability(models.Model):
    """ An instance of this class is the probability of a given direction in a given context.  """
    context = models.ForeignKey(Context, on_delete=models.PROTECT)
    direction = models.IntegerField()
    value = models.FloatField()
