from django.shortcuts import redirect


def redirect_short_link(request, id):
    return redirect(f'/recipes/{id}/')
