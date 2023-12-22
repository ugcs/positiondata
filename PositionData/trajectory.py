import geopandas as gpd
from shapely.geometry import LineString, Point
from datetime import datetime, timedelta
import numpy as np
from math import radians, degrees, atan2, sin, cos, sqrt
from haversine import haversine, Unit
from pyproj import Transformer

class Trajectory:
    def __init__(self, position_data, date_column, time_column):
        """
        Initialize the Trajectory object.

        :param position_data: An instance of PositionData.
        :param date_column: Name of the column with date.
        :param time_column: Name of the column with time.
        """
        self.position_data = position_data
        self.date_column = date_column
        self.time_column = time_column

    def _parse_datetime(self, row):
        """
        Parse date and time from the row into a datetime object.

        :param row: A row from the position data.
        :return: datetime object.
        """
        date_str = f"{row[self.date_column]} {row[self.time_column]}"
        return datetime.strptime(date_str, "%Y/%m/%d %H:%M:%S.%f")

    def duration(self, unit='seconds'):
        """
        Calculate the duration between the first and last record.

        :param unit: The unit of time for the duration ('seconds', 'minutes', 'hours').
        :return: Duration in the specified unit.
        """
        first_time = self._parse_datetime(self.position_data.data.iloc[0])
        last_time = self._parse_datetime(self.position_data.data.iloc[-1])
        duration = last_time - first_time

        if unit == 'seconds':
            return duration.total_seconds()
        elif unit == 'minutes':
            return duration.total_seconds() / 60
        elif unit == 'hours':
            return duration.total_seconds() / 3600
        else:
            raise ValueError("Invalid time unit. Choose 'seconds', 'minutes', or 'hours'.")

    def polyline(self, output_path, tolerance, projection):
        """
        Simplify the trajectory and save it as a polyline in GeoJSON format.

        :param output_path: Path to save the GeoJSON file.
        :param tolerance: The tolerance distance for simplification in meters.
        :param projection: The projection to use for distance calculation.
        """
        # Filter out None geometries
        valid_data = self.position_data.data[self.position_data.data['geometry'].notnull()]

        # Project to a coordinate system using meters
        transformer_to = Transformer.from_crs(valid_data.crs, projection, always_xy=True)
        transformer_from = Transformer.from_crs(projection, valid_data.crs, always_xy=True)
        projected_points = [transformer_to.transform(point.x, point.y) for point in valid_data['geometry']]
        line = LineString(projected_points)
        simplified_line_projected = line.simplify(tolerance)

        # Check if the simplified line is a LineString
        if not isinstance(simplified_line_projected, LineString):
            simplified_line_projected = LineString(simplified_line_projected)

        # Reproject back to original CRS
        reprojected_points = [transformer_from.transform(*pt) for pt in simplified_line_projected.coords]
        simplified_line = LineString(reprojected_points)

        # Create a GeoDataFrame and save as GeoJSON
        gdf = gpd.GeoDataFrame(geometry=[simplified_line], crs=valid_data.crs)
        gdf.to_file(output_path, driver='GeoJSON')

        print(f"Simplified trajectory polyline saved to {output_path}")