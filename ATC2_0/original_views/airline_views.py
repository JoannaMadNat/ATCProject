from django.shortcuts import render, redirect

from ATC.views.validation import set_coords, validate_name
from ..models import Airline, Airport


# By Hudson VVV

def airlines_index(request):
    return render(request, 'airlines/index.html', {
        'airlines': Airline.objects.all().order_by("name")
    })


def airlines_create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        if Airline.objects.filter(name=name).count() != 0:
            return render(request, 'landing/bad-input.html', status=420)

        airline = Airline()
        airline.name = name
        airline.save()

        airline.airport_set.clear()
        airports = request.POST.getlist('airports')
        for airport in airports:
            airline.airport_set.add(airport)

        return redirect(airlines_index)
    return render(request, 'airlines/create.html', {'airports': Airport.objects.all().order_by("name"), })


def airlines_update(request, airline_id):
    if Airline.objects.filter(pk=airline_id).count() != 1:
        return render(request, 'landing/not-found.html', status=404)

    if request.method == "POST":
        name = request.POST.get("name")
        if not validate_name(name, Airline, airline_id):
            return render(request, 'landing/bad-input.html', status=420)

        airline = Airline.objects.get(pk=airline_id)
        airline.name = name

        airline.airport_set.clear()
        airports = request.POST.getlist('airports')
        for airport in airports:
            airline.airport_set.add(airport)

        return redirect(airlines_index)
    return render(request, 'airlines/update.html', {
        'airline': Airline.objects.get(pk=airline_id)
    })


def airlines_delete(request, airline_id):
    if Airline.objects.filter(pk=airline_id).count() != 1:
        return render(request, 'landing/not-found.html', status=404)

    Airline.objects.get(pk=airline_id).delete()
    return redirect(airlines_index)
