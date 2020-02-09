import pytz
import requests
from ATC2_0.models import Airport, Gate, Runway, Plane
from kafka import KafkaProducer
from django.core.management.base import BaseCommand
from uuid import uuid4
from django.db.models import Q
from datetime import timedelta
from dateutil import parser
from ATC2_0.helpers import check_size, arrive_at_intersection_at_same_minute, check_time_delta
import json
from kafka import KafkaConsumer

GROUP_ID = 'VAtIN335WwpL85TLSgxt'  # nSLIoq2eIYMNExLYNALS
KAFKA_SERVER = 'ec2-18-206-71-156.compute-1.amazonaws.com:9092'
producer = KafkaProducer(bootstrap_servers=[KAFKA_SERVER], api_version=(0, 10))


def send_warning(object: dict):
    print(object['error'])
    requests.post(url='https://evently.bjucps.dev/app/error_report', json=object)

    producer = KafkaProducer(bootstrap_servers=[KAFKA_SERVER], api_version=(0, 10))
    key_bytes = bytes(str(uuid4()), encoding='utf-8')
    value_bytes = bytes(json.dumps(object), encoding='utf-8')
    producer.send("warnings", key=key_bytes, value=value_bytes)
    producer.flush()


def create_consumer(cons_type):
    return KafkaConsumer(cons_type,  # the channel on which to listen, you specify this in evently
                         auto_offset_reset='earliest',  # start processing at the beginning of time
                         bootstrap_servers=[KAFKA_SERVER],  # sorry this isn't a nice url :(
                         group_id=GROUP_ID,  # your group id in kafka, can be any random string
                         enable_auto_commit=True,
                         # remember where we last stopped, change to False to process all the messages every time (good for testing, not for prod)
                         consumer_timeout_ms=5000)  # how long to wait for a new message before we sleep for a bit


def handle_passenger_count(body):
    plane = Plane.objects.filter(identifier=body["plane"]).first()
    if plane.maxPassengerCount < int(body["passenger_count"]):
        send_warning({
            "team_id": GROUP_ID,
            "error": "TOO_MANY_PASSENGERS",
            "obj_type": "PLANE",
            "id": plane.identifier
        })


def handle_gate_publish(body):
    plane = Plane.objects.filter(identifier=body["plane"]).first()
    gate = Gate.objects.filter(identifier=body["gate"]).first()
    plane.gate = gate
    if "arrive_at_time" in body:
        if not check_size(plane.size, gate.size):
            send_warning({
                "team_id": GROUP_ID,
                "error": "TOO_SMALL_GATE",
                "obj_type": "PLANE",
                "id": plane.identifier
            })
        date = parser.parse(body["arrive_at_time"])
        plane.arrive_at_gate_time = date
        plane.save()
        if gate.plane_set.filter(Q(arrive_at_gate_time=date) | Q(arrive_at_runway_time=None)).count() > 1:
            for plane in gate.plane_set.filter(Q(arrive_at_gate_time=date) | Q(arrive_at_runway_time=None)).all():
                send_warning({
                    "team_id": GROUP_ID,
                    "error": "DUPLICATE_GATE",
                    "obj_type": "PLANE",
                    "id": plane.identifier
                })
    else:
        plane.arrive_at_gate_time = None
        plane.runway = None
    plane.save()


def handle_runway_publish(body):
    plane = Plane.objects.filter(identifier=body["plane"]).first()
    runway = Runway.objects.filter(identifier=body["runway"]).first()
    plane.runway = runway
    if "arrive_at_time" in body:
        if not check_size(plane.size, runway.size):
            send_warning({
                "team_id": GROUP_ID,
                "error": "TOO_SMALL_RUNWAY",
                "obj_type": "PLANE",
                "id": plane.identifier
            })
        date = parser.parse(body["arrive_at_time"])
        plane.arrive_at_runway_time = date
        plane.save()
        yup_collide = False
        if runway.plane_set.count() > 1:
            for other_plane in runway.plane_set.all():
                if plane != other_plane and check_time_delta(plane.arrive_at_runway_time,
                                                             other_plane.arrive_at_runway_time, timedelta(minutes=1)):
                    yup_collide = True
                    print("HERE")
                    send_warning({
                        "team_id": GROUP_ID,
                        "error": "DUPLICATE_RUNWAY",
                        "obj_type": "PLANE",
                        "id": other_plane.identifier
                    })
        if yup_collide:
            print("HERE")
            send_warning({
                "team_id": GROUP_ID,
                "error": "DUPLICATE_RUNWAY",
                "obj_type": "PLANE",
                "id": plane.identifier
            })
    else:
        plane.arrive_at_runway_time = None
        plane.gate = None
        plane.heading = 0
        plane.speed = 0
        plane.take_off_airport = plane.land_airport
        plane.land_airport = None
        plane.take_off_time = None
        plane.landing_time = None
    plane.save()


def handle_heading_publish(body):
    plane = Plane.objects.filter(identifier=body["plane"]).first()
    direction = float(body["direction"])
    speed = float(body["speed"])
    origin = Airport.objects.filter(name=body["origin"]).first()
    destination = Airport.objects.filter(name=body["destination"]).first()
    take_off_time = parser.parse(body["take_off_time"])
    landing_time = parser.parse(body["landing_time"])

    plane.take_off_airport = origin
    plane.land_airport = destination
    plane.take_off_time = take_off_time
    plane.landing_time = landing_time
    plane.heading = direction
    plane.speed = speed
    plane.runway = None
    plane.save()

    if plane.airline not in plane.land_airport.airlines.all():
        send_warning({
            "team_id": GROUP_ID,
            "error": "WRONG_AIRPORT",
            "obj_type": "PLANE",
            "id": plane.identifier
        })

    warned_for_current_plane = False
    set1 = Plane.objects.exclude(landing_time=None).filter(take_off_airport=plane.land_airport,
                                                           land_airport=plane.take_off_airport)
    if set1.count() > 0:
        if not warned_for_current_plane:
            warned_for_current_plane = True
            send_warning({
                "team_id": GROUP_ID,
                "error": "COLLISION_IMMINENT",
                "obj_type": "PLANE",
                "id": plane.identifier
            })
        for collidy_plane in set1.all():
            send_warning({
                "team_id": GROUP_ID,
                "error": "COLLISION_IMMINENT",
                "obj_type": "PLANE",
                "id": collidy_plane.identifier
            })

    set2 = Plane.objects.exclude(landing_time=None).filter(take_off_airport=plane.take_off_airport,
                                                           land_airport=plane.land_airport,
                                                           landing_time__gt=plane.landing_time)
    if set2.count() > 0:
        if not warned_for_current_plane:
            warned_for_current_plane = True
            send_warning({
                "team_id": GROUP_ID,
                "error": "COLLISION_IMMINENT",
                "obj_type": "PLANE",
                "id": plane.identifier
            })
        for collidy_plane in set2.all():
            send_warning({
                "team_id": GROUP_ID,
                "error": "COLLISION_IMMINENT",
                "obj_type": "PLANE",
                "id": collidy_plane.identifier
            })

    # now check for intersecting planes
    set3 = Plane.objects.exclude(Q(take_off_airport=plane.take_off_airport, land_airport=plane.land_airport) | Q(
        take_off_airport=plane.land_airport, land_airport=plane.take_off_airport)).exclude(landing_time=None)
    if set3.count() > 0:
        for collidy_plane in set3.all():
            if arrive_at_intersection_at_same_minute(plane, collidy_plane):
                if not warned_for_current_plane:
                    warned_for_current_plane = True
                    send_warning({
                        "team_id": GROUP_ID,
                        "error": "COLLISION_IMMINENT",
                        "obj_type": "PLANE",
                        "id": plane.identifier
                    })
                send_warning({
                    "team_id": GROUP_ID,
                    "error": "COLLISION_IMMINENT",
                    "obj_type": "PLANE",
                    "id": collidy_plane.identifier
                })


class Command(BaseCommand):
    help = 'processes entries in the kafka queue'

    def handle(self, *args, **options):
        # do processing stuffs
        consumer = create_consumer('events')
        for msg in consumer:
            data = json.loads(msg.value)
            print(data)
            if 'speed' in data:
                handle_heading_publish(data)
            elif 'runway' in data:
                handle_runway_publish(data)
            elif 'gate' in data:
                handle_gate_publish(data)
            elif 'passenger_count' in data:
                handle_passenger_count(data)
        consumer.close()
