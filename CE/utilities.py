from django.contrib.auth.decorators import login_required
import CE.settings


def conditional_login(func):
    if CE.settings.login_everywhere:
        return login_required(func)
    else:
        return func
