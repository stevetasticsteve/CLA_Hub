from django import forms


class CE_EditForm(forms.Form):
    title = forms.CharField(max_length=60,
                            widget=forms.TextInput(attrs={
                                'class' : 'form-control',
                                'placeholder' : 'CE title'
                            }))