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
    picture = forms.ImageField(required=False)


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
            new_pic = CE.models.PictureModel()
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

class TextForm(forms.Form):
    audio = forms.FileField(
        label='Upload audio',
        required=False
    )
    phonetic_text = forms.CharField(
        required=False,
        label='Phonetic transcription',
        widget=forms.Textarea(attrs={
        'class': 'form-control',
        'placeholder': 'type phonetics here',
        'rows': 5
    })
    )
    phonetic_standard = forms.ChoiceField(
        choices=[('', ''),
                 ('1', 'Unchecked'),
                 ('2', 'Double checked by author'),
                 ('3', 'Checked by team mate'),
                 ('4', 'Approved by whole team'),
                 ('5', 'Valid for linguistic analysis')],
        label='Phonetic accuracy',
        required=False
    )
    orthographic_text = forms.CharField(
        required=False,
        label='Orthographic transcription',
        widget = forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 5,
        'placeholder': 'type orthographic text here'
    })
    )
    valid_for_DA = forms.BooleanField(label='Valid for Discourse Analysis',
                                      required=False)
    discourse_type = forms.ChoiceField(
        choices=[('', ''),
                ('1', 'Narrative'),
                ('2', 'Hortatory'),
                ('3', 'Procedural'),
                ('4', 'Expository'),
                ('5', 'Descriptive')],
        label='Discourse type',
        required=False
    )
    
    def save(self, ce):
        if self.cleaned_data:
            new_text = CE.models.TextModel()
            new_text.ce = ce
            new_text.orthographic_text = self.cleaned_data['orthographic_text']
            new_text.phonetic_text = self.cleaned_data['phonetic_text']
            if self.cleaned_data['phonetic_text']:
                if self.cleaned_data['phonetic_standard'] == '':
                    new_text.phonetic_standard = 1
                else:
                    new_text.phonetic_standard = self.cleaned_data['phonetic_standard']
            if self.cleaned_data['valid_for_DA']:
                new_text.valid_for_DA = True
                new_text.discourse_type = self.cleaned_data['discourse_type']
            else:
                new_text.valid_for_DA = False
            new_text.audio = self.cleaned_data['audio']
            new_text.save()

text_form_set = forms.formset_factory(TextForm, extra=0)

def text_formset_prepopulated(ce):
    text_data = CE.models.TextModel.objects.filter(ce=ce)
    text_forms = []
    for data in text_data:
        text_form = text_form_set(initial=[{
            'audio': data.audio,
            'phonetic_text': data.phonetic_text,
            'orthographic_text': data.orthographic_text,
            'phonetic_standard': data.phonetic_standard,
            'valid_for_DA': data.valid_for_DA,
            'discourse_type': data.discourse_type
    }])
        text_forms.append(text_form)
    return text_forms

class QuestionForm(forms.Form):
    question = forms.CharField(
        required=True,
        label='Question about CE',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Write a question here',
        })
    )
    answer = forms.CharField(
        required=False,
        label='Answer',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'If you know the answer provide it here',
        })
    )

    def save(self, ce,request):
        if self.cleaned_data:
            new_question = CE.models.QuestionModel()
            new_question.ce = ce
            new_question.asked_by = str(request.user)
            new_question.last_modified_by = str(request.user)
            new_question.question = self.cleaned_data['question']
            new_question.answer = self.cleaned_data['answer']
            if self.cleaned_data['answer']:
                new_question.answered_by = str(request.user)
            new_question.save()

question_form_set = forms.formset_factory(QuestionForm, extra=0)


def question_formset_prepopulated(ce):
    question_data = CE.models.QuestionModel.objects.filter(ce=ce)
    question_forms = []
    for data in question_data:
        question_form = question_form_set(initial=[{
            'question': data.question,
            'answer': data.answer,

        }])
        question_forms.append(question_form)
    return question_forms


class ParticipationForm(forms.Form):
    date = forms.DateField(
        required=True,
        label='Date (Required)',
        widget=DateInput()
    )

    team_participants = forms.CharField(
        required=False,
        label='Team members present',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Who was there?',
        })
    )
    national_participants = forms.CharField(
        required=False,
        label='Nationals present',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Who else was there?',
        })
    )

    def save(self, ce, **kwargs):
        if 'instance' in kwargs:
            participants = CE.models.ParticipationModel.objects.filter(ce=kwargs['instance'])
        else:
            participants = CE.models.ParticipationModel()
        if self.cleaned_data:
            participants.ce = ce
            participants.team_participants = self.cleaned_data['team_participants']
            participants.national_participants = self.cleaned_data['national_participants']
            participants.date = self.cleaned_data['date']
            participants.save()

def prepopulated_participants_formset(ce):
    participant_data = CE.models.ParticipationModel.objects.filter(ce=ce)
    participant_forms = []
    for data in participant_data:
        participant_form = participant_formset(initial=[{
            'team_participants': data.team_participants,
            'national_participants': data.national_participants,
            'date': data.date
        }])
        participant_forms.append(participant_form)
    return participant_forms

participant_formset = forms.formset_factory(ParticipationForm, extra=1)
