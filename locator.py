#!F:\Projects\7dtd-locator\Scripts\python.exe

import math
import re
from typing import Dict, Tuple
import numpy as np

import matplotlib as mpl

import matplotlib.pyplot as pt

from bs4 import BeautifulSoup as bs

import os

def _get_map_info(path):

    map_info = {}

    with open(os.path.join(path), "r") as xml:
        info = bs(xml, "lxml")

    for prop in  info.find_all("property"):
        map_info[prop['name']] = prop['value']

    return map_info

    

class Locator():

    center_point: Tuple[float, float]

    base_path: str = ""

    map_info: Dict[str, str]

    def __init__(self,base_path: str, center_point: Tuple[float, float] = (0,0)):
        self.center_point = center_point
        self.base_path = base_path
        self.map_info = _get_map_info(os.path.join(self.base_path, 'map_info.xml'))

    def _distance_between(self, p1, p2):

        dx = p2[0]-p1[0]
        dy = p2[1]-p1[1]
        return math.sqrt(math.pow(dx, 2) + (math.pow(dy, 2)))

    def _generate_directions(self, center_point, dec):

        position = dec['position']
        dec['distance'] = str(round(self._distance_between(center_point, position), 3)) + "M" 
        deg_direction = math.fabs(math.atan2(position[1] - center_point[1], position[0] - center_point[0]) * 100)

        cardinals = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW", "N"]

        dec["direction"] = cardinals[round(deg_direction / 22.5)]

        return dec
    
    def locate_spawnpoints(self):
        with open(os.path.join(self.base_path, 'spawnpoints.xml'), "r") as xml:
            spawns = bs(xml, "lxml")

        spawnpoints = []

        for spawn in  spawns.find_all("spawnpoint"):
            points = spawn["position"].split(",")
            spawnpoints.append({'position': (int(points[0]), int(points[2])), 'direction': '', 'distance':0})
        
        return [self._generate_directions(self.center_point, spawn) for spawn in spawnpoints]

    def _generate_half_size(self):
        return int(self.map_info["HeightMapSize"].split(",")[0]) / 2

    def _add_img_layer(self,ax, file:str ):
        half_size = self._generate_half_size()
        img = pt.imread(os.path.join(self.base_path, file))
        ax.imshow(img,extent=(half_size * -1,half_size,half_size,half_size*-1))

    def _add_plot_layer(self, ax, items, color:str, marker="o", size=3 ):
        x = [item['position'][0] for item in items]
        y = [item['position'][1] for item in items]

        ax.scatter(x, y, c=color, marker=marker, s=size)

    def _add_single_point_layer(self, ax, x, y, color:str, marker="o", size=3):
        ax.scatter(x, y , c=color, marker=marker, s=size)


    # def _add_layer(self, type, path=None, x=None, y=None):

        

    def locate_prefabs(self):
        center_point = self.center_point

        with open(os.path.join(self.base_path, 'prefabs.xml'), "r") as xml:
            prefabs = bs(xml, "lxml")



        decs = []

        for dec in  prefabs.find_all("decoration"):
            points = dec["position"].split(",")
            decs.append({'name': dec['name'], 'position': (int(points[0]), int(points[2])), 'direction': '', 'distance':0})


        decs = [self._generate_directions(center_point, dec) for dec in decs]

        return decs

    def generate_map(self):

        decs = self.locate_prefabs()
        spawns = self.locate_spawnpoints()
        half_size = self._generate_half_size()

        fig = pt.figure()
        fig.set_facecolor('#303030')
        ax = pt.subplot()
        ax.set_xticks(np.arange(half_size * -1, half_size, 512))
        ax.set_yticks(np.arange(half_size * -1, half_size, 512))

        ax.set_xlim(half_size * -1, half_size)
        ax.set_ylim(half_size, half_size * -1)

        self._add_img_layer(ax, 'biomes.png')
        self._add_img_layer(ax, 'splat3.png')
        self._add_img_layer(ax, 'splat4.png')
        self._add_img_layer(ax, 'radiation.png')

        self._add_plot_layer(ax, decs, "#B80000")
        self._add_plot_layer(ax, spawns, "#ADD8E6", size=2)

        self._add_single_point_layer(ax, self.center_point[0], self.center_point[1], color="red", marker='x', size=2)


        ax.tick_params(axis='x', colors='#DAE1E7')
        ax.tick_params(axis='y', colors='#DAE1E7')

        ax.spines['bottom'].set_color('#DAE1E7')
        ax.spines['top'].set_color('#DAE1E7')
        ax.spines['left'].set_color('#DAE1E7')
        ax.spines['right'].set_color('#DAE1E7')

        mpl.rcParams.update({'text.color': '#DAE1E7', 'axes.labelcolor': '#DAE1E7'})


        pt.show()


    def generate_data_file(self, output_file: str):

        decs = self.locate_prefabs()

        with open(output_file, 'w') as output_writer:
            decs.sort(key= lambda x: x["distance"])
            for dec in decs:
                output_writer.write(format("{name} @ {distance} {direction}\n".format(**dec)))
