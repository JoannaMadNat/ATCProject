class Point:
    x = float
    y = float

    def __init__(self, x, y):
        self.x = x
        self.y = y


def on_segment(p, q, r):
    if max(p.x, r.x) >= q.x >= min(p.x, r.x) and max(p.y, r.y) >= q.y >= min(p.y, r.y):
        return True
    return False


def orientation(p, q, r):
    val = (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)
    if val == 0:
        return 0
    if val > 0:
        return 1
    else:
        return 2


def check_if_intersect(p1, q1, p2, q2):
    # https://www.geeksforgeeks.org/program-for-point-of-intersection-of-two-lines/
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    # general case
    if o1 != o2 and o3 != o4:
        return True
    # special cases
    if o1 == 0 and on_segment(p1, p2, q1):
        return True
    if o2 == 0 and on_segment(p1, q2, q1):
        return True
    if o3 == 0 and on_segment(p2, p1, q2):
        return True
    if o4 == 0 and on_segment(p2, q1, q2):
        return True
    return False


def get_intersect_point(a, b, c, d):
    # https://www.geeksforgeeks.org/program-for-point-of-intersection-of-two-lines/

    a1 = b.y - a.y
    b1 = a.x - b.x
    c1 = a1 * a.x + b1 * a.y
    a2 = d.y - c.y
    b2 = c.x - d.x
    c2 = a2 * c.x + b2 * c.y
    determinant = a1 * b2 - a2 * b1

    if determinant == 0:
        return None
    else:
        x = (b2 * c1 - b1 * c2) / determinant
        y = (a1 * c2 - a2 * c1) / determinant
    return Point(x, y)


def get_coords(plane, other_plane):
    port_origin_1 = plane.takeoff_airport
    port_dest_1 = plane.landing_airport
    port_origin_2 = other_plane.takeoff_airport
    port_dest_2 = other_plane.landing_airport

    a = Point(port_origin_1.x, port_origin_1.y)
    b = Point(port_dest_1.x, port_dest_1.y)
    c = Point(port_origin_2.x, port_origin_2.y)
    d = Point(port_dest_2.x, port_dest_2.y)

    return a, b, c, d


def get_intersect_data(plane, other_plane):
    a, b, c, d = get_coords(plane, other_plane)

    if not check_if_intersect(a, b, c, d):
        return None

    intersect = get_intersect_point(a, b, c, d)
    return intersect
