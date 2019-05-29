from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models.deletion import ProtectedError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse
from django.utils.translation import activate, LANGUAGE_SESSION_KEY, ugettext as _

from .forms import GoalkeeperGameForm
from .models import Context, GoalkeeperGame, Probability


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

    for field in goalkeeper_game_form.fields:
        goalkeeper_game_form.fields[field].widget.attrs['disabled'] = True

    if request.method == "POST" and request.POST['action'] == "remove":
        try:
            game.delete()
            messages.success(request, _('Game removed successfully.'))
            return redirect('home')
        except ProtectedError:
            messages.error(request, _("Error trying to delete the game."))
            redirect_url = reverse("goalkeeper_game_view", args=(goalkeeper_game_id,))
            return HttpResponseRedirect(redirect_url)

    context = {
        "game": game,
        "goalkeeper_game_form": goalkeeper_game_form,
        "probabilities": probabilities,
        "context_used": context_used,
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
                messages.warning(request, _('There is no changes to save.'))
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
    game = get_object_or_404(GoalkeeperGame, pk=goalkeeper_game_id)
    context_used = Context.objects.filter(goalkeeper=game).order_by('path')
    context_list = []

    if context_used:
        for direction in range(game.number_of_directions):
            context_list.append(direction)

        context_used_list = []
        for context in context_used:
            path = context.path
            context_used_list.append(path)
            probabilities = Probability.objects.filter(context=context.pk, value__gt=0)

            for item in probabilities:
                context_list.append(path+str(item.direction))

        for context in context_used_list:
            context_size = len(context)
            while context_size > 0:
                if int(context) in context_list:
                    context_list.remove(int(context))
                context = context[1:]
                context_size -= 1

        for context in context_list:
            context_size = len(str(context))
            context_aux = str(context)
            while context_size > 0:
                if context_aux in context_used_list:
                    context_list.remove(context)
                context_aux = context_aux[1:]
                context_size -= 1

    else:
        for direction in range(game.number_of_directions):
            context_list.append(direction)

    return context_list


@login_required
def context(request, goalkeeper_game_id, template_name="game/probability.html"):
    game = get_object_or_404(GoalkeeperGame, pk=goalkeeper_game_id)
    context_list = available_context(goalkeeper_game_id)
    probability = {}
    total_prob = 0.0

    if request.method == "POST" and request.POST['action'] == "save":
        for direction in range(game.number_of_directions):
            prob = request.POST['context-'+str(direction)].replace(',', '.')
            if prob:
                probability[direction] = float(prob)
                total_prob += float(prob)
            else:
                probability[direction] = 0.0

        if total_prob == 1:
            new_context = Context.objects.create(goalkeeper=game, path=request.POST['path'])
            for key, value in probability.items():
                Probability.objects.create(context=new_context, direction=key, value=value)

            messages.success(request, _('Probability created successfully.'))
            redirect_url = reverse("goalkeeper_game_view", args=(game.id,))
            return HttpResponseRedirect(redirect_url)

        else:
            messages.error(request, _('The sum of the probabilities must be equal to 1.'))
            redirect_url = reverse("context", args=(game.id,))
            return HttpResponseRedirect(redirect_url)

    context = {
        "game": game,
        "number_of_directions": range(game.number_of_directions),
        "context_list": context_list,
        "probability": probability
    }

    return render(request, template_name, context)
