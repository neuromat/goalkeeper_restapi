from django import forms
from django.forms import CheckboxInput, NumberInput, Select, TextInput
from .models import GameConfig, GoalkeeperGame


class GameConfigForm(forms.ModelForm):

    class Meta:
        model = GameConfig
        exclude = ('created_by',)

        widgets = {
            'level': Select(attrs={'class': 'form-control'}),
            'code': TextInput(attrs={'class': 'form-control'}),
            'name': TextInput(attrs={'class': 'form-control'}),
            'is_public': Select(attrs={'class': 'form-control'}),
        }


class GoalkeeperGameForm(forms.ModelForm):

    class Meta:
        model = GoalkeeperGame
        exclude = ('game_type', 'phase', 'read_seq')

        widgets = {
            'config': Select(attrs={'class': 'form-control'}),
            'number_of_directions': Select(attrs={'class': 'form-control'}),
            'number_of_plays': NumberInput(attrs={'class': 'form-control'}),
            'min_hits': NumberInput(attrs={'class': 'form-control'}),
            'min_hits_in_seq': NumberInput(attrs={'class': 'form-control'}),
            'sequence': TextInput(attrs={'class': 'form-control'}),
            'plays_to_relax': NumberInput(attrs={'class': 'form-control'}),
            'play_pause': CheckboxInput(attrs={'class': 'form-control'}),
            'play_pause_key': TextInput(attrs={'class': 'form-control'}),
            'player_time': NumberInput(attrs={'class': 'form-control'}),
            'celebration_time': NumberInput(attrs={'class': 'form-control'}),
            'score_board': CheckboxInput(attrs={'class': 'form-control'}),
            'final_score_board': Select(attrs={'class': 'form-control'}),
            'left_key': TextInput(attrs={'class': 'form-control'}),
            'center_key': TextInput(attrs={'class': 'form-control'}),
            'right_key': TextInput(attrs={'class': 'form-control'}),
            'depth': NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'seq_step_det_or_prob': TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'create_seq_manually': Select(attrs={'class': 'form-control'}),
            'show_history': CheckboxInput(attrs={'class': 'form-control'}),
            'send_markers_eeg': TextInput(attrs={'class': 'form-control'}),
            'port_eeg_serial': TextInput(attrs={'class': 'form-control'}),
        }
