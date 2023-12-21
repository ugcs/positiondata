import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import numpy as np
import os
import rasterio
from rasterio.transform import from_origin
from rasterio import warp
from scipy.interpolate import RBFInterpolator
import shutil
import tempfile
from scipy.interpolate import griddata
from rasterio.warp import calculate_default_transform, reproject, Resampling

class MethaneData:
    def __init__(self, position_data, methane_column = 'GAS:Methane', status_column = 'GAS:Status'):
        """
        Initialize the MethaneData object.

        :param position_data: An instance of PositionData.
        :param methane_column: Name of the column with methane readings.
        :param status_column: Name of the column with methane readings status.
        """
        self.position_data = position_data.clean_nan([methane_column, status_column])
        self.methane_column = methane_column
        self.status_column = status_column

    def map_methane(self, map_path, area_epsg, grid_rows=100, grid_columns=100, environment_methane_perc=75, ignore_invalid=True):
        """
        Generate a geotiff map of methane readings.

        :param map_path: Path to save the geotiff file.
                :param map_path: Path to save the geotiff file.
        :param grid_rows: Number of rows in the grid (default 100).
        :param grid_columns: Number of columns in the grid (default 100).
        :param environment_methane_perc: Percentage to use for environment methane threshold (default 75).
        :param ignore_invalid: Whether to ignore invalid readings (default True).
        """
        # Validate environment_methane
        if not 0 <= environment_methane_perc <= 100:
            raise ValueError("environment_methane must be between 0 and 100")

        if self.status_column not in self.position_data.data.columns:
            raise KeyError(f"'{self.status_column}' column not found in the data.")
        
        if self.methane_column not in self.position_data.data.columns:
            raise KeyError(f"'{self.methane_column}' column not found in the data.")
        
            # Filter data
        df = self.position_data.data
        if ignore_invalid:
            df = df[df[self.status_column].isin([1, 2])]

        # Calculate methane threshold
        threshold = np.percentile(df[self.methane_column], environment_methane_perc)
        df['adjusted_methane'] = df[self.methane_column] - threshold
        df['adjusted_methane'] = df['adjusted_methane'].clip(lower=0)

        # Check and handle CRS
        original_crs = self.position_data.data.crs
        if original_crs.is_geographic:
            df = df.to_crs(epsg=area_epsg)

        # Extract x and y coordinates
        df['x'] = df['geometry'].x
        df['y'] = df['geometry'].y

        # Coordinates and values for interpolation
        x, y = df.geometry.x, df.geometry.y
        z = df['adjusted_methane']

        # Create a grid
        xi = np.linspace(x.min(), x.max(), grid_columns)
        yi = np.linspace(y.min(), y.max(), grid_rows)
        X, Y = np.meshgrid(xi, yi)

        # Interpolate z values on the grid
        Z = griddata((x, y), z, (X, Y), method='cubic').astype('float32')

        Z = np.clip(Z, 0, None)

        xsize = (xi.max() - xi.min()) / Z.shape[1]
        ysize = (yi.min() - yi.max()) / Z.shape[0]  # Negative value
        transform = from_origin(xi.min(), yi.min(), xsize, ysize)

        # Set the desired NO_DATA value
        no_data_value = -9999  # You can set this to any value that makes sense for your data

        with rasterio.open(
            map_path,  # Output filename
            'w',
            driver='GTiff',
            height=Z.shape[0],
            width=Z.shape[1],
            count=1,
            dtype=Z.dtype,
            crs=df.crs,
            transform=transform,
            nodata=no_data_value  # Specify the NO_DATA value here
        ) as dst:
            # Before writing, replace NaNs (or other values) with the NO_DATA value
            Z_filled = np.where(np.isnan(Z), no_data_value, Z)
            dst.write(Z_filled, 1)