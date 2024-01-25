import geopandas as gpd
import matplotlib.pyplot as plt
import math
import numpy as np
import pandas as pd
from shapely.geometry import Point
from .position_base import PositionBase

class PositionData(PositionBase):
    def __init__(self, input_file, file_format='csv', latitude_prop='Latitude', longitude_prop='Longitude', crs="epsg:4326"):
        """
        Initialize the PositionData object with data from a CSV or GeoJSON file.
        Rows with NaN values in latitude or longitude are removed.

        :param input_file: Path to the CSV or GeoJSON file.
        :param file_format: The format of the input file ('csv' or 'geojson').
        :param latitude_prop: Name of the latitude column (default 'Latitude').
        :param longitude_prop: Name of the longitude column (default 'Longitude').
        :param crs: Coordinate reference system for the GeoDataFrame (default 'epsg:4326').
        """
        self.latitude_prop = latitude_prop
        self.longitude_prop = longitude_prop
        self.skyhub_columns = ['GAS:Methane', 'GAS:Status', 'AIR:Speed', 'AIR:Direction']

        if file_format == 'csv':
            # Read the CSV file using pandas
            df = pd.read_csv(input_file)

            # Remove rows with NaN in latitude or longitude
            df = df.dropna(subset=[latitude_prop, longitude_prop])

            # Create a GeoSeries from the latitude and longitude columns
            geometry = gpd.GeoSeries([Point(xy) for xy in zip(df[longitude_prop], df[latitude_prop])])

            # Convert the DataFrame to a GeoDataFrame
            self.data = gpd.GeoDataFrame(df, geometry=geometry, crs=crs)

        elif file_format == 'geojson':
            # Read the GeoJSON file
            self.data = gpd.read_file(input_file)

            # Remove rows with NaN in geometry (latitude or longitude)
            self.data = self.data.dropna(subset=['geometry'])

        else:
            raise ValueError("Invalid file format. Only 'csv' and 'geojson' are supported.")

    def _init_new_instance(self, data):
        """
        Create new instance of PositionData and transfer mandatory properties

        :param data: dataframe
        :return: A new instance of PositionData
        """        
        instance = PositionData.__new__(PositionData)
        instance.data = data
        instance.latitude_prop = self.latitude_prop
        instance.longitude_prop = self.longitude_prop
        instance.skyhub_columns = self.skyhub_columns
        return instance

    def clean_nan(self, columns):
        """
        Clean the data by removing rows with NaN values in the specified columns.

        :param columns: A list of column names to check for NaN values.
        :return: A new instance of PositionData with the cleaned data.
        """
        if not isinstance(columns, list):
            raise ValueError("columns must be a list of column names")

        cleaned_df = self.data.dropna(subset=columns)

        return self._init_new_instance(cleaned_df)
            
    def shape(self):
        """
        :return: shape of the data
        """
        return self.data.shape
    
    def filter_range(self, column_name, min, max):
        """
        Filter the data by column value.

        :param column_name: Name of the column.
        :param min: Minimum value or None.
        :param max: Maximum value or None.

        :return: New instance of PositionData with filtered data.
        """
        if min is None and max is None:
            return self  # No filtering required, return the original instance

        if min is None:
            filtered_data = self.data[self.data[column_name].astype(float) <= max]
        elif max is None:
            filtered_data = self.data[self.data[column_name].astype(float) >= min]
        else:
            filtered_data = self.data[
                (self.data[column_name].astype(float) >= min) & 
                (self.data[column_name].astype(float) <= max)
            ]

        return self._init_new_instance(filtered_data)
    
    def clip_by_polygon(self, clip_polygon_geojson):
        # Load the clip polygon into a GeoDataFrame
        clip_gdf = gpd.read_file(clip_polygon_geojson)

        # Store the original order
        self.data['original_order'] = range(len(self.data))

        # Clip the internal data with the provided polygon
        clipped_gdf = gpd.clip(self.data, clip_gdf)

        # Reorder based on the original order
        clipped_gdf = clipped_gdf.sort_values(by='original_order').drop(columns='original_order')

        self.data = self.data.drop(columns='original_order')

        # Create and return a new instance of PositionData with the clipped data
        return self._init_new_instance(clipped_gdf)

    def filter_noize(self, property_name, filter_type, window_size=3):
        """
        Apply a moving window filter to a property of the GeoDataFrame.

        :param property_name: Name of the property to calculate the moving statistic on.
        :param filter_type: Type of filter ('average' or 'median').
        :param window_size: Size of the moving window.

        :return: New instance of PositionData with updated data.
        """

        # Check if the property_name exists
        if property_name not in self.data.columns:
            raise ValueError(f"'{property_name}' does not exist in the GeoJSON properties.")
        
        # Convert the property to float where possible, and NaN where it's not possible
        self.data[property_name] = pd.to_numeric(self.data[property_name], errors='coerce')
        
        # Calculate the moving statistic based on user choice
        if filter_type == 'average':
            self.data[property_name] = self.data[property_name].rolling(window=window_size, min_periods=1).mean()
        elif filter_type == 'median':
            self.data[property_name] = self.data[property_name].rolling(window=window_size, min_periods=1).median()
        else:
            raise ValueError(f"Unsupported statistic type: {filter_type}")
        
        # Create a new instance of PositionData with the modified data
        return self._init_new_instance(self.data.copy(deep=True))
    
    def columns(self):
        """
        Returns an array of column names in the GeoDataFrame.

        :return: Array of column names.
        """
        # Check if data is not None
        if self.data is None:
            raise ValueError("Data is None. Cannot retrieve columns.")

        return self.data.columns.to_numpy()

    def statistics(self, column, bins=10):
        """
        Calculate and return statistics for a selected column, including probability distribution.

        Args:
        - column (str): The column for which statistics are to be calculated.
        - bins (int, optional): The number of bins to use for the probability distribution.

        Returns:
        - dict: A dictionary containing the statistics and probability distribution of the column.
        """
        # Check if the column exists in the dataframe
        if column not in self.data.columns:
            print(f"The column '{column}' does not exist in the data.")
            return None

        # Extract the data for the column
        column_data = self.data[column]

        # Calculate statistics
        stats = {
            'minimum': column_data.min(),
            'maximum': column_data.max(),
            'average': column_data.mean(),
            'median': column_data.median(),
            'std_deviation': column_data.std()
        }

        # Calculate histogram for the probability distribution
        counts, _ = np.histogram(column_data, bins=bins)
        probability_distribution = counts / counts.sum()

        stats['probability_distribution'] = probability_distribution.tolist()

        return stats    
    
    @staticmethod
    def get_azimuth(start_point, end_point):
        """
        Calculate azymuth between two points

        :param start_point: Starting point of a vector
        :param end_point: Ending point of a vector

        :return: angle between vector and north. CW direction is positive
        """
        longitudinalDifference = end_point[1] - start_point[1]
        latitudinalDifference = end_point[0] - start_point[0]

        if longitudinalDifference == 0:
            if latitudinalDifference > 0:
                return 0
            else:
                return 180

        azimuth = (math.pi * 0.5) - math.atan(latitudinalDifference / longitudinalDifference)
        
        if longitudinalDifference > 0:
            return math.degrees(azimuth)
        elif longitudinalDifference < 0:
            return math.degrees(azimuth + math.pi)

        return 0.0
    
    def calculate_direction(self, direction_property):
        """
        Calculate the direction between consecutive points and store it in a specified property.

        :param direction_property: Name of the target direction property in the resulting GeoDataFrame.

        :return: New instance of PositionData with direction data.
        """
        directions = []

        # Iterate over the rows, stopping before the last row
        for idx in range(len(self.data) - 1):
            row = self.data.iloc[idx]
            geom = row.geometry

            if geom is not None and geom.geom_type == 'Point' and not geom.is_empty:
                next_row = self.data.iloc[idx + 1]
                next_geom = next_row.geometry

                if next_geom is not None and next_geom.geom_type == 'Point' and not next_geom.is_empty:
                    start_point = (geom.y, geom.x)
                    end_point = (next_geom.y, next_geom.x)
                    angle = self.get_azimuth(start_point, end_point)
                    directions.append(angle)
                else:
                    directions.append(None)
            else:
                directions.append(None)

        # Append a default value (e.g., 0 or None) for the last point
        directions.append(None)  # or some default value

        # Create a new instance of PositionData with direction data
        result = self._init_new_instance(self.data.copy(deep=True))
        result.data[direction_property] = directions
        return result
    
    def export_as_geojson(self, output_path):
        """
        Export the data as a GeoJSON file.

        :param output_path: Path to save the GeoJSON file.
        """
        self._export_as_geojson(self.data, output_path)

    def export_as_csv(self, output_path):
        """
        Export the data as a CSV file.

        :param output_path: Path to save the GeoJSON file.
        """
        self._export_as_csv(self.data, output_path)

    [staticmethod]
    def calculate_ground_coordinates(row, altitude, earth_radius=6371000):  # Earth radius in meters
        # Convert latitude, longitude, and angles from degrees to radians
        lat_rad = math.radians(row['Latitude'])
        lon_rad = math.radians(row['Longitude'])
        pitch_rad = math.radians(row['Pitch'])  # Inclination from the vertical
        roll_rad = math.radians(row['Roll'])    # Tilt from the vertical
        yaw_rad = math.radians(row['Yaw'])      # Orientation relative to the north

        # Calculate the direction vector of the laser beam in 3D space
        # Assuming pitch and roll angles tilt the beam away from the downward vertical
        # And yaw rotates this tilted beam around the vertical axis
        # These calculations can be complex and depend on how pitch, roll, and yaw are defined
        # The following is a simplification for illustration purposes
        dx = math.sin(pitch_rad) * math.cos(yaw_rad) + math.sin(roll_rad) * math.sin(yaw_rad)
        dy = math.sin(pitch_rad) * math.sin(yaw_rad) - math.sin(roll_rad) * math.cos(yaw_rad)
        dz = -math.cos(pitch_rad) * math.cos(roll_rad)  # Negative as pointing downward

        # Normalize the direction vector
        length = math.sqrt(dx*dx + dy*dy + dz*dz)
        dx /= length
        dy /= length
        dz /= length

        # Calculate the horizontal distance based on altitude and direction
        horizontal_distance = altitude / -dz

        # Calculate the change in latitude and longitude
        delta_lat = horizontal_distance * dy / earth_radius
        delta_lon = horizontal_distance * dx / (earth_radius * math.cos(lat_rad))

        # Convert back to degrees
        delta_lat_deg = math.degrees(delta_lat)
        delta_lon_deg = math.degrees(delta_lon)

        # Calculate new latitude and longitude
        new_lat = row['Latitude'] + delta_lat_deg
        new_lon = row['Longitude'] + delta_lon_deg

        return new_lat, new_lon  # Return a tuple
    
    def convert_to_ground_coordinates(self, altitude_above_ground):
        """
        Convert sensor coordinates to actual methane spot on the ground.

        :param altitude_above_ground: Altitude of the sensor above the ground.
        :return: A new instance of PositionData with converted coordinates.
        """

        # Check if CRS is EPSG:4326, return the current instance if not
        if self.data.crs.to_string() != 'EPSG:4326':
            return self

        # Apply the calculation to each row
        new_coords = self.data.apply(lambda row: PositionData.calculate_ground_coordinates(row, altitude_above_ground), axis=1)
        new_latitudes, new_longitudes = zip(*new_coords)

        # Create a new GeoDataFrame with updated latitude, longitude, and geometry
        new_data = self.data.copy()
        new_data['Latitude'] = new_latitudes
        new_data['Longitude'] = new_longitudes
        new_data['geometry'] = [Point(lon, lat) for lon, lat in zip(new_longitudes, new_latitudes)]

        # Create a new PositionData instance with the updated data
        return self._init_new_instance(gpd.GeoDataFrame(new_data, crs=self.data.crs))

    def deduplicate_skyhub_data(self):
        """
        Deduplicate the data based on the specified columns.

        :return: A new instance of PositionData with deduplicated data.
        """

        # List of potential columns for deduplication
        potential_columns = self.skyhub_columns
        potential_columns.extend([self.latitude_prop, self.longitude_prop])

        # Filter out columns that are not in self.data.columns
        columns_to_use = [col for col in potential_columns if col in self.data.columns]

        # Deduplicate the data
        deduplicated_df = self.data.drop_duplicates(subset=columns_to_use)

        # Create a new instance of PositionData with deduplicated data
        return self._init_new_instance(deduplicated_df)
    
    def cut_useless_skyhub_columns(self):
        """
        Keep only the columns specified in self.skyhub_columns and the 'geometry' column,
        provided they exist in self.data.columns.

        :return: A new instance of PositionData with the updated data.
        """
        # Check if self.skyhub_columns is a list
        if not isinstance(self.skyhub_columns, list):
            raise ValueError("skyhub_columns must be a list of column names")

        # Filter columns that actually exist in self.data.columns and ensure 'geometry' is included
        columns_to_keep = [col for col in self.skyhub_columns if col in self.data.columns]
        if 'geometry' not in columns_to_keep:
            columns_to_keep.append('geometry')

        # Select only the specified columns
        updated_df = self.data[columns_to_keep]

        # Create a new instance of PositionData with the updated data
        return self._init_new_instance(updated_df)