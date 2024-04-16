#!F:\Projects\7dtd-locator\Scripts\python.exe

import argparse
import sys
import logging

import arg_handler
from locator import Locator
from form import show_window

parser = argparse.ArgumentParser(prog= "7dtd-locator")

parser.add_argument('--latitude', '-x', dest="x", default=0, help="east / west value to be used to calculate distance to POIs")
parser.add_argument('--longitude', '-y', dest="y", default =0, help="north / south value to be used to calculate distance to POIs")
parser.add_argument("-i", "--input", dest="input", help="path containing a 7DTD generated world")
parser.add_argument("--logging", dest="logging", default="INFO", choices=["DEBUG", "INFO", "WARN", "ERROR", "FATAL"], help="set logging level")
parser.add_argument('--output', '-o', dest="output", default=None, help="path to output the generated data files to")
parser.add_argument('--filter', '-f', dest="filter", default=".*", help="regex filter to filter POIs")
parser.add_argument('--pois', '-p', dest="write_pois", default=True, choices=[True, False], help="write POIs to data file")
parser.add_argument('--spawns', '-s', dest="write_spawns", default=False, choices=[True, False], help="write spawnpoints to data file")

args = parser.parse_args()

# logging = logging.getLogger("7DTD Locator")

logging.basicConfig(level=arg_handler.determine_logging_level(args.logging), format='%(levelname)s | %(asctime)s | %(message)s')

logging.info("Logger initialized.")

if args.input is None:
    show_window()

if (arg_handler.check_path(args.input)):
    logging.info("Input path verified")
else:
    parser.print_help()
    sys.exit(-1)



input_point = arg_handler.convert_coords(args.x, args.y)


locator: Locator

locator = Locator(base_path=args.input, center_point=input_point, poi_filter=args.filter, output_path=args.output)

locator.locate_prefabs()
locator.locate_spawnpoints()

if args.output:
    locator.generate_data(get_pois=args.write_pois, get_spawns=args.write_spawns)

else:
    locator.add_markers()

# locator.display_map()