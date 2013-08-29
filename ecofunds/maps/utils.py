def parse_centroid(centroid):
    latlng = centroid.split(',')
    x = float(latlng[0].strip())
    y = float(latlng[1].strip())
    return (x, y)
