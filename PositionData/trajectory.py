import geopandas as gpd
from shapely.geometry import LineString
from datetime import datetime
import numpy as np
from pyproj import Transformer, CRS
from pyproj.exceptions import CRSError
from .position_base import PositionBase

class Trajectory(PositionBase):
    def __init__(self, position_data, date_column, time_column, tolerance, projection):
        """
        Initialize the Trajectory object and create the trajectory polyline.

        :param position_data: An instance of PositionData.
        :param date_column: Name of the column with date.
        :param time_column: Name of the column with time.
        :param tolerance: The tolerance distance for simplification in meters.
        :param projection: The projection to use for distance calculation.
        """
        self.position_data = position_data
        self.date_column = date_column
        self.time_column = time_column

        # Validate if the projection is a projected CRS
        try:
            crs = CRS.from_user_input(projection)
            if crs.is_projected:
                # Generate the trajectory polyline
                self.polyline_gdf = self._generate_polyline(tolerance, projection)
            else:
                raise ValueError("The provided projection is not a projected CRS.")
        except CRSError:
            raise ValueError("Invalid projection provided.")


    def _parse_datetime(self, row):
        """
        Parse date and time from the row into a datetime object.

        :param row: A row from the position data.
        :return: datetime object.
        """
        date_str = f"{row[self.date_column]} {row[self.time_column]}"
        return datetime.strptime(date_str, "%Y/%m/%d %H:%M:%S.%f")
    
    def _generate_polyline(self, tolerance, projection):
        """
        Generate a simplified trajectory polyline.

        :param tolerance: The tolerance distance for simplification in meters.
        :param projection: The projection to use for distance calculation.
        :return: A GeoDataFrame with the simplified polyline.
        """
        # Filter out None geometries
        valid_data = self.position_data.data[self.position_data.data['geometry'].notnull()]

        # Project to a coordinate system using meters
        transformer_to = Transformer.from_crs(valid_data.crs, projection, always_xy=True)
        projected_points = [transformer_to.transform(point.x, point.y) for point in valid_data['geometry']]
        line = LineString(projected_points)
        simplified_line_projected = line.simplify(tolerance)

        # Ensure it's a LineString
        if not isinstance(simplified_line_projected, LineString):
            simplified_line_projected = LineString(simplified_line_projected)

        # Create and return a GeoDataFrame
        return gpd.GeoDataFrame(geometry=[simplified_line_projected], crs=projection)

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

    def polyline(self):
        """
        Return the simplified trajectory polyline and its length.

        :return: A tuple containing the GeoDataFrame with the polyline and the length of the polyline.
        """
        length = self.polyline_gdf['geometry'].length.iloc[0]  # Length in the units of the CRS
        return self.polyline_gdf, length
    
    def export_as_geojson(self, output_path):
        """
        Export the data as a GeoJSON file.

        :param output_path: Path to save the GeoJSON file.
        """
        self._export_as_geojson(self.polyline_gdf, output_path)