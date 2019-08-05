from django import forms
import CE.models

class DateInput(forms.DateInput):
    input_type = 'date'

class CE_EditForm(forms.ModelForm):
    class Meta:
        model = CE.models.CultureEvent
        fields = '__all__'
        exclude = ('last_modified_by',)


class Text_EditForm(forms.ModelForm):
    class Meta:
        model = CE.models.Texts
        fields = '__all__'
        exclude = ('primary',)

class PictureUploadForm(forms.ModelForm):
    class Meta:
        model = CE.models.PictureModel
        fields = ('picture',)

        #todo write tests for picture upload

        #todo work out how to include n number of Text_EditForms along with the CE_EditForm to the edit_CE template
        #todo placeholder text

class ParticipantForm(forms.ModelForm):
    class Meta:
        model = CE.models.ParticipationModel
        fields = '__all__'
        exclude = ('ce',)
        widgets = {
            'date': DateInput(),
        }


