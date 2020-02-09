from ATC.models import SIZES


def validate_name(str, obj, id):  # the string to validate, the object type, the element id
    res = obj.objects.filter(name=str)
    if res.count() > 0 and res[0].id != id:
        return False
    return True


# check if username exists and is not same object
def validate_username(str, obj, id):
    res = obj.objects.filter(username=str)
    if res.count() > 0 and res[0].id != id:
        return False
    return True


def validate_identifier(str, obj, id):
    res = obj.objects.filter(identifier=str)
    if res.count() > 0 and res[0].id != id:
        return False
    return True


def set_coords(airport, request):  # specific for airports
    res = request.POST.get("x")
    if res:
        airport.x = res
    res = request.POST.get("y")
    if res:
        airport.y = res
    airport.save()


def get_size(str):
    if str == 'SMALL':
        return SIZES[0][0]
    elif str == 'MEDIUM':
        return SIZES[1][0]
    elif str == 'LARGE':
        return SIZES[2][0]
