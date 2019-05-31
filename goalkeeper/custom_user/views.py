from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.translation import ugettext as _

from .forms import UserForm, UserFormUpdate
from custom_user.models import Profile
from game.models import Level


@login_required
@permission_required('auth.add_user')
def user_list(request, template_name='custom_user/user_list.html'):
    users = User.objects.filter(is_active=True).order_by('username')
    data = {'users': users}
    return render(request, template_name, data)


@login_required
@permission_required('auth.add_user')
def new_user(request, template_name='custom_user/register_users.html'):
    form = UserForm(request.POST or None)

    if request.method == "POST" and request.POST['action'] == "save":
        if form.is_valid():
            user = form.save()

            try:
                user_level = Level.objects.get(name=0)
            except Level.DoesNotExist:
                user_level = Level.objects.create(name=0)

            Profile.objects.create(user=user, level=user_level)
            messages.success(request, _('User created successfully.'))
            return redirect('user_list')
        else:
            messages.warning(request, _('Information not saved.'))

    context = {
        'form': form,
        'creating': True,
    }

    return render(request, template_name, context)


@login_required
@permission_required('auth.change_user')
def update_user(request, user_id, template_name="custom_user/register_users.html"):
    user = get_object_or_404(User, pk=user_id)

    if user and user.is_active:
        form = UserFormUpdate(request.POST or None, instance=user)

        if request.method == "POST":
            if request.POST['action'] == "save":
                if form.is_valid():
                    form.save()
                    messages.success(request, _('User updated successfully.'))
                    return redirect('user_list')

            if request.POST['action'] == "remove":
                user = get_object_or_404(User, id=user_id)
                user.is_active = False
                user.save()
                messages.success(request, _('User deleted successfully.'))
                return redirect('user_list')

        context = {
            'form': form,
            'editing': True,
        }

        return render(request, template_name, context)
