import geopandas as gpd
from geopy.distance import geodesic
from windrose import WindroseAxes
import matplotlib.pyplot as plt
import math
import numpy as np
import pandas as pd
import rasterio
from rasterio.transform import from_origin
from shapely.geometry import Point, LineString, MultiLineString
from scipy.interpolate import griddata


class PositionData:
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
        
    def clean_nan(self, columns):
        """
        Clean the data by removing rows with NaN values in the specified columns.

        :param columns: A list of column names to check for NaN values.
        :return: A new instance of PositionData with the cleaned data.
        """
        if not isinstance(columns, list):
            raise ValueError("columns must be a list of column names")

        cleaned_df = self.data.dropna(subset=columns)

        # Create a new PositionData instance with the cleaned data
        cleaned_position_data = PositionData.__new__(PositionData)
        cleaned_position_data.data = cleaned_df

        return cleaned_position_data
            
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

        result = PositionData.__new__(PositionData)
        result.data = filtered_data
        return result
        

    def clip_by_polygon(self, clip_polygon_geojson):
        """
        Clip the internal data with a provided polygon GeoJSON.

        :param clip_polygon_geojson: Path to the GeoJSON file with the clipping polygon.

        :return: New instance of PositionData with clipped data.
        """
        # Load the clip polygon into a GeoDataFrame
        clip_gdf = gpd.read_file(clip_polygon_geojson)

        # Clip the internal data with the provided polygon
        clipped_gdf = gpd.clip(self.data, clip_gdf)

        # Create and return a new instance of PositionData with the clipped data
        result = PositionData.__new__(PositionData)
        result.data = clipped_gdf
        return result

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
        result = PositionData.__new__(PositionData)
        result.data = self.data.copy()
        return result

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
        counts, bin_edges = np.histogram(column_data, bins=bins)
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

        for idx, row in self.data.iterrows():
            geom = row.geometry
            if geom is not None and geom.geom_type == 'Point' and not row.geometry.is_empty:
                if idx == len(self.data) - 1:
                    directions.append(0)
                else:
                    next_row = self.data.iloc[idx + 1]
                    next_geom = next_row.geometry
                    if next_geom is not None and next_geom.geom_type == 'Point' and not next_row.geometry.is_empty:
                        start_point = (row.geometry.y, row.geometry.x)
                        end_point = (next_row.geometry.y, next_row.geometry.x)
                        angle = self.get_azimuth(start_point, end_point)
                        directions.append(angle)
                    else:
                        directions.append(None)
            else:
                directions.append(None)

        # Create a new instance of PositionData with direction data
        result = PositionData.__new__(PositionData)
        result.data = self.data.copy()
        result.data[direction_property] = directions
        return result
    
    def export_as_geojson(self, output_path):
        """
        Export the data as a GeoJSON file.

        :param output_path: Path to save the GeoJSON file.
        """
        self.data.to_file(output_path, driver="GeoJSON")

