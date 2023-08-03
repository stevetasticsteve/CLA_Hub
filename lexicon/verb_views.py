from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.forms import inlineformset_factory

from django.urls import reverse_lazy
from django.forms.models import model_to_dict


from lexicon import forms, models
from django.views.generic import DetailView
import datetime

# Create inline formsets for adding one to many fields to forms
sense_inline_form = inlineformset_factory(
    models.ImengisVerb, models.VerbSense, form=forms.VerbSenseForm, extra=0
)

variation_inline_form = inlineformset_factory(
    models.ImengisVerb,
    models.VerbSpellingVariation,
    form=forms.VerbVariationForm,
    extra=0,
)


class VerbDetailView(DetailView):
    """The view at url verb/1/detail. Displays all info in .db for a verb."""

    model = models.ImengisVerb
    context_object_name = "word"
    template_name = "lexicon/verb_detail.html"

    def get_context_data(self, **kwargs):
        """Add senses, spelling and Matat object for the template to use."""
        context = super().get_context_data(**kwargs)
        context["verb_senses"] = models.VerbSense.objects.filter(verb=self.object)
        context["spelling_variations"] = models.VerbSpellingVariation.objects.filter(
            verb=self.object
        )
        context["matat"] = models.MatatVerb.objects.filter(
            imengis_verb=self.object
        ).first()
        return context


class CreateVerbView(CreateView):
    """The view at url verb/1/create. Creates a new verb."""

    model = models.ImengisVerb
    fields = "__all__"
    template_name = "lexicon/simple_form.html"


class VerbUpdateView(UpdateView):
    """The view at url verb/1/edit. Updates verb, senses and spellings.

    get_context_data and form_valid are extended to add in inline formsets representing
    the one to many relationships of spelling variations and senses.
    The inline formsets allow deleting sense and spelling variations so a delete view
    isn't required.
    """

    model = models.ImengisVerb
    template_name = "lexicon/verb_update_form.html"
    fields = "__all__"

    def get_context_data(self, **kwargs):
        """Add formsets to the context data for the template to use."""
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            print(self.request.POST)
            context["senses_form"] = sense_inline_form(
                self.request.POST, prefix="sense", instance=self.object
            )
            context["variation_form"] = variation_inline_form(
                self.request.POST, prefix="spelling_variation", instance=self.object
            )
        else:
            print("get")
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


class DeleteVerbView(DeleteView):
    """The view at url word/1/delete. Deletes a word."""

    model = models.ImengisVerb
    fields = None
    template_name = "lexicon/confirm_word_delete.html"
    success_url = success_url = reverse_lazy("lexicon:main")


class CreateVerbSenseView(CreateView):
    """The view at url verb/1/add-sense. Adds a sense to a verb."""

    model = models.VerbSense
    fields = ["sense"]
    template_name = "lexicon/simple_form.html"

    def form_valid(self, form):
        """Give the Foreign key of the word to the form."""
        form.instance.verb = models.ImengisVerb.objects.get(pk=self.kwargs["pk"])
        return super().form_valid(form)


class CreateMatatVerbView(CreateView):
    """The view at url verb/1/matat-create. Adds a matat paradigm to a verb."""

    model = models.MatatVerb
    fields = models.LexiconVerbEntry.verb_text_fields
    template_name = "lexicon/simple_form.html"

    def get_context_data(self, **kwargs):
        """Prepopulate Matat paradigm with Imengis data."""
        context = super().get_context_data(**kwargs)
        imengis_verb = models.ImengisVerb.objects.get(pk=self.kwargs.get("pk"))
        context["form"].initial = model_to_dict(
            imengis_verb, fields=models.LexiconVerbEntry.verb_text_fields
        )
        return context

    def form_valid(self, form):
        """Save the foreign key from related model, along with eng and tpi."""
        imengis_verb = models.ImengisVerb.objects.get(pk=self.kwargs.get("pk"))
        form.instance.imengis_verb = imengis_verb
        form.instance.eng = imengis_verb.eng
        form.instance.tpi = imengis_verb.tpi
        form.instance.created = datetime.datetime.now()
        return super().form_valid(form)


class UpdateMatatVerbView(UpdateView):
    """The view at url verb/1/matat-update. Edits a matat paradigm to a verb."""

    model = models.MatatVerb
    fields = models.LexiconVerbEntry.verb_text_fields
    template_name = "lexicon/simple_form.html"


class DeleteMatatVerbView(DeleteView):
    """The view at url word/1/matat-delete. Deletes a matat verb."""

    model = models.MatatVerb
    fields = None
    template_name = "lexicon/confirm_word_delete.html"
    success_url = success_url = reverse_lazy("lexicon:main")


class CreateVerbSpellingView(CreateView):
    """The view at url verb/1/add-spelling. Adds a spelling variation to a verb."""

    model = models.VerbSpellingVariation
    fields = ["spelling_variation", "conjugation"]
    template_name = "lexicon/simple_form.html"

    def form_valid(self, form):
        """Give the Foreign key of the word to the form."""
        form.instance.verb = models.ImengisVerb.objects.get(pk=self.kwargs["pk"])
        return super().form_valid(form)
