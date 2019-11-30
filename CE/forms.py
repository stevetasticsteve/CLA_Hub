from django import forms
from django.contrib import messages
from django.core import exceptions

import taggit.forms
import CE.models
import CE.settings

if CE.settings.auto_cross_reference:
    description_placeholder = 'Auto cross reference is on. If you type the (lowercase) title of an existing CE' \
                              ' it will become a hyperlink.'
else:
    description_placeholder = 'Auto cross reference is off. To insert a cross reference put the title of an existing' \
                              ' CE within curly brackets like this: {fishing}'


class DateInput(forms.DateInput):
    input_type = 'date'

class CE_EditForm(forms.Form):
    title = forms.CharField(
        required=True,
        label='CE title',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Title (Required)',
        })
    )

    tags = taggit.forms.TagField(
        required=False,
        label='Tags',
        widget=taggit.forms.TagWidget(attrs={
            'class': 'form-control',
            'data-role': 'tagsinput',
            'type': 'text',
            'name': 'tags'
        })
    )

    description_plain_text = forms.CharField(
        required=False,
        label='Description: What happened? Try to stick to the facts.',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': description_placeholder,
            'rows': 5
        })
    )


    differences = forms.CharField(
        required=False,
        label='Variation',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'If CE has been visited multiple times comment on how it changes or remains the same.',
            'rows': 3
        })
    )
    interpretation = forms.CharField(
        required=False,
        label='Interpretation',
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Write down personal comments, observations, hypothesis and hunches.',
            'rows': 3
        })
    )
    picture = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control'
        }))


    def save(self, request, **kwargs):
        # the instance kwarg is passed in if a prexisting record needs updating
        # without an instance a new .db entry is created
        if 'instance' in kwargs:
            ce = CE.models.CultureEvent.objects.get(pk=kwargs['instance'].pk)
        else:
            ce = CE.models.CultureEvent()
        ce.title = self.cleaned_data['title']
        ce.description_plain_text = self.cleaned_data['description_plain_text']
        ce.last_modified_by = str(request.user)
        ce.interpretation = self.cleaned_data['interpretation']
        ce.differences = self.cleaned_data['differences']
        ce.save()

        if self.cleaned_data['tags']:
            for tag in self.cleaned_data['tags']:
                ce.tags.add(tag)

        if self.cleaned_data['picture']:
            new_pic = CE.models.Picture()
            new_pic.ce = ce
            new_pic.picture = self.cleaned_data['picture']
            new_pic.save()

        if 'instance' in kwargs:
            messages.success(request, 'CE updated')
        else:
            messages.success(request, 'New CE created')
        return ce


def prepopulated_CE_form(ce):
    form = CE_EditForm(initial={
    'title': ce.title,
    'tags': ce.tags.all(),
    'description_plain_text': ce.description_plain_text,
    'differences': ce.differences,
    'interpretation': ce.interpretation
    })

    return form


class TextForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # init method injects 'form-control' in to enable bootstrap styling
        super(TextForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

    class Meta:
        model = CE.models.Text
        exclude = ('ce', 'DELETE')

    def save(self, **kwargs):
        # only save the form if user has entered data. Otherwise default fields will be filled in
        # and an entry made despite no user input
        try:
            if self.cleaned_data['phonetic_text'] or self.cleaned_data['orthographic_text']\
            or self.cleaned_data['audio'] or self.cleaned_data['text_title']:
                super(TextForm, self).save()
        except KeyError:
            pass


text_form_set = forms.modelformset_factory(CE.models.Text, form=TextForm, extra=0)


def text_formset_prepopulated(ce):
    text_data = CE.models.Text.objects.filter(ce=ce)
    text_forms = []
    for data in text_data:
        text_form = text_form_set(initial=[{
            'audio': data.audio,
            'phonetic_text': data.phonetic_text,
            'orthographic_text': data.orthographic_text,
            'phonetic_standard': data.phonetic_standard,
            'valid_for_DA': data.valid_for_DA,
            'discourse_type': data.discourse_type
    }], prefix='text')
        text_forms.append(text_form)
    return text_forms


class QuestionForm(forms.ModelForm):
    class Meta:
        model = CE.models.Question
        fields = ('question', 'answer')

    def save(self, **kwargs):
        # only save the form if user has entered data. Otherwise default fields will be filled in
        # and an entry made despite no user input
        try:
            if self.cleaned_data['question']:
                self.instance.last_modified_by= str(kwargs['request'].user)
                self.instance.asked_by = str(kwargs['request'].user)
                super(QuestionForm, self).save()
        except KeyError:
            pass


class VisitsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # init method injects 'form-control' in to enable bootstrap styling
        super(VisitsForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

    class Meta:
        model = CE.models.Visit
        fields = ('team_present', 'nationals_present', 'date')
        widgets = {
            'date': DateInput()
        }

    def save(self, **kwargs):
        # only save the form if user has entered data. Otherwise default fields will be filled in
        # and an entry made despite no user input
        try:
            if self.cleaned_data:
                super(VisitsForm, self).save()
        except KeyError:
            pass




