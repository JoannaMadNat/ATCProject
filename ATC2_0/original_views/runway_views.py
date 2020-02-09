from django.shortcuts import render, redirect

from ATC.views.validation import validate_identifier, get_size
from ..models import Runway, Plane, Airport


def runways_index(request):
    return render(request, 'runways/index.html', {
        'runways': Runway.objects.all().order_by("identifier"),
        'planes': Plane.objects.all().order_by("identifier"),
    })


def runways_create(request):
    if request.method == "POST":
        identifier = request.POST.get("identifier")
        if Runway.objects.filter(identifier=identifier).count() != 0:
            return render(request, 'landing/bad-input.html', status=420)

        runway = Runway()
        runway.identifier = identifier
        runway.size = get_size(request.POST.get("size"))  # no need to validate because select statement
        runway.airport = Airport.objects.get(pk=request.POST.get("airport"))
        runway.save()

        return redirect(runways_index)
    return render(request, 'runways/create.html', {'airports': Airport.objects.all().order_by("name")})


def runways_update(request, runway_id):
    if Runway.objects.filter(pk=runway_id).count() != 1:
        return render(request, 'landing/not-found.html', status=404)

    if request.method == "POST":
        identifier = request.POST.get("identifier")
        if not validate_identifier(identifier, Runway, runway_id):
            return render(request, 'landing/bad-input.html', status=420)

        runway = Runway.objects.get(pk=runway_id)
        runway.identifier = identifier
        runway.size = get_size(request.POST.get("size"))
        runway.airport = Airport.objects.get(pk=request.POST.get("airport"))
        runway.save()

        return redirect(runways_index)
    return render(request, 'runways/update.html', {
        'runway': Runway.objects.get(pk=runway_id), 'airports': Airport.objects.all().order_by("name")
    })


def runways_delete(request, runway_id):

    if Runway.objects.filter(pk=runway_id).count() != 1:
        return render(request, 'landing/not-found.html', status=404)

    Runway.objects.get(pk=runway_id).delete()
    return redirect(runways_index)
