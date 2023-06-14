from django import forms


class ProfileUploadForm(forms.Form):
    file = forms.FileField(
        required=True,
        label="file",
        widget=forms.ClearableFileInput(
            attrs={"class": "form-control", "accept": ".csv"}
        ),
    )
