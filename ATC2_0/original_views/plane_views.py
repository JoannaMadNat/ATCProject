from django.shortcuts import render, redirect

from ATC.views.validation import get_size
from ..models import Plane, Airline


def planes_index(request):
    return render(request, 'planes/index.html', {
        'planes': Plane.objects.all().order_by("identifier")
    })


def planes_create(request):
    if request.method == "POST":
        identifier = request.POST.get("identifier")
        if Plane.objects.filter(identifier=identifier).count() != 0:
            return render(request, 'landing/bad-input.html', status=420)

        plane = Plane()
        plane.identifier = identifier
        plane.size = get_size(request.POST.get("size"))
        plane.airline = Airline.objects.get(id=request.POST.get("airline"))

        n = request.POST.get("Current Passenger Count")
        if n:
            plane.currentPassengerCount = n
        n = request.POST.get("Max Passenger Count")
        if n:
            plane.maxPassengerCount = n
        plane.save()

        return redirect(planes_index)
    return render(request, 'planes/create.html', {'airlines': Airline.objects.all().order_by("name")})


def planes_update(request, plane_id):
    if request.method == "POST":
        if Plane.objects.filter(pk=plane_id).count() != 1:
            return render(request, 'landing/not-found.html', status=404)

        identifier = request.POST.get("identifier")
        if Plane.objects.filter(identifier=identifier).count() != 0:
            return render(request, 'landing/bad-input.html', status=420)

        plane = Plane.objects.get(pk=plane_id)
        plane.identifier = identifier
        plane.size = get_size(request.POST.get("size"))
        plane.airline = Airline.objects.get(id=request.POST.get("airline"))

        n = request.POST.get("Current Passenger Count")
        if n:
            plane.currentPassengerCount = n
        n = request.POST.get("Max Passenger Count")
        if n:
            plane.maxPassengerCount = n
        plane.save()
        return redirect(planes_index)

    return render(request, 'planes/update.html', {
        'plane': Plane.objects.get(pk=plane_id), 'airlines': Airline.objects.all().order_by("name")
    })


def planes_delete(request, plane_id):
    if Plane.objects.filter(pk=plane_id).count() != 1:
        return render(request, 'landing/not-found.html', status=404)

    Plane.objects.get(pk=plane_id).delete()
    return redirect(planes_index)
