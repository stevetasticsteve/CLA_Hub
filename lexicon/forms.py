from django import forms
from django.forms import ModelForm

import lexicon.models as models
import lexicon.utilities

phrase_fields = [
    "kgu",
    "linked_word",
    "eng",
    "tpi",
    "matat",
    "comments",
    "review",
    "review_comments",
]


def get_model_choices():
    words = lexicon.utilities.get_words_queryset_from_cache()
    choices = []
    for w in words:
        if w.type == "word":
            text = f'{w.kgu} "{w.eng}" - word'
        else:
            text = f'{w.future_1s}, "{w.eng}" - verb'
        choices.append((w, text))
        print(type(w))
    return choices


class WordSenseForm(ModelForm):
    class Meta:
        model = models.KovolWordSense
        fields = ["sense"]


class WordVariationForm(ModelForm):
    class Meta:
        model = models.KovolWordSpellingVariation
        fields = ["spelling_variation"]


class VerbSenseForm(ModelForm):
    class Meta:
        model = models.VerbSense
        fields = ["sense"]


class VerbVariationForm(ModelForm):
    class Meta:
        model = models.VerbSpellingVariation
        fields = ["conjugation", "spelling_variation"]


class PhraseForm(ModelForm):

    # linked_word = forms.ChoiceField(choices=get_model_choices())
    linked_word = forms.ModelChoiceField(
        models.LexiconEntry.objects.exclude(
            phraseentry__pos="phr"
        ).order_by("kovolword__kgu", "lexiconverbentry__future_1s")
    )

    class Meta:
        model = models.PhraseEntry
        fields = phrase_fields
