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
    context_registered = Context.objects.filter(goalkeeper=game)
    context_used = context_registered.filter(is_context=True)
    last_context = len(context_used.last().path) if context_used else None
    context_list = available_context(goalkeeper_game_id)
    context_without_probability = check_contexts_without_probability(goalkeeper_game_id)

    for field in goalkeeper_game_form.fields:
        goalkeeper_game_form.fields[field].widget.attrs['disabled'] = True

    if request.method == "POST":
        # Remove a Goalkeeper Game
        if request.POST['action'] == "remove":
            try:
                game.delete()
                messages.success(request, _('Game removed successfully.'))
            except ProtectedError:
                messages.error(request, _("Error trying to delete the game."))

            return HttpResponseRedirect(reverse("goalkeeper_game_list"))

        # Remove a context from a game
        if request.POST['action'][:12] == "remove_path-":
            context_id = request.POST['action'][12:]
            try:
                get_context = Context.objects.get(pk=context_id)
            except Context.DoesNotExist:
                get_context = None

            if get_context:
                path = get_context.path
                get_context.delete()

                # After removing a context, check if there are others of the same depth that is not a context
                # and remove them as well.
                possible_context_to_remove = []
                for item in context_registered:
                    if len(item.path) == len(path) and item.is_context != 'True':
                        possible_context_to_remove.append(item)

                # Remove contexts with the same depth that is configured with is_context = False or Null.
                if possible_context_to_remove:
                    for context_to_remove in possible_context_to_remove:
                        context_to_remove.delete()

                # The user should be able to answer again whether a context is a real context or not.
                while path:
                    path = path[1:]
                    try:
                        update_context = Context.objects.get(goalkeeper=game, path=path)
                        if update_context:
                            update_context.analyzed = False
                            update_context.save()
                            break
                    except Context.DoesNotExist:
                        pass

                # Update the depth of the context tree
                if context_used:
                    depth = len(context_used.last().path) if context_used.last() else None
                    if game.depth != depth:
                        game.depth = depth
                        game.save()
                else:
                    game.depth = None
                    game.save()

            messages.success(request, _('Context removed successfully.'))
            redirect_url = reverse("goalkeeper_game_view", args=(goalkeeper_game_id,))
            return HttpResponseRedirect(redirect_url)

    context = {
        "game": game,
        "goalkeeper_game_form": goalkeeper_game_form,
        "probabilities": probabilities,
        "context_used": context_used,
        "context_list": context_list,
        "context_without_probability": context_without_probability,
        "last_context": last_context,
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
    :return: list of available contexts and list of contexts not analyzed
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
                    # Verification required in case of context removal
                    if not Context.objects.filter(goalkeeper=game, path=str(direction)+str(item.path)):
                        context_list.append(str(direction)+str(item.path))

        # Check if any height 1 context has been removed to add in the context_list
        for direction in range(game.number_of_directions):
            if not Context.objects.filter(goalkeeper=game, path=direction):
                context_list.append(str(direction))
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

        context_list, context_not_analyzed = available_context(goalkeeper_game_id)
        if context_list:
            redirect_url = reverse("context", args=(goalkeeper_game_id,))
        else:
            redirect_url = reverse("probability", args=(goalkeeper_game_id,))

        return HttpResponseRedirect(redirect_url)

    context = {
        "game": game,
        "context_list": context_list,
    }

    return render(request, template_name, context)


def check_contexts_without_probability(goalkeeper_game_id):
    list_of_contexts = Context.objects.filter(goalkeeper=goalkeeper_game_id, is_context=True)
    contexts_without_probability = []
    for item in list_of_contexts:
        if not Probability.objects.filter(context=item.pk):
            contexts_without_probability.append(item.path)

    if contexts_without_probability:
        return contexts_without_probability[0]
    else:
        return None


def check_probabilities(request, number_of_directions):
    """
    Function to check the probability inserted in each direction
    :param request: data sent by the user
    :param number_of_directions: number of directions registered in the game
    :return: dictionary with the probabilities and the sum of the probabilities
    """
    probabilities = {}
    total_prob = 0.0
    prob_for = request.POST['context']

    # Check the probability for each direction
    for direction in number_of_directions:
        prob = request.POST['context-' + prob_for + '-' + str(direction)].replace(',', '.')
        if prob:
            probabilities[direction] = float(prob)
            total_prob += float(prob)
        else:
            probabilities[direction] = 0.0

    return probabilities, total_prob


@login_required
def probability(request, goalkeeper_game_id, template_name="game/probability.html"):
    game = get_object_or_404(GoalkeeperGame, pk=goalkeeper_game_id)
    path = check_contexts_without_probability(goalkeeper_game_id)

    if request.method == "POST" and request.POST['action'] == "save":
        prob_for = request.POST['context']
        probabilities, total_prob = check_probabilities(request, range(game.number_of_directions))

        if total_prob == 1:
            # If the sum of the probabilities is equal to 1, create the probabilities for the path
            get_context = get_object_or_404(Context, goalkeeper=goalkeeper_game_id, path=prob_for)
            for key, value in probabilities.items():
                Probability.objects.create(context=get_context, direction=key, value=value)
            messages.success(request, _('Probability created successfully.'))

            # Update the depth of the context tree
            if game.depth != len(prob_for):
                game.depth = len(prob_for)
                game.save()
        else:
            messages.error(request, _('The sum of the probabilities must be equal to 1.'))

        path = check_contexts_without_probability(goalkeeper_game_id)
        if path:
            redirect_url = reverse("probability", args=(game.id,))
        else:
            redirect_url = reverse("goalkeeper_game_view", args=(goalkeeper_game_id,))

        return HttpResponseRedirect(redirect_url)

    context = {
        "game": game,
        "path": path,
        "number_of_directions": range(game.number_of_directions)
    }

    return render(request, template_name, context)


@login_required
def probability_update(request, context_id, template_name="game/probability.html"):
    path = get_object_or_404(Context, pk=context_id)
    game = get_object_or_404(GoalkeeperGame, pk=path.goalkeeper)
    probabilities = Probability.objects.filter(context=path).order_by('direction')

    if request.method == "POST" and request.POST['action'] == "save":
        values, total_prob = check_probabilities(request, range(game.number_of_directions))

        if total_prob == 1:
            # If the sum of the probabilities is equal to 1, update the probabilities for the path
            for key, value in values.items():
                probability_to_update = Probability.objects.get(context=path, direction=key)
                probability_to_update.value = value
                probability_to_update.save()
            messages.success(request, _('Probability updated successfully.'))
            redirect_url = reverse("goalkeeper_game_view", args=(game.pk,))

        else:
            messages.error(request, _('The sum of the probabilities must be equal to 1.'))
            redirect_url = reverse("probability_update", args=(path.id,))

        return HttpResponseRedirect(redirect_url)

    context = {
        "game": game,
        "number_of_directions": range(game.number_of_directions),
        "path": path.path,
        "probabilities": probabilities,
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
