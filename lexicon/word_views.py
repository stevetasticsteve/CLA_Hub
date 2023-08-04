"""Views that deal with creating, updating and deleting words."""
from django.forms import inlineformset_factory
from django.urls import reverse_lazy
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView

import datetime

from lexicon import forms, models

# Defining the order fields are to be displayed in
word_form_fields = [
    "kgu",
    "eng",
    "matat",
    "tpi",
    "pos",
    "comments",
    "checked",
    "review",
    "review_comments",
]

# Create inline formsets for adding one to many fields to forms
sense_inline_form = inlineformset_factory(
    models.KovolWord, models.KovolWordSense, form=forms.WordSenseForm, extra=0
)

variation_inline_form = inlineformset_factory(
    models.KovolWord,
    models.KovolWordSpellingVariation,
    form=forms.WordVariationForm,
    extra=0,
)


class WordDetailView(DetailView):
    """The view at url word/1/detail. Displays all info in .db for a word."""

    model = models.KovolWord
    context_object_name = "word"
    template_name = "lexicon/word_detail.html"

    def get_context_data(self, **kwargs):
        """Add senses and variations for the template to use."""
        context = super().get_context_data(**kwargs)
        context["word_senses"] = models.KovolWordSense.objects.filter(word=self.object)
        context[
            "spelling_variations"
        ] = models.KovolWordSpellingVariation.objects.filter(word=self.object)
        context["phrases"] = models.PhraseEntry.objects.filter(linked_word=self.object)

        return context


class CreateWordView(CreateView):
    """The view at url word/1/create. Creates a new word."""

    model = models.KovolWord
    fields = word_form_fields
    template_name = "lexicon/simple_form.html"


class UpdateWordView(UpdateView):
    """The view at url /word/1/update. Updates words.

    get_context_data and form_valid are extended to add in inline formsets representing
    the one to many relationships of spelling variations and senses.
    The inline formsets allow deleting sense and spelling variations so a delete view
    isn't required.
    """

    model = models.KovolWord
    fields = word_form_fields
    template_name = "lexicon/word_update_form.html"

    def get_context_data(self, **kwargs):
        """Add formsets to the context data for the template to use."""
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context["senses_form"] = sense_inline_form(
                self.request.POST, prefix="sense", instance=self.object
            )
            context["variation_form"] = variation_inline_form(
                self.request.POST, prefix="spelling_variation", instance=self.object
            )
        else:
            context["sense_form"] = sense_inline_form(
                prefix="sense", instance=self.object
            )
            context["variation_form"] = variation_inline_form(
                prefix="spelling_variation", instance=self.object
            )
        return context

    def form_valid(self, form, **kwargs):
        """Save changes to the sense and variation formsets."""
        context = self.get_context_data()
        sense_form = context["senses_form"]
        variation_form = context["variation_form"]
        if sense_form.is_valid():
            sense_form.save()
        if variation_form.is_valid():
            variation_form.save()
        self.object.modified_by = self.request.user.username
        if "review" in form.changed_data:
            self.object.review_user = self.request.user.username
            self.object.review_time = datetime.date.today()
        return super().form_valid(form, **kwargs)


class DeleteWordView(DeleteView):
    """The view at url word/1/delete. Deletes a word."""

    model = models.KovolWord
    fields = None
    template_name = "lexicon/confirm_word_delete.html"
    success_url = success_url = reverse_lazy("lexicon:main")


class CreateWordSenseView(CreateView):
    """The view at url word/1/add-sense. Adds a sense to a word."""

    model = models.KovolWordSense
    fields = ["sense"]
    template_name = "lexicon/simple_form.html"

    def form_valid(self, form):
        """Give the Foreign key of the word to the form."""
        form.instance.word = models.KovolWord.objects.get(pk=self.kwargs["pk"])
        return super().form_valid(form)


class CreateWordVariationView(CreateView):
    """The view at url word/1/add-spelling. Adds a spelling variation to a word."""

    model = models.KovolWordSpellingVariation
    fields = ["spelling_variation"]
    template_name = "lexicon/simple_form.html"

    def form_valid(self, form):
        """Give the Foreign key of the word to the form."""
        form.instance.word = models.KovolWord.objects.get(pk=self.kwargs["pk"])
        return super().form_valid(form)
