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

        df.to_csv('D:\\Temp\\methane_data\\temp_methane_wgs84.csv', index = False)

        # Check and handle CRS
        original_crs = self.position_data.data.crs
        if original_crs.is_geographic:
            df = df.to_crs(epsg=area_epsg)

        # Extract x and y coordinates
        df['x'] = df['geometry'].x
        df['y'] = df['geometry'].y

        df.to_csv('D:\\Temp\\methane_data\\temp_methane_epsg{}.csv'.format(area_epsg), index = False)

        # Coordinates and values for interpolation
        x, y = df.geometry.x, df.geometry.y
        z = df['adjusted_methane']

        # DEBUG plot
        plt.figure(figsize=(10, 6))
        sc = plt.scatter(x, y, c=z, cmap='coolwarm', edgecolor='none')
        plt.colorbar(sc, label='Methane Concentration')
        plt.xlabel('X Coordinate')
        plt.ylabel('Y Coordinate')
        plt.title('Methane Concentration Scatter Plot')

        # Save the figure
        plt.savefig('D:\\Temp\\methane_data\\original_data_plot.jpg', format='jpeg', dpi=300)

        # Create a grid
        xi = np.linspace(x.min(), x.max(), 100)
        yi = np.linspace(y.min(), y.max(), 100)
        X, Y = np.meshgrid(xi, yi)

        # Interpolate z values on the grid
        Z = griddata((x, y), z, (X, Y), method='cubic').astype('float32')

        Z = np.clip(Z, 0, None)

        xsize = (xi.max() - xi.min()) / Z.shape[1]
        ysize = (yi.min() - yi.max()) / Z.shape[0]  # Negative value
        transform = from_origin(xi.min(), yi.min(), xsize, ysize)
        #transform = from_origin(xi.min(), yi.max(), (xi.max() - xi.min()) / Z.shape[1], (yi.max() - yi.min()) / Z.shape[0])
        utm_crs = "EPSG:xxxx"  # Replace xxxx with the correct UTM zone CRS

        # use temp dir
        temp_dir = tempfile.mkdtemp() 
        temp_map = os.path.join(temp_dir, 'methane_map.tif')
        temp_map = 'D:\\Temp\\methane_data\\temp_methane_map.tif'

        # Save the interpolated data as a GeoTIFF
        #transform = from_origin(xi[0][0], yi[0][0], abs(xi[0][1] - xi[0][0]), abs(yi[1][0] - yi[0][0]))

        #with rasterio.open(temp_map, 'w', driver='GTiff', height=Z.shape[0], width=Z.shape[1], count=1, dtype='float32', crs=df.crs, transform=transform) as dst:
        #    dst.write(Z.astype('float32'), 1)

        with rasterio.open(
            temp_map,  # UTM grid filename
            'w',
            driver='GTiff',
            height=Z.shape[0],
            width=Z.shape[1],
            count=1,
            dtype=Z.dtype,
            crs=df.crs,
            transform=transform
        ) as dst:
            dst.write(Z, 1)

        map_path = 'D:\\Temp\\methane_data\\methane_map.tif'

        with rasterio.open(temp_map) as src:
            transform, width, height = calculate_default_transform(
                src.crs, original_crs, src.width, src.height, *src.bounds)
            kwargs = src.meta.copy()
            kwargs.update({
                'crs': original_crs,
                'transform': transform,
                'width': width,
                'height': height
            })

            with rasterio.open(map_path, 'w', **kwargs) as dst:
                for i in range(1, src.count + 1):
                    reproject(
                        source=rasterio.band(src, i),
                        destination=rasterio.band(dst, i),
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=transform,
                        dst_crs=original_crs,
                        resampling=Resampling.nearest)

        # Plotting
        plt.figure(figsize=(10, 6))
        contour = plt.contourf(X, Y, Z, levels=100, cmap='coolwarm')
        plt.colorbar(contour, label='Methane Concentration')
        plt.xlabel('X Coordinate')
        plt.ylabel('Y Coordinate')
        plt.title('Methane Concentration Contour Plot')

        # Save the figure
        plt.savefig('D:\\Temp\\methane_data\\original_data_grid.jpg', format='jpeg', dpi=300)
                
        # clean temp directory
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)