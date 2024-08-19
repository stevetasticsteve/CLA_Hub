"""Views for managing ignore words to be included in the spell check."""

from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.urls import reverse_lazy


from lexicon.models import IgnoreWord


class CreateIgnoreWordView(LoginRequiredMixin, CreateView):
    """The view at url ignore/1/create. Creates a new ignore view."""

    template_name = "lexicon/ignore_word_form.html"
    model = IgnoreWord
    fields = "__all__"
    success_url = success_url = reverse_lazy("lexicon:ignore")


class UpdateIgnoreWordView(LoginRequiredMixin, UpdateView):
    """The view at url ignore/1/update. Updates a new ignore view."""

    template_name = "lexicon/ignore_word_form.html"
    model = IgnoreWord
    fields = "__all__"
    success_url = success_url = reverse_lazy("lexicon:ignore")


class DeleteIgnoreWordView(LoginRequiredMixin, DeleteView):
    """The view at url ignore/1/delete. Deletes a new ignore view."""

    model = IgnoreWord
    fields = None
    template_name = "lexicon/confirm_word_delete.html"
    success_url = success_url = reverse_lazy("lexicon:ignore")


class IgnoreListView(ListView):
    """The view at url ignore. Lists all the ignore words."""

    model = IgnoreWord
    template_name = "lexicon/ignore_word_list.html"

