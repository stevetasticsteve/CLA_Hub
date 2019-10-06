from django.contrib.auth.decorators import login_required
import CLAHub.base_settings


def conditional_login(func):
    if CLAHub.base_settings.LOGIN_EVERYWHERE:
        return login_required(func)
    else:
        return func
