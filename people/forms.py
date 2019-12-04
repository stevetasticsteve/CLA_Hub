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
        exclude = ('DELETE', 'last_modified_by', 'thumbnail')
        widgets = {
            'born': DateInput()
        }

    def save(self, **kwargs):
        self.instance.last_modified_by = str(kwargs['request'].user)
        return super(PeopleForm, self).save()
