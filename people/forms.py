from django import forms

import people.models


class DateInput(forms.DateInput):
    input_type = 'date'


class PeopleForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # init method injects 'form-control' in to enable bootstrap styling
        super(PeopleForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

    class Meta:
        model = people.models.Person
        exclude = ('DELETE', 'last_modified_by', 'thumbnail', 'family', 'medical')
        widgets = {
            'born': DateInput(),
            'death': DateInput(),
            'team_contact': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write whatever notes you like here'
            }),
            'family_plain_text': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Field is html enabled'
            })
        }
        labels = {
            'team_contact': 'Notes',
            'family_plain_text': 'Family'
        }

    def save(self, **kwargs):
        self.instance.last_modified_by = str(kwargs['request'].user)
        if kwargs.get('request').POST.get('picture-clear'):
            self.instance.clear_picture()
        return super(PeopleForm, self).save()


class SoapForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # init method injects 'form-control' in to enable bootstrap styling
        super(SoapForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

    class Meta:
        model = people.models.MedicalAssessment
        exclude = ['person']
        widgets = {
            'short': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Required.',
                'label': 'Short as possible description',
            }),
            'subjective': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write what the patient says here.',
                'rows': 5
            }),
            'objective': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write vitals and stats here.',
                'rows': 5
            }),
            'assessment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write your conclusions here.',
                'rows': 5
            }),
            'plan': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Write the plan of action here.',
                'rows': 5
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Any additional comments can go here.',
                'rows': 5
            }),
        }

    def save(self, **kwargs):
        self.instance.person = kwargs['person']
        super(SoapForm, self).save()


class MedicalNotesForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # init method injects 'form-control' in to enable bootstrap styling
        super(MedicalNotesForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({
                'class': 'form-control'
            })

    class Meta:
        model = people.models.Person
        fields = ['medical']
