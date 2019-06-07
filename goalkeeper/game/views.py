from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models.deletion import ProtectedError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils.translation import activate, LANGUAGE_SESSION_KEY, ugettext as _

from rest_framework import generics, permissions

from .forms import GameConfigForm, GoalkeeperGameForm
from .models import Context, Game, GoalkeeperGame, Probability, GameConfig, Level
from .serializers import GameConfigSerializer


@login_required
def home(request, template_name="game/home.html"):
    return render(request, template_name)


def language_change(request, language_code):
    activate(language_code)
    request.session[LANGUAGE_SESSION_KEY] = language_code
    return HttpResponseRedirect(request.GET['next'])


@login_required
def game_config_list(request, template_name="game/config_list.html"):
    configs = GameConfig.objects.all().order_by('name')

    context = {
        "configs": configs,
    }

    return render(request, template_name, context)


@login_required
def goalkeeper_game_list(request, template_name="game/goalkeeper_game_list.html"):
    games = GoalkeeperGame.objects.all().order_by('config', 'phase')

    context = {
        "games": games,
        "creating": True
    }

    return render(request, template_name, context)


@login_required
def game_config_new(request, template_name="game/config.html"):
    form = GameConfigForm(request.POST or None)

    if request.method == "POST" and request.POST['action'] == "save":
        if form.is_valid():
            config = form.save(commit=False)
            config.created_by = request.user
            config.save()
            messages.success(request, _('New kicker created successfully.'))
            redirect_to = request.POST.get('next')

            if redirect_to and redirect_to.split('/')[-2] == 'new':
                return HttpResponseRedirect(reverse("goalkeeper_game_new"))
            else:
                return HttpResponseRedirect(reverse("game_config_view", args=(config.id,)))

        else:
            messages.warning(request, _('Information not saved.'))

    context = {
        "form": form,
        "creating": True
    }

    return render(request, template_name, context)


@login_required
def game_config_view(request, config_id, template_name="game/config.html"):
    config = get_object_or_404(GameConfig, pk=config_id)
    form = GameConfigForm(request.POST or None, instance=config)

    for field in form.fields:
        form.fields[field].widget.attrs['disabled'] = True

    if request.method == "POST" and request.POST['action'] == "remove":
        if Game.objects.filter(config=config.id):
            messages.error(request, _("This config can't be removed because there are games configured with it."))
            redirect_url = reverse("game_config_view", args=(config_id,))
            return HttpResponseRedirect(redirect_url)
        else:
            try:
                config.delete()
                messages.success(request, _('Kicker removed successfully.'))
                return redirect('game_config_list')
            except ProtectedError:
                messages.error(request, _("Error trying to delete this config."))
                redirect_url = reverse("game_config_view", args=(config_id,))
                return HttpResponseRedirect(redirect_url)

    context = {
        "config": config,
        "form": form,
        "viewing": True
    }

    return render(request, template_name, context)


@login_required
def game_config_update(request, config_id, template_name="game/config.html"):
    config = get_object_or_404(GameConfig, pk=config_id)
    form = GameConfigForm(request.POST or None, instance=config)

    if request.method == "POST" and request.POST['action'] == "save":
        if form.is_valid():
            if form.has_changed():
                form.save()
                messages.success(request, _('Kicker updated successfully.'))
            else:
                messages.warning(request, _('There are no changes to save.'))
        else:
            messages.warning(request, _('Information not saved.'))

        redirect_url = reverse("game_config_view", args=(config.id,))
        return HttpResponseRedirect(redirect_url)

    context = {
        "config": config,
        "form": form,
        "editing": True
    }

    return render(request, template_name, context)


@login_required
def goalkeeper_game_new(request, template_name="game/goalkeeper_game.html"):
    goalkeeper_game_form = GoalkeeperGameForm(request.POST or None)

    if request.method == "POST" and request.POST['action'] == "save":
        if goalkeeper_game_form.is_valid():
            game_selected = GoalkeeperGame.objects.filter(config=request.POST['config']).order_by('phase')

            if game_selected:
                next_phase = game_selected.last().phase + 1
            else:
                next_phase = 0

            game = goalkeeper_game_form.save(commit=False)
            game.phase = next_phase
            game.save()

            messages.success(request, _('Game created successfully.'))
            redirect_url = reverse("goalkeeper_game_view", args=(game.id,))
            return HttpResponseRedirect(redirect_url)

        else:
            messages.warning(request, _('Information not saved.'))

    context = {
        "goalkeeper_game_form": goalkeeper_game_form,
        "creating": True
    }

    return render(request, template_name, context)


@login_required
def goalkeeper_game_view(request, goalkeeper_game_id, template_name="game/goalkeeper_game.html"):
    game = get_object_or_404(GoalkeeperGame, pk=goalkeeper_game_id)
    goalkeeper_game_form = GoalkeeperGameForm(request.POST or None, instance=game)
    probabilities = Probability.objects.filter(context__goalkeeper=game)
    context_used = Context.objects.filter(goalkeeper=game)
    context_list = available_context(goalkeeper_game_id)

    for field in goalkeeper_game_form.fields:
        goalkeeper_game_form.fields[field].widget.attrs['disabled'] = True

    if request.method == "POST":
        if request.POST['action'] == "remove":
            try:
                game.delete()
                messages.success(request, _('Game removed successfully.'))
            except ProtectedError:
                messages.error(request, _("Error trying to delete the game."))

            return HttpResponseRedirect(reverse("goalkeeper_game_list"))

        if request.POST['action'][:12] == "remove_path-":
            get_context = get_object_or_404(Context, pk=request.POST['action'][12:])
            get_context.delete()
            messages.success(request, _('Context removed successfully.'))
            redirect_url = reverse("goalkeeper_game_view", args=(goalkeeper_game_id,))
            return HttpResponseRedirect(redirect_url)

    context = {
        "game": game,
        "goalkeeper_game_form": goalkeeper_game_form,
        "probabilities": probabilities,
        "context_used": context_used,
        "context_list": context_list,
        "viewing": True
    }

    return render(request, template_name, context)


@login_required
def goalkeeper_game_update(request, goalkeeper_game_id, template_name="game/goalkeeper_game.html"):
    game = get_object_or_404(GoalkeeperGame, pk=goalkeeper_game_id)
    goalkeeper_game_form = GoalkeeperGameForm(request.POST or None, instance=game)

    if request.method == "POST" and request.POST['action'] == "save":
        if goalkeeper_game_form.is_valid():
            if goalkeeper_game_form.has_changed():
                goalkeeper_game_form.save()
                messages.success(request, _('Game updated successfully.'))
            else:
                messages.warning(request, _('There are no changes to save.'))
        else:
            messages.warning(request, _('Information not saved.'))

        redirect_url = reverse("goalkeeper_game_view", args=(game.id,))
        return HttpResponseRedirect(redirect_url)

    context = {
        "game": game,
        "goalkeeper_game_form": goalkeeper_game_form,
        "editing": True
    }

    return render(request, template_name, context)


def available_context(goalkeeper_game_id):
    """
    Function to create the list of available context
    :param goalkeeper_game_id: ID of the game for which a context will be created
    :return: list with the available context
    """
    game = get_object_or_404(GoalkeeperGame, pk=goalkeeper_game_id)
    context_registered = Context.objects.filter(goalkeeper=game.pk).order_by('path')
    context_list = []
    context_not_analyzed = []

    if context_registered:
        context_not_analyzed = context_registered.filter(is_context=False, analyzed=False)

        # Concatenation of a node that is not context with each direction.
        if context_not_analyzed:
            for item in context_not_analyzed:
                for direction in range(game.number_of_directions):
                    context_list.append(str(item.path)+str(direction))

    else:
        # Start the list of available context with 0 until the number_of_directions
        for direction in range(game.number_of_directions):
            context_list.append(str(direction))

    return context_list, context_not_analyzed


@login_required
def context_tree(request, goalkeeper_game_id, template_name="game/context.html"):
    """
    An instance of this class is a node that may or may not be a context
    :param request: request method
    :param goalkeeper_game_id: ID of the game for which a context will be created
    :param template_name: template used to create the context
    :return: data available to create the context
    """
    game = get_object_or_404(GoalkeeperGame, pk=goalkeeper_game_id)
    context_list, context_not_analyzed = available_context(goalkeeper_game_id)

    if request.method == "POST" and request.POST['action'] == "save":
        context_to_save = {}
        for num in context_list:
            context_to_save[num] = request.POST.get(num)

        for key, value in context_to_save.items():
            if value == 'True':
                Context.objects.create(goalkeeper=game, path=key, is_context=value, analyzed=True)
            else:
                Context.objects.create(goalkeeper=game, path=key, is_context=value)

        for item in context_not_analyzed:
            item.analyzed = True
            item.save()

        redirect_url = reverse("context", args=(goalkeeper_game_id,))
        return HttpResponseRedirect(redirect_url)

    context = {
        "game": game,
        "context_list": context_list,
    }

    return render(request, template_name, context)


# Django Rest
# With ?level=<int:level X> at the URL we can filter only games of level X
class GetGameConfigs(generics.ListCreateAPIView):
    serializer_class = GameConfigSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    http_method_names = ['get', 'head']

    def get_queryset(self):
        queryset = GameConfig.objects.all()
        level_req = self.request.query_params.get('level', None)
        level = Level.objects.get_or_create(name=level_req)[0].id if level_req else 1

        if level is not None:
            queryset = queryset.filter(level__lte=level)

        return queryset.order_by('id')
