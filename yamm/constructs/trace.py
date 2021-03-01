from __future__ import annotations

from csv import DictReader
from pathlib import Path
from typing import List

from pyproj import CRS, Transformer

from yamm.constructs.coordinate import Coordinate

valid_latitude_names = {'latitude', 'Latitude', 'lat', 'Lat'}
valid_longitude_names = {'longitude', 'Longitude', 'Lon', 'Lon', 'long', 'Long'}


class Trace:
    def __init__(self, coords: List[Coordinate], project_xy: bool = False):
        if project_xy:
            base_crs = CRS(4326)
            xy_crs = CRS(3857)
            transformer = Transformer.from_crs(base_crs, xy_crs)

            lats = [c.lat for c in coords]
            lons = [c.lon for c in coords]

            lat_proj, lon_proj = transformer.transform(lats, lons)

            coords = [Coordinate(lat=lat, lon=lon, x=x, y=y) for x, y, lat, lon in zip(lat_proj, lon_proj, lats, lons)]

        self.coords = coords

    def __getitem__(self, i):
        return Trace(self.coords[i])

    @classmethod
    def from_csv(cls, file: str, project_xy: bool = False) -> Trace:
        """
        Builds a trace from a csv file.

        Expects the file to have latitude / longitude information in the epsg 4326 format

        :param file: the file to load
        :param project_xy: should the trace include the XY projection?
        :return: the trace
        """
        filepath = Path(file)
        if not filepath.is_file():
            raise FileNotFoundError(file)
        elif not filepath.suffix == ".csv":
            raise TypeError(f"file of type {filepath.suffix} does not appear to be a csv file")

        lats = []
        lons = []
        with filepath.open('r') as f:
            reader = DictReader(f)

            lat_name_set = valid_latitude_names.intersection(set(reader.fieldnames))
            lon_name_set = valid_longitude_names.intersection(set(reader.fieldnames))

            if len(lat_name_set) == 0:
                raise ValueError(f"could not find latitude information from fields {set(reader.fieldnames)}")
            elif len(lat_name_set) > 1:
                raise ValueError("found multiple instances of latitude; please only provide one")
            else:
                lat_name = list(lat_name_set)[0]

            if len(lon_name_set) == 0:
                raise ValueError(f"could not find longitude information from fields {set(reader.fieldnames)}")
            elif len(lon_name_set) > 1:
                raise ValueError("found multiple instances of longitude; please only provide one")
            else:
                lon_name = list(lon_name_set)[0]

            for row in reader:
                lats.append(float(row[lat_name]))
                lons.append(float(row[lon_name]))

        if project_xy:
            base_crs = CRS(4326)
            xy_crs = CRS(3857)
            transformer = Transformer.from_crs(base_crs, xy_crs)

            lat_proj, lon_proj = transformer.transform(lats, lons)

            coords = [Coordinate(lat=lat, lon=lon, x=x, y=y) for x, y, lat, lon in zip(lat_proj, lon_proj, lats, lons)]
        else:
            coords = [Coordinate(lat=lat, lon=lon) for lat, lon in zip(lats, lons)]

        return Trace(coords)
