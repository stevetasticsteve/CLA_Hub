from django.urls import path

import lexicon.views
import lexicon.verb_views
import lexicon.word_views

app_name = "lexicon"

urlpatterns = [
    path("main/", lexicon.views.LexiconView.as_view(), name="main"),
    path("matat/", lexicon.views.MatatView.as_view(), name="matat"),
    path("review-now/", lexicon.views.ReviewListView.as_view(), name="review-now"),
    path(
        "review-literacy/",
        lexicon.views.ReviewLiteracyView.as_view(),
        name="review-literacy",
    ),
    path("export/", lexicon.views.ExportView.as_view(), name="export"),
    path("download-dic/", lexicon.views.download_dic, name="dic_download"),
    path("download-json/", lexicon.views.download_json, name="json_download"),
    path(
        "verb/<int:pk>/detail",
        lexicon.verb_views.VerbDetailView.as_view(),
        name="verb-detail",
    ),
    path(
        "verb/create", lexicon.verb_views.CreateVerbView.as_view(), name="verb-create"
    ),
    path(
        "verb/<int:pk>/edit",
        lexicon.verb_views.VerbUpdateView.as_view(),
        name="verb-update",
    ),
    path(
        "verb/<int:pk>/delete",
        lexicon.verb_views.DeleteVerbView.as_view(),
        name="verb-delete",
    ),
    path(
        "verb/<int:pk>/add-sense",
        lexicon.verb_views.CreateVerbSenseView.as_view(),
        name="verb-add-sense",
    ),
    path(
        "verb/<int:pk>/add-spelling",
        lexicon.verb_views.CreateVerbSpellingView.as_view(),
        name="verb-add-spelling",
    ),
    path(
        "verb/<int:pk>/matat-create",
        lexicon.verb_views.CreateMatatVerbView.as_view(),
        name="verb-create-matat",
    ),
    path(
        "verb/<int:pk>/matat-update",
        lexicon.verb_views.UpdateMatatVerbView.as_view(),
        name="verb-update-matat",
    ),
    path(
        "verb/<int:pk>/matat-delete",
        lexicon.verb_views.DeleteMatatVerbView.as_view(),
        name="verb-delete-matat",
    ),
    path(
        "word/<int:pk>/detail",
        lexicon.word_views.WordDetailView.as_view(),
        name="word-detail",
    ),
    path(
        "word/create", lexicon.word_views.CreateWordView.as_view(), name="word-create"
    ),
    path(
        "word/<int:pk>/update",
        lexicon.word_views.UpdateWordView.as_view(),
        name="word-update",
    ),
    path(
        "word/<int:pk>/delete",
        lexicon.word_views.DeleteWordView.as_view(),
        name="word-delete",
    ),
    path(
        "word/<int:pk>/add-sense",
        lexicon.word_views.CreateWordSenseView.as_view(),
        name="word-add-sense",
    ),
    path(
        "word/<int:pk>/add-spelling",
        lexicon.word_views.CreateWordVariationView.as_view(),
        name="word-add-spelling",
    ),
]