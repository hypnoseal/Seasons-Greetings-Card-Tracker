from django.contrib import admin
from django.utils.html import format_html
from django.forms import ModelForm, ModelChoiceField

# Register your models here.


from .models import HomeBase, Recipient, Card


class HomeBaseAdmin(admin.ModelAdmin):
    list_display = ('year', 'mailing_address')

    def mailing_address(self, obj):
        return format_html(obj.mailing_address())


class RecipientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'mailing_address', 'latest_card')
    search_fields = ['first_name', 'last_name']

    def mailing_address(self, obj):
        return format_html(obj.mailing_address())


class CardRecipientListField(ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s %s" % (obj.first_name, obj.last_name)


class CardHomeBaseListField(ModelChoiceField):
    def label_from_instance(self, obj):
        return "%s" % obj.address


def get_latest_homebase():
    try:
        latest_homebase = [HomeBase.objects.latest()]
    except (KeyError, HomeBase.DoesNotExist):
        latest_homebase = []
    return latest_homebase


class CardAdminForm(ModelForm):
    try:
        recipient = CardRecipientListField(queryset=Recipient.objects.all())
    except (KeyError, Recipient.DoesNotExist):
        recipient = []
    try:
        homebase = CardHomeBaseListField(queryset=HomeBase.objects.all(), initial=get_latest_homebase)
    except (KeyError, HomeBase.DoesNotExist):
        homebase = []

    class Meta:
        model = Card
        fields = ['card_id', 'homebase', 'recipient', 'recipient_country', 'recipient_country_code', 'date_sent', 'date_received']


class CardAdmin(admin.ModelAdmin):
    list_display = ('card_id', 'date_sent', 'get_recipient')
    form = CardAdminForm

    def get_recipient(self, obj):
        return obj.recipient.first_name + ' ' + obj.recipient.last_name

    get_recipient.short_description = 'Recipient'


admin.site.register(HomeBase, HomeBaseAdmin)
admin.site.register(Recipient, RecipientAdmin)
admin.site.register(Card, CardAdmin)

