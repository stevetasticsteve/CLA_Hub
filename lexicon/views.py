from typing import Any, Dict
from django.shortcuts import render
from django.views import View
from django.views.generic.list import ListView
from django.http import FileResponse
from django.forms.models import model_to_dict


from lexicon import models

import os
import json


def get_lexicon_entries(matat_filter=False):
    """Top method for getting lexicon entrys in {'letter': [objects]}
    format."""
    words = get_db_models(matat_filter)
    return get_initial_letters(words)


def get_db_models(matat_filter):
    """Query the database and return Kovol words and verbs in alphabetical
    order."""
    if matat_filter:
        words = models.KovolWord.objects.exclude(matat__isnull=True)
        verbs = models.MatatVerb.objects.all()
        # verbs = [v.imengis_verb for v in verbs]
    else:
        words = models.KovolWord.objects.all()
        verbs = models.ImengisVerb.objects.all()

    for w in words:
        w.type = "word"
    for v in verbs:
        v.type = "verb"

    if matat_filter:
        for w in words:
            w.kgu = w.matat
        for v in verbs:
            v.pk = v.imengis_verb.pk

    lexicon = [w for w in words] + [v for v in verbs]
    return sorted(lexicon, key=lambda x: str(x))


def get_initial_letters(words):
    """Return a dict of initial letters as keys and the lexicon entries as
    values."""
    letters = set([str(w)[0] for w in words])
    lexicon = {letter: [w for w in words if str(w)[0] == letter] for letter in letters}
    return dict(sorted(lexicon.items()))


class LexiconView(View):
    """The main display for the lexicon, listing all entries."""

    def get(self, request):
        lexicon = get_lexicon_entries()
        context = {
            "lexicon": lexicon,
        }
        return render(request, "lexicon/main_view.html", context=context)


class MatatView(View):
    """The same as the main display, but filtered for matat data."""

    def get(self, request):
        lexicon = get_lexicon_entries(matat_filter=True)
        context = {
            "lexicon": lexicon,
        }
        return render(request, "lexicon/main_view.html", context=context)


class ReviewList(ListView):
    model = models.KovolWord
    paginate_by = 50
    template_name = "lexicon/review_list.html"

    def get_review_entries(self, review_id):
        words = models.KovolWord.objects.filter(review=review_id)
        verbs = models.ImengisVerb.objects.filter(review=review_id)
        for w in words:
            w.type = "word"
        for v in verbs:
            v.type = "verb"
        list_ = sorted([w for w in words] + [v for v in verbs], key=lambda x: str(x))
        return list_


class ReviewListView(ReviewList):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_list"] = self.get_review_entries("1")
        context["review_time"] = "now"
        return context


class ReviewLiteracyView(ReviewList):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_list"] = self.get_review_entries("2")
        context["review_time"] = "later"
        return context


class ExportView(View):
    def get(self, request):
        return render(request, "./lexicon/export.html")


def serve_file(file):
    response = FileResponse(open(file, "rb"))
    response["Content-Disposition"] = f"attachment; filename={os.path.basename(file)}"
    return response


def download_dic(*args):
    word_objs = get_db_models(matat_filter=False)
    words = []
    for w in word_objs:
        if w.type == "word":
            words.append(w.kgu)
        elif w.type == "verb":
            words += w.get_conjugations()

    dic_file = os.path.join("data", "lexicon.dic")
    with open(dic_file, "w") as file:
        file.write(str(len(words)))
        file.writelines([f"\n{w}" for w in words])
    return serve_file(dic_file)


def download_json(*args):
    word_objs = get_db_models(matat_filter=False)
    json_data = [model_to_dict(w) for w in word_objs]

    json_file = os.path.join("data", "lexicon.json")
    with open(json_file, "w") as file:
        json.dump(json_data, file)
    return serve_file(json_file)