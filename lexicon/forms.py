from django.forms import ModelForm
import lexicon.models as models


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
