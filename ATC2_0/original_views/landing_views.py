from django.shortcuts import render, redirect
from ..models import User


def landing_index(request):
    return render(request, 'landing/index.html')


def not_found(request):
    return render(request=request, template_name='landing/not-found.html', status=400)


def bad_input(request):
    return render(request, 'landing/bad-input.html')
