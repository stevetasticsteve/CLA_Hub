import json
import os
import logging
from collections import Counter

from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms.models import model_to_dict
from django.http import FileResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.views.generic.list import ListView
from django.core.cache import cache

from lexicon import models
from lexicon import forms
from lexicon import utilities


logger = logging.getLogger("debug")


def get_lexicon_entries(matat_filter=False):
    """Returns all entries in {'letter': [objects]} format.

    Also sets the cache items lexicon (contains words, verbs and phrases) and
    lexicon words (contains words and verbs)."""

    utilities.get_lexicon_words_from_cache()
    return get_initial_letters(cache.get("lexicon"))


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
        phrases = models.PhraseEntry.objects.filter(review=review_id)

        for w in words:
            w.type = "word"
        for v in verbs:
            v.type = "verb"
        for p in phrases:
            p.type = "phrase"
        list_ = sorted(
            [w for w in words] + [v for v in verbs] + [p for p in phrases],
            key=lambda x: str(x),
        )
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
        context = {
            "version": models.LexiconMetaData.objects.get(pk=1).version,
            "total_words": len(utilities.get_word_list(checked=False)),
            "checked_words": len(utilities.get_word_list(checked=True)),
            "checked_counter": Counter(
                [w.pos for w in utilities.get_db_models(matat_filter=False)]
            ),
        }
        return render(request, "./lexicon/export.html", context=context)


class CreatePhrase(CreateView):
    model = models.PhraseEntry
    form_class = forms.PhraseForm
    template_name = "lexicon/simple_form.html"

    def form_valid(self, form, **kwargs):
        """Save changes to the sense and variation formsets."""
        obj = form.save(commit=False)
        obj.modified_by = self.request.user.username
        obj.save()
        return super().form_valid(form, **kwargs)


class PhraseDetail(DetailView):
    model = models.PhraseEntry
    context_object_name = "phrase"
    template_name = "lexicon/phrase_detail.html"

    def get_context_data(self, **kwargs):
        """Add senses and variations for the template to use."""
        context = super().get_context_data(**kwargs)
        context["phrase_senses"] = models.PhraseSense.objects.filter(phrase=self.object)
        context["spelling_variations"] = models.PhraseSpellingVariation.objects.filter(
            phrase=self.object
        )

        return context


class UpdatePhrase(UpdateView):
    model = models.PhraseEntry
    template_name = "lexicon/simple_form.html"
    form_class = forms.PhraseForm

    def form_valid(self, form, **kwargs):
        self.object.modified_by = self.request.user.username
        return super().form_valid(form, **kwargs)


class DeletePhrase(DeleteView):
    model = models.PhraseEntry
    fields = None
    template_name = "lexicon/confirm_word_delete.html"
    success_url = success_url = reverse_lazy("lexicon:main")


class DeleteWordView(LoginRequiredMixin, DeleteView):
    """The view at url word/1/delete. Deletes a word."""

    model = models.KovolWord
    fields = None
    template_name = "lexicon/confirm_word_delete.html"
    success_url = success_url = reverse_lazy("lexicon:main")


class CreatePhraseSenseView(LoginRequiredMixin, CreateView):
    """The view at url word/1/add-sense. Adds a sense to a word."""

    model = models.PhraseSense
    fields = ["sense"]
    template_name = "lexicon/simple_form.html"

    def form_valid(self, form):
        """Give the Foreign key of the word to the form."""
        form.instance.phrase = models.PhraseEntry.objects.get(pk=self.kwargs["pk"])
        return super().form_valid(form)


class CreatePhraseVariationView(LoginRequiredMixin, CreateView):
    """The view at url word/1/add-spelling. Adds a spelling variation to a word."""

    model = models.PhraseSpellingVariation
    fields = ["spelling_variation"]
    template_name = "lexicon/simple_form.html"

    def form_valid(self, form):
        """Give the Foreign key of the word to the form."""
        form.instance.phrase = models.PhraseEntry.objects.get(pk=self.kwargs["pk"])
        return super().form_valid(form)


def serve_file(file):
    response = FileResponse(open(file, "rb"))
    response["Content-Disposition"] = f"attachment; filename={os.path.basename(file)}"
    return response


def download_dic(*args):
    words = utilities.get_word_list(checked=True)

    dic_file = os.path.join("data", "lexicon.dic")
    with open(dic_file, "w") as file:
        file.write(str(len(words)))
        file.writelines([f"\n{w}" for w in words])
    return serve_file(dic_file)


def download_json(*args):
    word_objs = utilities.get_db_models(matat_filter=False)
    json_data = [model_to_dict(w) for w in word_objs]

    json_file = os.path.join("data", "lexicon.json")
    with open(json_file, "w") as file:
        json.dump(json_data, file)
    return serve_file(json_file)


def download_oxt(*args):
    return serve_file(utilities.write_oxt_package())
