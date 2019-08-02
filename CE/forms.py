from django import forms
from CE.models import CultureEvent, Texts, PictureModel


class CE_EditForm(forms.ModelForm):
    class Meta:
        model = CultureEvent
        fields = '__all__'
        exclude = ('last_modified_by',)


class Text_EditForm(forms.ModelForm):
    class Meta:
        model = Texts
        fields = '__all__'
        exclude = ('primary',)

class PictureUploadForm(forms.ModelForm):
    class Meta:
        model = PictureModel
        fields = ('picture',)

        #todo work out how to include n number of Text_EditForms along with the CE_EditForm to the edit_CE template
        #todo placeholder text