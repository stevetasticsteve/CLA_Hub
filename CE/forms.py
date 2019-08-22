from django import forms
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
# todo possible to get a form to pass validation by typing stuff in box, but result in it not creating an entry. Form passes validation, but db doesn't


text_form_set = forms.formset_factory(TextForm, extra=0)


class PictureUploadForm(forms.ModelForm):
    class Meta:
        model = CE.models.PictureModel
        fields = ('picture',)


class ParticipantForm(forms.Form):
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
    date = forms.DateField(
        required=True,
        label='Date (Required)',
        widget=DateInput()
    )


