import datetime
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string

import ssl
import certifi
import geopy
from geopy.distance import great_circle
from geopy.geocoders import GoogleV3

# Create your models here.

ctx = ssl.create_default_context(cafile=certifi.where())
geopy.geocoders.options.default_ssl_context = ctx
google_api_key = settings.GOOGLE_API_KEY
geocoder = GoogleV3(api_key=google_api_key)

def get_component(results, component_type, component_form):
    for component in results.raw['address_components']:
        if component_type in component['types']:
            return component[component_form]


def format_big_address_to_str(address_big):
    address_string = address_big
    return address_string


def place_id_default(param):
    return geocoder.geocode(param).place_id


def latitude_default(param):
    return geocoder.geocode(param).latitude


def longitude_default(param):
    return geocoder.geocode(param).longitude


def country_default(param):
    return get_component(geocoder.geocode(param), 'country', 'long_name')

def country_code_default(param):
    return get_component(geocoder.geocode(param), 'country', 'short_name')


def get_random_id():
    return get_random_string(5, 'ABCDEFGHJKMNPQRSTWXY23456789')


class HomeBase(models.Model):
    year = models.IntegerField(default=2020)
    address_big = models.TextField(null=True, max_length=500)
    address = models.CharField(null=True, blank=True, max_length=500)
    lat = models.FloatField(null=True, default=0)
    lon = models.FloatField(null=True, default=0)

    def mailing_address(self):
        return self.address_big.replace("\n", "<br>")

    class Meta:
        get_latest_by = ['year']


class Recipient(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    spouse_first_name = models.CharField(max_length=100, blank=True)
    spouse_last_name = models.CharField(max_length=100, blank=True)
    address_big = models.TextField(null=True, max_length=500)
    address = models.CharField(null=True, blank=True, max_length=500)
    lat = models.FloatField(null=True, default=0)
    lon = models.FloatField(null=True, default=0)

    def mailing_address(self):
        delivery_name = self.first_name + " " + self.last_name
        if self.spouse_first_name and self.spouse_last_name:
            delivery_name = delivery_name + " & " + self.spouse_first_name + " " + self.spouse_last_name
        elif self.spouse_first_name and not self.spouse_last_name:
            delivery_name = self.first_name + " & " + self.spouse_first_name + " " + self.last_name
        return delivery_name + "<br>" + self.address_big.replace("\n", "<br>")

    def latest_card(self):
        if self.card_set:
            return self.card_set.latest('date_sent').date_sent
        else:
            return


class Card(models.Model):
    card_id = models.CharField(max_length=10, default=get_random_id, verbose_name="Card ID")
    homebase = models.ForeignKey(HomeBase, on_delete=models.CASCADE, null=True)
    recipient = models.ForeignKey(Recipient, on_delete=models.CASCADE, null=True)
    date_sent = models.DateField(null=True, default=datetime.date.today)
    recipient_country = models.CharField(null=True, blank=True, max_length=100)
    recipient_country_code = models.CharField(null=True, blank=True, max_length=2)
    date_received = models.DateField(null=True, blank=True)

    def travel_time(self):
        if self.date_received is not None:
            d = self.date_received - self.date_sent
            return d.days
        else:
            return None

    def distance(self):
        homebase_lat_lon = (self.homebase.lat, self.homebase.lon)
        recipient_lat_lon = (self.recipient.lat, self.recipient.lon)
        return great_circle(homebase_lat_lon, recipient_lat_lon).km

    def travel_speed(self):
        if self.travel_time() is not None and self.travel_time() != 0:
            return self.distance() / (self.travel_time() * 24)
        elif self.travel_time() is not None and self.travel_time() == 0:
            return self.distance() / 24
        else:
            return None


@receiver(pre_save, sender=HomeBase)
@receiver(pre_save, sender=Recipient)
def convert_address(sender, instance, **kwargs):
    if not instance.address:
        instance.address = instance.address_big.replace("\n",", ")


@receiver(pre_save, sender=HomeBase)
@receiver(pre_save, sender=Recipient)
def geocode(sender, instance, **kwargs):
    if instance.lat == 0 or instance.lon == 0:
        instance.lat = latitude_default(instance.address)
        instance.lon = longitude_default(instance.address)


@receiver(pre_save, sender=Card)
def get_country(sender, instance, **kwargs):
    if not instance.recipient_country:
        instance.recipient_country = country_default(instance.recipient.address)
    if not instance.recipient_country_code:
        instance.recipient_country_code = country_code_default(instance.recipient.address)
