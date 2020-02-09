from django.shortcuts import render, redirect

from ATC.views.validation import validate_identifier, get_size
from ..models import Gate, Plane, Airport


def gates_index(request):
    return render(request, 'gates/index.html', {
        'gates': Gate.objects.all().order_by("identifier"),
        'planes': Plane.objects.all().order_by("identifier"),
    })


def gates_create(request):
    if request.method == "POST":
        identifier = request.POST.get("identifier")
        if Gate.objects.filter(identifier=identifier).count() != 0:
            return render(request, 'landing/bad-input.html', status=420)

        gate = Gate()
        gate.identifier = identifier
        gate.size = get_size(request.POST.get("size"))  # no need to validate because select statement
        gate.airport = Airport.objects.get(pk=request.POST.get("airport"))
        gate.save()

        return redirect(gates_index)
    return render(request, 'gates/create.html', {'airports': Airport.objects.all().order_by("name")})


def gates_update(request, gate_id):
    if Gate.objects.filter(pk=gate_id).count() != 1:
        return render(request, 'landing/not-found.html', status=404)

    if request.method == "POST":
        identifier = request.POST.get("identifier")
        if not validate_identifier(identifier, Gate, gate_id):
            return render(request, 'landing/bad-input.html', status=420)

        gate = Gate.objects.get(pk=gate_id)
        gate.identifier = identifier
        gate.size = get_size(request.POST.get("size"))
        gate.airport = Airport.objects.get(pk=request.POST.get("airport"))
        gate.save()

        return redirect(gates_index)
    return render(request, 'gates/update.html', {
        'gate': Gate.objects.get(pk=gate_id), 'airports': Airport.objects.all().order_by("name")
    })


def gates_delete(request, gate_id):
    if Gate.objects.filter(pk=gate_id).count() != 1:
        return render(request, 'landing/not-found.html', status=404)

    Gate.objects.get(pk=gate_id).delete()
    return redirect(gates_index)
