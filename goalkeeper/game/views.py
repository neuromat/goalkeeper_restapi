from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models.deletion import ProtectedError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils.translation import activate, LANGUAGE_SESSION_KEY, ugettext as _

from rest_framework import generics, permissions

from .forms import GoalkeeperGameForm
from .models import Context, GoalkeeperGame, Probability, GameConfig, Level
from .serializers import GameConfigSerializer, GameSerializer, ContextSerializer, ProbSerializer


@login_required
def home(request, template_name="game/home.html"):
    return render(request, template_name)


def language_change(request, language_code):
    activate(language_code)
    request.session[LANGUAGE_SESSION_KEY] = language_code
    return HttpResponseRedirect(request.GET['next'])


@login_required
def goalkeeper_game_list(request, template_name="game/goalkeeper_game_list.html"):
    games = GoalkeeperGame.objects.all().order_by('config', 'phase')

    context = {
        "games": games,
        "creating": True
    }

    return render(request, template_name, context)


@login_required
def goalkeeper_game_new(request, template_name="game/goalkeeper_game.html"):
    goalkeeper_game_form = GoalkeeperGameForm(request.POST or None)

    if request.method == "POST" and request.POST['action'] == "save":
        if goalkeeper_game_form.is_valid():
            game = goalkeeper_game_form.save(commit=False)
            game.save()

            messages.success(request, _('Goalkeeper game created successfully.'))
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
                return redirect('home')
            except ProtectedError:
                messages.error(request, _("Error trying to delete the game."))
                redirect_url = reverse("goalkeeper_game_view", args=(goalkeeper_game_id,))
                return HttpResponseRedirect(redirect_url)

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
                messages.success(request, _('Goalkeeper game updated successfully.'))
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
    context_used = Context.objects.filter(goalkeeper=game).order_by('path')
    context_list = []

    if context_used:
        # Start the list of available context with 0 until the number_of_directions
        for direction in range(game.number_of_directions):
            context_list.append(str(direction))

        context_used_list = []
        # For each context already registered, check the directions with a value greater than 0
        for context in context_used:
            path = context.path
            context_used_list.append(path)
            probabilities = Probability.objects.filter(context=context.pk, value__gt=0)

            # For each direction with a value greater than 0, create a new context concatenating the path and the
            # direction. Repeat this action slicing the path, eg: 201 -> 01 -> 1.
            for item in probabilities:
                new_path = path + str(item.direction)
                context_list.append(new_path)
                while len(new_path) > 0:
                    new_path = new_path[1:]
                    if new_path and new_path not in context_list:
                        context_list.append(new_path)

        # Remove the context already used
        for context in context_used_list:
            while len(context) > 0:
                if context in context_list:
                    context_list.remove(context)
                context = context[1:]

        # Remove the context already used but also slicing the context, eg: 201 -> 01 -> 1.
        remove_this_context = []
        for context in context_list:
            context_aux = context
            while len(context_aux) > 0:
                if context_aux in context_used_list:
                    remove_this_context.append(context)
                context_aux = context_aux[1:]

        context_list = sorted(list(set(context_list) - set(remove_this_context)))

    else:
        # Start the list of available context with 0 until the number_of_directions
        for direction in range(game.number_of_directions):
            context_list.append(str(direction))

    return context_list


@login_required
def context_tree(request, goalkeeper_game_id, template_name="game/probability.html"):
    """
    An instance of this class is a context with its probabilities
    :param request: request method
    :param goalkeeper_game_id: ID of the game for which a context will be created
    :param template_name: template used to create the context
    :return: data available to create the context
    """
    game = get_object_or_404(GoalkeeperGame, pk=goalkeeper_game_id)
    probabilities = Probability.objects.filter(context__goalkeeper=game)
    context_used = Context.objects.filter(goalkeeper=game)
    context_list = available_context(goalkeeper_game_id)
    probability = {}
    total_prob = 0.0

    if request.method == "POST":
        if request.POST['action'] == "save":
            # Check the probability for each direction
            for direction in range(game.number_of_directions):
                prob = request.POST['context-'+str(direction)].replace(',', '.')
                if prob:
                    probability[direction] = float(prob)
                    total_prob += float(prob)
                else:
                    probability[direction] = 0.0

            if total_prob == 1:
                # If the sum of the probabilities is equal to 1, create the probabilities for the path
                new_context = Context.objects.create(goalkeeper=game, path=request.POST['path'])
                for key, value in probability.items():
                    Probability.objects.create(context=new_context, direction=key, value=value)

                context_available = available_context(goalkeeper_game_id)
                if context_available:
                    messages.success(request, _('Probability created successfully.'))
                    redirect_url = reverse("context", args=(goalkeeper_game_id,))
                else:
                    messages.success(request, _('Context tree created successfully.'))
                    redirect_url = reverse("goalkeeper_game_view", args=(goalkeeper_game_id,))

                return HttpResponseRedirect(redirect_url)

            else:
                messages.error(request, _('The sum of the probabilities must be equal to 1.'))
                redirect_url = reverse("context", args=(game.id,))
                return HttpResponseRedirect(redirect_url)

        if request.POST['action'][:12] == "remove_path-":
            get_context = get_object_or_404(Context, pk=request.POST['action'][12:])
            get_context.delete()
            messages.success(request, _('Context removed successfully.'))
            redirect_url = reverse("context", args=(goalkeeper_game_id,))
            return HttpResponseRedirect(redirect_url)

    context = {
        "game": game,
        "number_of_directions": range(game.number_of_directions),
        "context_list": context_list,
        "probabilities": probabilities,
        "context_used": context_used
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
        name_req = self.request.query_params.get('name', None)

        if level is not None:
            queryset = queryset.filter(level__lte=level)

        if name_req is not None:
            queryset = queryset.filter(name=name_req)

        return queryset.order_by('id')


class GetGames(generics.ListCreateAPIView):
    serializer_class = GameSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    http_method_names = ['get', 'head']

    def get_queryset(self):
        config_id = self.request.query_params.get('config_id', None)
        queryset = GoalkeeperGame.objects.filter(game_type="JG", config=config_id)
        phase = self.request.query_params.get('phase', None)

        if phase is not None:
            queryset = queryset.filter(phase=phase)

        return queryset.order_by("phase")


class GetContexts(generics.ListCreateAPIView):
    serializer_class = ContextSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    http_method_names = ['get', 'head']

    def get_queryset(self):
        game_id_req = self.request.query_params.get('game', None)
        queryset = Context.objects.filter(goalkeeper=game_id_req) if game_id_req else None

        return queryset.order_by('id')


class GetProbs(generics.ListCreateAPIView):
    serializer_class = ProbSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    http_method_names = ['get', 'head']

    def get_queryset(self):
        context_id_req = self.request.query_params.get('context', None)
        queryset = Probability.objects.filter(context=context_id_req) if context_tree else None

        direction = self.request.query_params.get('direction', None)

        if direction is not None:
            queryset = queryset.filter(direction=direction)

        return queryset.order_by('direction')
