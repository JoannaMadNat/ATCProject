import json
from datetime import timedelta
from math import sqrt
from django.utils.datetime_safe import datetime
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
import requests
from django.shortcuts import render
from ATC2_0.models import Plane, Airport, Runway, Gate
from ATC2_0.views.utils import get_intersect_data

errors_cache = []

error_messages = {"collision": "COLLISION_IMMINENT",
                  "airport": "WRONG_AIRPORT",
                  "runway": "DUPLICATE_RUNWAY",
                  "gate": "DUPLICATE_GATE"}


class Point:
    x = float
    y = float

    def __init__(self, x, y):
        self.x = x
        self.y = y


def update_errors(data):
    global errors_cache
    if len(errors_cache) > 10:
        errors_cache.clear()
    errors_cache.append(data)


def post_response_headers(obj_id, error_type):
    response = {'team_id': 'nSLIoq2eIYMNExLYNALS',  # given when app is registered to evently
                'obj_type': 'PLANE',
                'id': obj_id,
                'error': error_type
                }

    print(obj_id, error_type)
    update_errors(response)
    requests.post(url='https://evently.bjucps.dev/app/error_report', json=response)


def crash(plane, other_plane):
    post_response_headers(plane.identifier, error_messages['collision'])
    post_response_headers(other_plane.identifier, error_messages['collision'])


def compare_times(time1, time2):
    if time1.year == time2.year and \
            time1.month == time2.month and \
            time1.day == time2.day and \
            time1.hour == time2.hour and \
            time1.minute == time2.minute:
        return True
    return False


def check_collision_scenario_0(plane, other_plane):
    if plane.landing_airport == other_plane.landing_airport \
            and compare_times(plane.landing_time, other_plane.landing_time):
        return True
    return False


def check_collision_scenario_1(plane, other_plane):
    if other_plane.landing_airport == plane.takeoff_airport and \
            other_plane.takeoff_airport == plane.landing_airport and \
            plane.speed != 0 and other_plane.speed != 0:
        return True
    return False


def check_collision_scenario_2(plane, other_plane):
    if other_plane.landing_airport == plane.landing_airport and \
            other_plane.takeoff_airport == plane.takeoff_airport and \
            plane.speed > other_plane.speed and \
            (plane.landing_time < other_plane.landing_time or
             compare_times(plane.landing_time, other_plane.landing_time)):
        return True
    return False


def check_collision_scenario_3(plane, other_plane):
    intersect = get_intersect_data(plane, other_plane)
    if intersect:
        distance = sqrt(pow(intersect.x - plane.takeoff_airport.x, 2) + pow(intersect.y - plane.takeoff_airport.y, 2))
        plane_intersect_time = plane.takeoff_time + timedelta(hours=(distance / plane.speed))

        distance = sqrt(
            pow(intersect.x - other_plane.takeoff_airport.x, 2) + pow(intersect.y - other_plane.takeoff_airport.y, 2))
        other_intersect_time = other_plane.takeoff_time + timedelta(hours=(distance / other_plane.speed))

        if compare_times(plane_intersect_time, other_intersect_time):
            return True
    return False


def check_collisions(plane):
    planes = Plane.objects.filter(current_state="In Air")
    status = True
    for other_plane in planes:
        if other_plane == plane:
            continue
        elif check_collision_scenario_0(plane, other_plane) or \
                check_collision_scenario_1(plane, other_plane) or \
                check_collision_scenario_2(plane, other_plane) or \
                check_collision_scenario_3(plane, other_plane):
            crash(plane, other_plane)
            status = False
    return status


def check_airport(plane, flight):
    for serviced in plane.airline.airport_set.all():
        if flight['destination'] == serviced.name:
            return True
    post_response_headers(flight['plane'], error_messages['airport'])
    return False


def update_plane(flight):
    plane = Plane.objects.get(identifier=flight['plane'])
    plane.speed = float(flight['speed'])
    plane.landing_airport = Airport.objects.get(name=flight['destination'])
    plane.takeoff_airport = Airport.objects.get(name=flight['origin'])
    plane.takeoff_time = datetime.strptime(flight['takeoff_time'], '%Y-%m-%d %H:%M')
    plane.landing_time = datetime.strptime(flight['landing_time'], '%Y-%m-%d %H:%M')
    plane.current_state = "In Air"
    plane.runway = None
    plane.gate = None
    plane.save()


@method_decorator(csrf_exempt)
def get_rest_headers(request):  # get API jason packages
    status = 200

    if request.method == "POST":
        flight_data = json.loads(request.body)
        update_plane(flight_data)
        plane = Plane.objects.get(identifier=flight_data['plane'])

        if not check_airport(plane, flight_data) or not check_collisions(plane):
            status = 240

    return render(request, 'REST/index.html', {'errors': errors_cache}, status=status)


@method_decorator(csrf_exempt)
def get_rest_runway(request):
    status = 200

    if request.method == "POST":
        data = json.loads(request.body)
        plane = Plane.objects.get(identifier=data['plane'])
        if 'arrive_at_time' in data:
            plane.current_state = "Needs Runway"
            plane.runway = Runway.objects.get(identifier=data['runway'])
            plane.arrival_time = datetime.strptime(data['arrive_at_time'], '%Y-%m-%d %H:%M')
            plane.save()

            planes = Plane.objects.filter(runway=plane.runway, arrival_time=plane.arrival_time)
            if planes.count() > 1:
                status = 240
                for p in planes:
                    post_response_headers(p.identifier, error_messages['runway'])
        else:
            plane.gate = None  # free gate
            plane.current_state = "Taxi"
            plane.takeoff_airport = None
            plane.takeoff_time = None
            plane.landing_time = None
            plane.save()

    return render(request, 'REST/index.html', {'errors': errors_cache}, status=status)


@method_decorator(csrf_exempt)
def get_rest_gate(request):
    status = 200

    if request.method == "POST":
        data = json.loads(request.body)
        plane = Plane.objects.get(identifier=data['plane'])
        if 'arrive_at_time' in data:
            plane.current_state = "Docking"
            plane.gate = Gate.objects.get(identifier=data['gate'])
            plane.arrival_time = datetime.strptime(data['arrive_at_time'], '%Y-%m-%d %H:%M')
            plane.save()

            planes = Plane.objects.filter(gate=plane.gate, arrival_time=plane.arrival_time)
            if planes.count() > 1:
                status = 240
                for p in planes:
                    post_response_headers(p.identifier, error_messages['gate'])
        else:
            plane.current_state = "Arrived"
            plane.runway = None  # free runway
            plane.arrival_time = None
            plane.save()

    return render(request, 'REST/index.html', {'errors': errors_cache}, status=status)
