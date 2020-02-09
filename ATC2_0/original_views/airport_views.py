from django.shortcuts import render, redirect

from ATC.views.validation import set_coords, validate_name
from ..models import Airport, Airline, Runway, Gate


def airports_index(request):
    return render(request, 'airports/index.html', {
        'airports': Airport.objects.all().order_by("name"),
        'runways': Runway.objects.all().order_by("identifier"),
        'gates': Gate.objects.all().order_by("identifier"),
        'airlines': Airline.objects.all().order_by("name"),
    })


def airports_create(request):
    if request.method == "POST":
        name = request.POST.get("name")
        if Airport.objects.filter(name=name).count() != 0:
            return render(request, 'landing/bad-input.html', status=420)

        airport = Airport()
        airport.name = name
        set_coords(airport, request)

        return redirect(airports_index)
    return render(request, 'airports/create.html', {})


def airports_update(request, airport_id):
    if Airport.objects.filter(pk=airport_id).count() != 1:
        return render(request, 'landing/not-found.html', status=404)

    if request.method == "POST":
        name = request.POST.get("name")
        if not validate_name(name, Airport, airport_id):
            return render(request, 'landing/bad-input.html', status=420)

        airport = Airport.objects.get(pk=airport_id)
        airport.name = name
        set_coords(airport, request)
        airport.save()

        return redirect(airports_index)
    return render(request, 'airports/update.html', {
        'airport': Airport.objects.get(pk=airport_id)
    })


def airports_delete(request, airport_id):
    if Airport.objects.filter(pk=airport_id).count() != 1:
        return render(request, 'landing/not-found.html', status=404)

    Airport.objects.get(pk=airport_id).delete()
    return redirect(airports_index)
