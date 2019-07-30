from django import forms
from CE.models import CultureEvent


class CE_EditForm(forms.ModelForm):
    class Meta:
        model = CultureEvent
        fields = '__all__'
    # title = forms.CharField(
    #     queryset=CultureEvent.objects.filter(pk=1) ,
    #     max_length=60,
    #     widget=forms.TextInput(attrs={
    #         'class' : 'form-control',
    #         'placeholder' : 'CE title'}),
    #     label='CE title')