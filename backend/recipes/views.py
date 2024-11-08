from django.http import Http404
from django.shortcuts import redirect

from recipes.models import Recipe


def redirect_short_link(request, pk):
    if not Recipe.objects.filter(pk=pk).exists():
        raise Http404(f'Неверный ключ {pk}')
    return redirect(f'/recipes/{pk}/')
