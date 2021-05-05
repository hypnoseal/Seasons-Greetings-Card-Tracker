from django.conf import settings
from django.http import HttpResponse
from django.template import loader
import datetime
import numpy

from .models import Card, HomeBase
from .forms import CardForm


def get_cards(request):
    card_list = Card.objects.all()
    card_distance_array = []
    card_speed_array = []
    card_travel_time_array = []
    card_countries_array = []
    number_of_countries = 0
    furthest_travelled = 0
    total_distance = 0
    average_distance = 0
    average_speed = 0
    top_speed = 0
    average_travel_time = 0
    cards_received = len(card_travel_time_array)

    def calculate_card_stats(card_array):
        nonlocal card_distance_array
        nonlocal card_speed_array
        nonlocal card_travel_time_array
        nonlocal card_countries_array
        nonlocal number_of_countries
        nonlocal furthest_travelled
        nonlocal total_distance
        nonlocal average_distance
        nonlocal average_speed
        nonlocal top_speed
        nonlocal average_travel_time
        nonlocal cards_received

        card_distance_array = []
        card_speed_array = []
        card_travel_time_array = []
        card_countries_array = []

        for c in card_array:
            card_distance_array.append(c.distance())
            if c.travel_time():
                card_travel_time_array.append(c.travel_time())
            if c.travel_speed():
                card_speed_array.append(c.travel_speed())
            if c.recipient_country and [c.recipient_country, c.recipient_country_code] not in card_countries_array:
                card_countries_array.append([c.recipient_country, c.recipient_country_code])
        if card_distance_array:
            furthest_travelled = numpy.max(card_distance_array).round().astype(int)
            total_distance = numpy.sum(card_distance_array).round().astype(int)
            average_distance = numpy.mean(card_distance_array).round().astype(int)
        if card_speed_array:
            average_speed = numpy.mean(card_speed_array).round().astype(int)
            top_speed = numpy.max(card_speed_array).round().astype(int)
        if card_travel_time_array:
            average_travel_time = numpy.mean(card_travel_time_array).round().astype(int)
        cards_received = len(card_travel_time_array)
        number_of_countries = len(card_countries_array)

    calculate_card_stats(card_list)
    form = CardForm(request.POST)
    context = {
        'card_count': card_list.count,
        'furthest_travelled': furthest_travelled,
        'total_distance': total_distance,
        'average_distance': average_distance,
        'cards_received': cards_received,
        'average_speed': average_speed,
        'top_speed': top_speed,
        'average_travel_time': average_travel_time,
        'countries': sorted(card_countries_array),
        'countries_count': number_of_countries,
        'google_api_key': settings.GOOGLE_API_KEY,
        'form': form
    }
    if not card_list:
        context['error_message'] = "Uh oh! There are no cards in the database!"
        context['card_count'] = "No"

    return card_list, context


def check_and_update_cards(card_list, card_id, context, request):
    try:
        selected_card = card_list.get(card_id=card_id)
    except (KeyError, Card.DoesNotExist):
        error_message = "I'm sorry I cannot find that card. Please try again."
        context['error_message'] = error_message
        template = loader.get_template('card_tracker/index.html')
        return context, template
    else:
        if selected_card.date_received is None:
            selected_card.date_received = datetime.date.today()
            selected_card.save()
            run_cards = get_cards(request)
            context = run_cards[1]
        context['selected_card_distance'] = numpy.round(selected_card.distance()).astype(int)
        context['selected_card_travel_speed'] = numpy.round(selected_card.travel_speed()).astype(int)
        context['selected_card_travel_time'] = numpy.round(selected_card.travel_time()).astype(int)
        try:
            context['homebase_address'] = selected_card.homebase.address
        except (KeyError, HomeBase.DoesNotExist):
            error_message = "I'm sorry I cannot find that card. Please try again."
            context['error_message'] = error_message
            template = loader.get_template('card_tracker/index.html')
            return context, template
        context['recipient_address'] = selected_card.recipient.address
        context['site_url'] = settings.SITE_URL
        context['card_id'] = card_id
        template = loader.get_template('card_tracker/results.html')
        return context, template


def index(request):
    run_cards = get_cards(request)
    card_list = run_cards[0]
    context = run_cards[1]
    if request.method == 'POST':
        card_check = check_and_update_cards(card_list, request.POST['card_id_form'], context, request)
        context = card_check[0]
        template = card_check[1]
    else:
        if card_list and not context['cards_received']:
            context['warning_message'] = "Oh my! It looks like you're the first person to receive a card. Please enter " \
                                         "your card's five digit ID code to start showing statistics!"
            context['cards_received'] = "No"
        template = loader.get_template('card_tracker/index.html')
    return HttpResponse(template.render(context, request))


def search(request, card_id):
    request.POST = request.POST.copy()
    request.POST['card_id_form'] = card_id
    run_cards = get_cards(request)
    card_list = run_cards[0]
    context = run_cards[1]
    card_check = check_and_update_cards(card_list, card_id, context, request)
    context = card_check[0]
    context['card_id'] = card_id
    template = card_check[1]
    return HttpResponse(template.render(context, request))
