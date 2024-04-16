#!F:\Projects\7dtd-locator\Scripts\python.exe

import json
import logging
import math
import re
from typing import Dict, List, Tuple
import io
from bs4 import BeautifulSoup as bs
import os

import matplotlib.pyplot as pt
import matplotlib.style as mplstyle

from dashboard import DashboardAPI, Marker

mplstyle.use('fast')


def _get_map_info(path):

    map_info = {}

    if os.path.exists(path):

        with open(os.path.join(path), "r") as xml:
            info = bs(xml, "lxml")

        for prop in  info.find_all("property"):
            map_info[prop['name']] = prop['value']

    return map_info
    

    

class Locator():

    center_point: Tuple[float, float]

    _base_path: str = ""

    _map_info: Dict[str, str] = None

    poi_filter: re.Pattern = None

    _prefab_mappings: List[Dict[str,str]]

    _camel_case_re: re.Pattern = re.compile("(?:^|_)([a-z])")

    _number_re: re.Pattern = re.compile("_?\d?\d?")

    output_path: str = ""

    _map_is_generated: bool = False

    _prefabs: List[Dict[str,str]] = []

    _spawns: List[Dict[str,str]] = []

    image: io.BytesIO = io.BytesIO()

    def __init__(self,base_path: str, center_point: Tuple[float, float] = (0,0), poi_filter: str | re.Pattern = ".*", output_path: str = None):
        self.center_point = center_point
        self.base_path = base_path
        self._map_info = _get_map_info(os.path.join(self._base_path, 'map_info.xml'))
        self.poi_filter = re.compile((poi_filter if isinstance(poi_filter, str) else poi_filter.pattern), re.IGNORECASE)
        self.output_path = output_path
        with open("id_mappings.json") as json_reader:
            self._prefab_mappings = json.load(json_reader)

        logging.info("Locator initialized.")


    def __init__(self):
        with open("id_mappings.json") as json_reader:
            self._prefab_mappings = json.load(json_reader)

    def _distance_between(self, p1, p2):

        dx = p2[0]-p1[0]
        dy = p2[1]-p1[1]
        return math.sqrt(math.pow(dx, 2) + (math.pow(dy, 2)))


    
    def _angle_between(self, p1, p2):
        rad = math.atan2(p2[1] - p1[1], p2[0] - p1[1])
        deg = math.degrees(rad)

        return math.fabs(deg % 360)
    
    def _generate_directions(self, center_point, dec):

        position = dec['position']
        dec['distance'] = str(round(self._distance_between(center_point, position), 3)) + "M" 
        deg_direction = self._angle_between(center_point, position)

        print(deg_direction, round(deg_direction / 22.5))

        cardinals = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]

        cardinals = cardinals[4:] + cardinals[:4]

        dec["direction"] = cardinals[math.floor(deg_direction / 22.5)]

        return dec

    def _generate_half_size(self):
        return int(self._map_info["HeightMapSize"].split(",")[0]) / 2

    def _add_img_layer(self,ax, file:str ):
        half_size = self._generate_half_size()
        img = pt.imread(os.path.join(self._base_path, file))
        ax.imshow(img,extent=(half_size * -1,half_size,half_size,half_size*-1))
        logging.info("Added file: " + file)

    def _add_plot_layer(self, ax, items, color:str, marker="o", size=3, label=None ):
        x = [item['position'][0] for item in items]
        y = [item['position'][1] for item in items]

        ax.scatter(x, y, c=color, marker=marker, s=size, label=label)

        logging.info("Added layer: " + label)


    def _add_single_point_layer(self, ax, x, y, color:str, marker="o", size=3):
        ax.scatter(x, y , c=color, marker=marker, s=size)
        logging.info(f"Added point ({x}, {y})")


    def _generate_prefab_name(self, prefab_id: str):
        name = [mapping.get("name", "$") for mapping in self._prefab_mappings if re.compile(mapping["id_regex"]).match(prefab_id)]
        if len(name) == 0 or name[0] == "$":

            if not name:
                name = prefab_id

            replacements = [mapping for mapping in self._prefab_mappings if re.compile(mapping["id_regex"]).match(prefab_id)]
            for replacement in replacements:
                name = prefab_id.replace(replacement["id_regex"], replacement["replace"] )

        else:
            name = name[0]

        name = self._camel_case_re.sub(lambda x: " " + x.group().upper(), name).strip()

        name = self._number_re.sub("", name)

        return name
    
    
    def _pad_line(self, line:str, max_length):
        m_index = min([i for i in [line.find(str(i)) for i in range(0,10)] if i > 0])
        padding = " " * (max_length - len(line))
        return line[:m_index] + padding + line[m_index:]


    def _pad_lines(self,lines):
        max_length = max([len(line) for line in lines])
        return [self._pad_line(line, max_length) for line in lines]
    

    def _generate_coords(self, point):
        east_west = str(point[0] * -1) + "W" if point[0] <= 0 else str(point[0]) + "E"

        north_south = (str(point[1] * -1) + "S" if point[1] <= 0 else str(point[1]) + "N")

        return f"{east_west:<6} {north_south}"
                
    def _sort_by_distance(self, item):
        if isinstance(item["distance"], str):
            return float(item['distance'].replace("M", ""))
        else:
            return item['distance']
        
    def set_filter(self, filter:str | re.Pattern):
        self.poi_filter = re.compile((filter if isinstance(filter, str) else filter.pattern), re.IGNORECASE)
    
    def set_input_path(self, path):
        self._base_path = path
        self._map_info = _get_map_info(os.path.join(self._base_path, 'map_info.xml'))

    def locate_spawnpoints(self):
        with open(os.path.join(self._base_path, 'spawnpoints.xml'), "r") as xml:
            spawns = bs(xml, "lxml")

        for spawn in  spawns.find_all("spawnpoint"):
            points = spawn["position"].split(",")
            self._spawns.append({'position': (int(points[0]), int(points[2])), 'direction': '', 'distance':0})

        logging.info("Spawnpoints located")
        
        self._spawns = [self._generate_directions(self.center_point, spawn) for spawn in self._spawns]
    
    def generate_map(self):
        
        logging.info("Starting map generation")

        if not self._map_is_generated:
            half_size = self._generate_half_size()

            fig = pt.figure()
            fig.set_facecolor('#303030')

            
            ax = pt.subplot()

            ax.set_ylim(half_size * -1, half_size)

            
            self._add_img_layer(ax, 'biomes.png')
            self._add_img_layer(ax, 'splat3.png')

            if len(self._prefabs) == 0:
                self.locate_prefabs()

            if len(self._spawns) == 0:
                self.locate_spawnpoints()

            self._add_plot_layer(ax, self._prefabs, "#B80000", label="Prefabs", size=5)
            self._add_plot_layer(ax, self._spawns, "#ADD8E6", size=2, label="Spawnpoints")

            self._add_single_point_layer(ax, self.center_point[0], self.center_point[1], color="yellow", marker='x', size=2)

            pt.axis('off')
            fig = pt.gcf()
            fig.savefig(self.image, format='svg', bbox_inches='tight')

            self.image.seek(0)

        self._map_is_generated = True

        logging.info("Plotting completed.")

    def locate_prefabs(self):
        center_point = self.center_point


        with open(os.path.join(self._base_path, 'prefabs.xml'), "r") as xml:
            prefabs = bs(xml, "lxml")
        logging.info("Prefab XML read")

        for dec in  prefabs.find_all("decoration"):
            
            name = self._generate_prefab_name(dec['name'])
            if not self.poi_filter or self.poi_filter.search(name):
                points = dec["position"].split(",")
                print(points)
                self._prefabs.append({'id': dec['name'], 'name': name, 'position': (int(points[0]), int(points[2])), 'direction': '', 'distance':0})

        logging.info("POIs located")

        self._prefabs = [self._generate_directions(center_point, dec) for dec in self._prefabs if dec['name']]

    def display_map(self):

        self.generate_map()

        pt.show()

    def add_markers(self):
        
        dashboard = DashboardAPI()

        markers = [Marker(*prefab['position']) for prefab in self._prefabs]

        dashboard.add_markers(markers)

    def generate_data(self, get_spawns: bool=False, get_pois: bool=True, write_file:bool=True):

        self.generate_map()

        data_string = ""

        if get_pois:

            if len(self._prefabs) == 0:
                self.locate_prefabs()

            self._prefabs.sort(key=self._sort_by_distance)

            self._prefabs = [{
            "name": dec["name"],
            "coordinates": self._generate_coords(dec["position"]),
            "distance": dec["distance"],
            "direction": dec["direction"],
                } for dec in self._prefabs]
            
            self._prefabs.insert(0, {"name": "POI Name", "coordinates": "Coordinates", "distance": "Distance", "direction": "Direction"})

            data_string += "".join( ["{name:22} {coordinates:<14} {distance:>9} {direction:3}\n".format(**poi) for poi in self._prefabs] )

        if get_spawns:
            if len(self._spawns) == 0:
                self.locate_spawnpoints()
            self._spawns.sort(key=self._sort_by_distance)

            self._spawns = [ {
                    "coordinates": self._generate_coords(spawn["position"]),
                    "distance": spawn["distance"],
                    "direction": spawn["direction"],
                } for spawn in self._spawns]
                
            self._spawns.insert(0, {"coordinates": "Coordinates", "distance": "Distance", "direction": "Direction"})

            data_string += "".join( ["{coordinates:<14} {distance:>10} {direction:3}\n".format(**spawn) for spawn in self._spawns] )
        
        self._prefabs = []
        self._spawns = []
        
        logging.info("Data generated writing...")


        if write_file:

            with open(os.path.join(self.output_path, "data.txt"), 'w') as output_writer:
               output_writer.write(data_string)

        else:
            return data_string
        
    def clear_data(self):

        self._prefabs = []

        self._spawns = []

        self.image = io.BytesIO()
        self._map_is_generated = False