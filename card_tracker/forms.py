from django import forms


class CardForm(forms.Form):
    card_id_form = forms.CharField(label='Card ID Code', max_length=5, widget=forms.TextInput(attrs={'class': "form-control form-control-lg"}))
