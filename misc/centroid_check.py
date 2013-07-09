from ecofunds.models import Location

ok = 0
error = 0

print("Total locations %d" % (Location.objects.count()))

for location in Location.objects.all():
    if not location.centroid or location.centroid == "":
        print("Locatio id %d %s without centroid" % (location.id, location.name.encode('utf-8')))
        error += 1
    else:
        print("Locatio id %d %s OK" % (location.id, location.name.encode('utf-8')))
        ok += 1

print("OK %d" % (ok))
print("Error %d" % (error))
