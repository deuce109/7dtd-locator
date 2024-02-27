#!~\Documents\Projects\7DTD-Locator\locator\Scripts\python.exe

import math
import argparse
import re
import numpy as np

import matplotlib as mpl

import matplotlib.pyplot as pt

from bs4 import BeautifulSoup as bs

parser = argparse.ArgumentParser(prog= "locator")

parser.add_argument('-x', default=0)
parser.add_argument('-y', default =0)
parser.add_argument('-map', '--map', action="store_true", default=False)
parser.add_argument('-o', '--output', default='')

args = parser.parse_args()

lat_coord = args.x
lon_coord = args.y

coord_re = re.compile(r'\d*(?:\.\d*)?[NSEW]')

if isinstance(lat_coord,str):
    if coord_re.match(lat_coord):
        lat_coord = float(lat_coord[:-1]) if lat_coord[-1].upper() == "E" else float(lat_coord[:-1]) * -1 
    else:
        lat_coord = float(lat_coord)

if isinstance(lon_coord,str):

    if coord_re.match(lon_coord):
        lon_coord = int(lon_coord[:-1]) if lon_coord[-1].upper() == "S" else int(lon_coord[:-1]) * -1 
    else:
        lon_coord = float(lon_coord)

input_point = (float(lat_coord), float(lon_coord))


def distance_between(p1, p2):

    dx = p2[0]-p1[0]
    dy = p2[1]-p1[1]
    return math.sqrt(math.pow(dx, 2) + (math.pow(dy, 2)))

data = ""

with open("prefabs.xml", "r") as xml:
    prefabs = bs(xml, "lxml")



decs = []

for dec in  prefabs.find_all("decoration"):
    points = dec["position"].split(",")
    decs.append({'name': dec['name'], 'position': (int(points[0]), int(points[2])), 'direction': '', 'distance':0})


for dec in decs:
    position = dec['position']
    dec['distance'] = str(round(distance_between(input_point, position), 3)) + "M" 
    deg_direction = math.fabs(math.atan2(position[1] - input_point[1], position[0] - input_point[0]) * 100)

    cardinals = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW", "N"]

    dec["direction"] = cardinals[round(deg_direction / 22.5)]

x = [dec['position'][0] for dec in decs]
y = [dec['position'][1] for dec in decs]

if args.map:
    img = pt.imread("biomes.png")
    half_size = len(img) / 2
    fig = pt.figure()
    fig.set_facecolor('#303030')
    ax = pt.subplot()
    ax.set_xticks(np.arange(half_size * -1, half_size, 512))
    ax.set_yticks(np.arange(half_size * -1, half_size, 512))
    ax.set_xlim(half_size * -1, half_size)
    ax.set_ylim(half_size, half_size * -1)
    ax.imshow(img,extent=(half_size * -1,half_size,half_size,half_size*-1))
    ax.scatter(x, y, c="#B80000", marker="o", s=3)
    ax.scatter(lat_coord, lon_coord, c="#3FB1DE", marker="o", s=2)

    ax.tick_params(axis='x', colors='#DAE1E7')
    ax.tick_params(axis='y', colors='#DAE1E7')

    ax.spines['bottom'].set_color('#DAE1E7')
    ax.spines['top'].set_color('#DAE1E7')
    ax.spines['left'].set_color('#DAE1E7')
    ax.spines['right'].set_color('#DAE1E7')

    mpl.rcParams.update({'text.color': '#DAE1E7', 'axes.labelcolor': '#DAE1E7'})


    pt.show()

if args.output != "":
    with open(args.output, 'w') as output_writer:
        decs.sort(key= lambda x: x["distance"])
        for dec in decs:
            output_writer.write(format("{name} @ {distance} {direction}\n".format(**dec)))
