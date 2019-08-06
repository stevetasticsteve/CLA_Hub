from django import forms
import CE.models


class DateInput(forms.DateInput):
    input_type = 'date'

class CE_EditForm(forms.ModelForm):
    class Meta:
        model = CE.models.CultureEvent
        fields = '__all__'
        exclude = ('last_modified_by', 'slug')


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



class PictureUploadForm(forms.ModelForm):
    class Meta:
        model = CE.models.PictureModel
        fields = ('picture',)

        #todo work out how to include n number of Text_EditForms along with the CE_EditForm to the edit_CE template

class ParticipantForm(forms.ModelForm):
    class Meta:
        model = CE.models.ParticipationModel
        fields = '__all__'
        exclude = ('ce',)
        widgets = {
            'date': DateInput(),
        }


