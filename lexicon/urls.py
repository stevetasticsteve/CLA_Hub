from django.urls import path
import lexicon.views

app_name = "lexicon"

urlpatterns = [
    path("main/", lexicon.views.LexiconView.as_view(), name="main"),
]
