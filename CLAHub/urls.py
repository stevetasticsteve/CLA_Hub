"""CLAHub URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.staticfiles.urls import static, staticfiles_urlpatterns
from . import settings, views
from CLAHub.base_settings import CLAHUB_VERSION as version

urlpatterns = [
    path("admin/", admin.site.urls),
    path("tools/", views.tools, name="tools"),
    path("tools/import-profiles", views.import_profiles, name="import_profiles"),
    path("CE/", include("CE.urls")),
    path("people/", include("people.urls")),
    path("lexicon/", include("lexicon.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("", views.home, name="home"),
    path("help/markdown", views.markdown, name="markdown"),
    path("help/texts", views.text_features, name="text_features"),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

admin.site.site_header = "CLAHub admin v.{version}".format(version=version)
admin.site.site_title = "CLAHub"
