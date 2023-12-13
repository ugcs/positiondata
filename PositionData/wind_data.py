import geopandas as gpd
from geopy.distance import geodesic
from windrose import WindroseAxes
import math
import numpy as np
import pandas as pd
from PositionData import PositionData
from scipy.interpolate import griddata

class WindData:
    def __init__(self, position_data,air_speed_prop, air_dir_prop, platform_speed_prop, platform_dir_prop, true_speed_prop, true_dir_prop, sensor_cw_rot = 0, sensor_to_north = False):
        """
        Initialize the WindMap with an instance of PositionData.

        :param position_data: An instance of PositionData.
        :param air_speed_prop: Property name for air speed.
        :param air_dir_prop: Property name for air direction.
        :param platform_speed_prop: Property name for platform speed.
        :param platform_dir_prop: Property name for platform direction.
        :param true_speed_prop: Property name for true wind speed.
        :param true_dir_prop: Property name for true wind direction.
        :param sensor_cw_rot: CW rotation of the sensor relative to platform noze
        :param sensor_to_north: if true, means that sensor readings are related to North, otherwise relative to platform noze
        """
        if not isinstance(position_data, PositionData):
            raise ValueError("position_data must be an instance of PositionData")
        
        # process true wind columns
        self.position_data = self._true_wind(position_data, air_speed_prop, air_dir_prop, platform_speed_prop, platform_dir_prop, true_speed_prop, true_dir_prop)
    
    def _true_wind(self, position_data, air_speed_prop, air_dir_prop, platform_speed_prop, platform_dir_prop, true_speed_prop, true_dir_prop,sensor_cw_rot = 0, sensor_to_north = False):
        """
        Calculate the true wind speed and direction based on platform and measured wind data.

        :param air_speed_prop: Property name for air speed.
        :param air_dir_prop: Property name for air direction.
        :param platform_speed_prop: Property name for platform speed.
        :param platform_dir_prop: Property name for platform direction.
        :param true_speed_prop: Property name for true wind speed.
        :param true_dir_prop: Property name for true wind direction.
        :param sensor_cw_rot: CW rotation of the sensor relative to platform noze
        :param sensor_to_north: if true, means that sensor readings are related to North, otherwise relative to platform noze
        :return: New instance of PositionData with calculated true wind.
        """
        new_gdf = position_data.data.copy()

        for idx, row in new_gdf.iterrows():
            try:
                # Platform vector
                platform_speed = float(row[platform_speed_prop])
                platform_dir = math.radians(float(row[platform_dir_prop]))  # Convert degrees to radians

                platform_x = platform_speed * math.sin(platform_dir)
                platform_y = platform_speed * math.cos(platform_dir)

                # Measured wind vector
                # TODO take into account sensor orientation and reference datum
                wind_speed = float(row[air_speed_prop])
                wind_dir = math.radians(float(row[air_dir_prop]))

                wind_x = wind_speed * math.sin(wind_dir)
                wind_y = wind_speed * math.cos(wind_dir)

                # True wind vector
                true_wind_x = wind_x - platform_x
                true_wind_y = wind_y - platform_y 

                # Convert back to speed and direction
                true_wind_speed = math.sqrt(true_wind_x**2 + true_wind_y**2)
                true_wind_dir = (math.degrees(math.atan2(true_wind_x, true_wind_y)) + 360) % 360

                # Assign to separate properties in the GeoDataFrame using loc
                new_gdf.loc[idx, true_speed_prop] = true_wind_speed
                new_gdf.loc[idx, true_dir_prop] = true_wind_dir

            except (ValueError, TypeError): 
                # If there's any missing or invalid data, continue to the next row
                continue
    
        result = PositionData.__new__(PositionData)
        result.data = new_gdf.copy()

        return result
    
    def grid_wind(self, speed_property, direction_property, method='linear', resolution=100):
        """
        Grid measurements 

        :param speed_property: Property name for air speed.
        :param direction_property: Property name for air direction.
        :param method: gridding method according to https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.griddata.html
        :param resolution: grid size 
        """
        # Check if the properties exist
        for prop in [speed_property, direction_property]:
            if prop not in self.position_data.data.columns:
                raise ValueError(f"'{prop}' does not exist in the properties.")

        data = self.position_data.data.dropna(subset=[speed_property, direction_property])
        # Convert the properties to float and drop non-numeric values (NaN)
        for prop in [speed_property, direction_property]:
            data[prop] = pd.to_numeric(data[prop], errors='coerce')

        # Extract x, y, and vector values for interpolation
        x = data.geometry.x.values
        y = data.geometry.y.values
        speed_values = data[speed_property].values
        direction_values = np.radians(data[direction_property].values)  # Convert to radians

        # Convert polar coordinates (speed, direction) to cartesian for interpolation
        u = speed_values * np.sin(direction_values)
        v = speed_values * np.cos(direction_values)

        # Create a grid
        grid_y, grid_x = np.mgrid[max(y):min(y):complex(0, resolution), min(x):max(x):complex(0, resolution)]

        # Interpolate u and v components
        grid_u = griddata((x, y), u, (grid_x, grid_y), method=method)
        grid_v = griddata((x, y), v, (grid_x, grid_y), method=method)

        # Convert back interpolated cartesian to polar coordinates
        interpolated_speed = np.sqrt(grid_u**2 + grid_v**2)
        interpolated_direction = (np.degrees(np.arctan2(grid_u, grid_v)) + 360) % 360  # Convert back to degrees

        # Convert grid to GeoDataFrame
        grid_geom = [gpd.points_from_xy(grid_x_row, grid_y_row) for grid_x_row, grid_y_row in zip(grid_x, grid_y)]
        grid_geom = [point for sublist in grid_geom for point in sublist]  # Flatten the list
        grid_df = gpd.GeoDataFrame(geometry=grid_geom)
        grid_df.set_crs(data.crs)

        # Assign interpolated data to the GeoDataFrame
        grid_df[speed_property] = interpolated_speed.ravel()
        grid_df[direction_property] = interpolated_direction.ravel()

        # Return a new PositionData instance
        result = PositionData.__new__(PositionData)
        result.data = grid_df.copy()

        return result
