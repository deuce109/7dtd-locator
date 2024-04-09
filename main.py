#!F:\Projects\7dtd-locator\Scripts\python.exe

import argparse
import sys
import arg_handler
from locator import Locator

# import matplotlib as mpl

# import matplotlib.pyplot as pt

# from bs4 import BeautifulSoup as bs

parser = argparse.ArgumentParser(prog= "locator")

parser.add_argument('-x', default=0)
parser.add_argument('-y', default =0)
parser.add_argument('-i', dest="input", required=True)
parser.add_argument('-m', dest="map", action="store_true", default=False, )
parser.add_argument('-o', dest="output", default='')

args = parser.parse_args()


if not (arg_handler.check_path(args.input)):
    sys.exit(1)


input_point = arg_handler.convert_coords(args.x, args.y)

locator = Locator(args.input, input_point)

if args.map:
    locator.generate_map()

if args.output:
    locator.generate_data_file(args.output)



# def distance_between(p1, p2):

#     dx = p2[0]-p1[0]
#     dy = p2[1]-p1[1]
#     return math.sqrt(math.pow(dx, 2) + (math.pow(dy, 2)))

# data = ""

# with open("prefabs.xml", "r") as xml:
#     prefabs = bs(xml, "lxml")



# decs = []

# for dec in  prefabs.find_all("decoration"):
#     points = dec["position"].split(",")
#     decs.append({'name': dec['name'], 'position': (int(points[0]), int(points[2])), 'direction': '', 'distance':0})


# for dec in decs:
#     position = dec['position']
#     dec['distance'] = str(round(distance_between(input_point, position), 3)) + "M" 
#     deg_direction = math.fabs(math.atan2(position[1] - input_point[1], position[0] - input_point[0]) * 100)

#     cardinals = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW", "N"]

#     dec["direction"] = cardinals[round(deg_direction / 22.5)]

# x = [dec['position'][0] for dec in decs]
# y = [dec['position'][1] for dec in decs]

# if args.map:
#     img = pt.imread("biomes.png")
#     half_size = len(img) / 2
#     fig = pt.figure()
#     fig.set_facecolor('#303030')
#     ax = pt.subplot()
#     ax.set_xticks(np.arange(half_size * -1, half_size, 512))
#     ax.set_yticks(np.arange(half_size * -1, half_size, 512))
#     ax.set_xlim(half_size * -1, half_size)
#     ax.set_ylim(half_size, half_size * -1)
#     ax.imshow(img,extent=(half_size * -1,half_size,half_size,half_size*-1))
#     ax.scatter(x, y, c="#B80000", marker="o", s=3)
#     ax.scatter(lat_coord, lon_coord, c="#3FB1DE", marker="o", s=2)

#     ax.tick_params(axis='x', colors='#DAE1E7')
#     ax.tick_params(axis='y', colors='#DAE1E7')

#     ax.spines['bottom'].set_color('#DAE1E7')
#     ax.spines['top'].set_color('#DAE1E7')
#     ax.spines['left'].set_color('#DAE1E7')
#     ax.spines['right'].set_color('#DAE1E7')

#     mpl.rcParams.update({'text.color': '#DAE1E7', 'axes.labelcolor': '#DAE1E7'})


#     pt.show()

# if args.output != "":
#     with open(args.output, 'w') as output_writer:
#         decs.sort(key= lambda x: x["distance"])
#         for dec in decs:
#             output_writer.write(format("{name} @ {distance} {direction}\n".format(**dec)))
