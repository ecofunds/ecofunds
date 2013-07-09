from ecofunds.models import Location
from BeautifulSoup import BeautifulSoup

def polygon_centroid(corners):
    n = len(corners)
    cx = float(sum(x for x, y in corners)) / n
    cy = float(sum(y for x, y in corners)) / n
    return cx, cy

for location in Location.objects.all():
    xml = BeautifulSoup(location.polygon)
    paths = []
    corners = []
    for polygon in xml.findAll('polygon'):
        try:
            coordinates = polygon.outerboundaryis.linearring.coordinates.text.split(' ')
            for c in coordinates:

                o = c.split(',')
                cx = float(o[1])
                cy = float(o[0])
                corners.append((cx, cy))
        except Exception as e:
            print("Error %d %s - %s" % (location.id, location.name.encode('utf-8'), e))

    try:
        x, y = polygon_centroid(corners)
        location.centroid = "%s,%s" % (str(x), str(y))
        location.save()
    except:
        print("Error Centroid %s - %s" % (location.name.encode('utf-8'), e))
