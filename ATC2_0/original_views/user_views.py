from django.shortcuts import render, redirect

from ATC.views.validation import set_coords, validate_username
from ..models import User


def users_index(request):
    return render(request, 'users/index.html', {
        'users': User.objects.all().order_by("username")
    })


def users_create(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username == "" or not validate_username(username, User, -1):
            return render(request, 'landing/bad-input.html', status=420)

        user = User()
        user.username = username
        user.password = password
        user.save()

        return redirect(users_index)
    return render(request, 'users/create.html', {})


def users_update(request, user_id):
    if User.objects.filter(pk=user_id).count() != 1:  # validate exists
        return render(request, 'landing/not-found.html', status=404)

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if not validate_username(username, User, user_id):
            return render(request, 'landing/bad-input.html', status=420)

        user = User.objects.get(pk=user_id)
        if username != "":
            user.username = username

        if password != "":
            user.password = password

        user.save()
        return redirect(users_index)
    return render(request, 'users/update.html', {
        'user': User.objects.get(pk=user_id)
    })


def users_delete(request, user_id):
    if User.objects.filter(pk=user_id).count() != 1:  # validate exists
        return render(request, 'landing/not-found.html', status=404)

    User.objects.get(pk=user_id).delete()
    return redirect(users_index)
