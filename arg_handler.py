import logging
import re
import os
import zlib

coord_re = re.compile(r'\d*(?:\.\d*)?[NSEW]')

def convert_coords(lat_coord, lon_coord):
    try:
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

        logging.info("Input coordinates verified")

        return (float(lat_coord), float(lon_coord))

    except Exception as e:

        logging.warn(e)
        return None



def _get_checksum(filepath: str) -> int:
    if not os.path.exists(filepath):
        return -1
    with open(filepath, 'rb') as byte_reader:
        return zlib.crc32(byte_reader.read())

def _check_checksum(world_path, file_path, checksum) -> bool:
    return _get_checksum(os.path.join(world_path, file_path)) == int(checksum)

def check_path(world_path: str) -> bool:
    try:
        with open(os.path.join(world_path, 'checksums.txt')) as checksum_reader:
            checksum_reader.seek(3)
            valid = all([_check_checksum(world_path, *(line.split("="))) for line in checksum_reader])
        return valid
    except FileNotFoundError as e:
        return False
    except Exception as e:
        logging.error(e)
        return False

def validate_filter(filter_string: str) -> re.Pattern:
        try:
            return re.compile(filter_string)
        except Exception as e:
            logging.warn(e)
            return None

def determine_logging_level(logging_level):
    match logging_level:

        case  "DEBUG":
            return logging.DEBUG
        case  "INFO":
            return logging.INFO
        case  "WARNING":
            return logging.WARNING
        case  "ERROR":
            return logging.ERROR
        case  "FATAL":
            return logging.FATAL