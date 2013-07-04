'''Generate 100 positions color scale values

$ python generate_scale > colors_SOMESCALE.py
'''
import pylab

colors = []

for i in range(101):
    scale = i * 0.01
    tp = pylab.cm.RdYlBu(1 - scale)
    rgb = []
    for c in tp[:3]:
        rgb.append(c * 255)
    colors.append(tuple(rgb))

print("scale = %s" % str(colors))
