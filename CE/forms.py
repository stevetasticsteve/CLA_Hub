from django import forms
from CE.models import CultureEvent, Texts


class CE_EditForm(forms.ModelForm):
    class Meta:
        model = CultureEvent
        fields = '__all__'


class Text_EditForm(forms.ModelForm):
    class Meta:
        model = Texts
        fields = '__all__'
        exclude = ('primary',)

        #todo work out how to include n number of Text_EditForms along with the CE_EditForm to the edit_CE template
        #todo placeholder text