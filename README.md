# PositionData package
Python package for positional CSV data processing. Positional CSV is being generated by [SkyHub](https://www.sphengineering.com/integrated-systems/skyhub) - an onboard computer which records data from drone-based sensors, such as methane detectors, wind sensors, magnerometers, echo sounders and others with scalar georeferenced readings.   

Packase is maintained by [SPH Engineering](www.sphengineering.com) .

# Classes/Features
- [PositionData](#positiondata-class) - methods for loading data, filtering, clipping, export/import
- [WindData](#winddata-class) - true wind vector processing, wind rose generation

# Examples
## Wind Data Processing Example

This example demonstrates how to process wind data using the `PositionData` and `WindData` classes. The steps include loading data from a CSV file, clipping by a polygon, calculating the platform direction, and generating a windrose.

```python
from PositionData import PositionData
from PositionData  import WindData

# Assuming 'data.csv' is your CSV file with wind data
position_data = PositionData('data.csv')
# Assuming 'clip_polygon.geojson' is your GeoJSON file with the clipping polygon
clipped_data = position_data.clip_by_polygon('clip_polygon.geojson')
# Calculate platform direction relative to north as a Direction column
data_with_direction = clipped_data.calculate_direction('Direction')
# Initialize wind data and generate true wind as TrueWindSpeed and TrueWindDirection
wind_data = WindData(clipped_data, 'Air:Speed', 'Air:Direction', 'Velocity', 'Direction', 'TrueWindSpeed', 'TrueWindDirection')
# Save the windrose plot as 'windrose.png'
wind_data.build_windrose('TrueWindSpeed', 'TrueWindDirection', 'windrose.png')
```

# Reference
## PositionData Class

The `PositionData` class is designed for handling and processing geospatial data from CSV or GeoJSON files. It provides methods for cleaning data, filtering, clipping, computing statistics, and more.

## Initialization
### `PositionData(input_file, file_format='csv', latitude_prop='Latitude', longitude_prop='Longitude', crs="epsg:4326")`
Initializes the `PositionData` object with data from a CSV or GeoJSON file.

#### Parameters:
- `input_file`: Path to the CSV or GeoJSON file.
- `file_format`: The format of the input file ('csv' or 'geojson').
- `latitude_prop`: Name of the latitude column (default 'Latitude').
- `longitude_prop`: Name of the longitude column (default 'Longitude').
- `crs`: Coordinate reference system for the GeoDataFrame (default 'epsg:4326').

#### Example:
```python
position_data = PositionData("data.csv")
```

## Methods

### `clean_nan(columns)`
Cleans the data by removing rows with NaN values in the specified columns. This method is useful for ensuring data quality and integrity.

#### Parameters:
- `columns`: A list of column names to check for NaN values.

#### Example:
```python
# Assuming position_data is an instance of PositionData
cleaned_data = position_data.clean_nan(['Latitude', 'Longitude'])
```

### `shape()`
Returns the shape of the data, which includes the number of rows and columns in the GeoDataFrame. This method is essential for understanding the dimensions of your dataset.

#### Example:
```python
# Assuming position_data is an instance of PositionData
data_shape = position_data.shape()
print("Number of rows and columns:", data_shape)
```

### `filter_range(column_name, min, max)`
Filters the data by column value within a specified range. This method is particularly useful for narrowing down the dataset to a specific range of values in a given column, which can be essential for focused analysis or data visualization.

#### Parameters:
- `column_name`: Name of the column to apply the filter on.
- `min`: The minimum value of the range. If `None`, no lower limit is applied.
- `max`: The maximum value of the range. If `None`, no upper limit is applied.

#### Example:
```python
# Assuming position_data is an instance of PositionData
# Filter data where the values in 'Velocity' column are between 10 and 20
filtered_data = position_data.filter_range('Velocity', 10, 20)
print(filtered_data)
```
### `clip_by_polygon(clip_polygon_geojson)`
Clips the internal data to the boundaries of a provided polygon, as specified in a GeoJSON file. This method is useful for spatially subsetting the data to a specific geographic area, allowing for focused analysis within that area.

#### Parameters:
- `clip_polygon_geojson`: The path to the GeoJSON file containing the polygon against which the data will be clipped.

#### Example:
```python
# Assuming position_data is an instance of PositionData
# Clip the data using the boundaries defined in 'clip_polygon.geojson'
clipped_data = position_data.clip_by_polygon('clip_polygon.geojson')
print(clipped_data)
```
### `filter_noize(property_name, filter_type, window_size=3)`
Applies a moving window filter to a specified property of the GeoDataFrame. This method is useful for smoothing or reducing noise in the data, particularly in cases where the data contains fluctuations or irregularities that can obscure underlying trends or patterns.

#### Parameters:
- `property_name`: The name of the property (column) on which to apply the filter.
- `filter_type`: The type of filter to apply ('average' or 'median').
- `window_size`: The size of the moving window, defaulting to 3.

#### Example:
```python
# Assuming position_data is an instance of PositionData
# Apply a moving average filter with a window size of 5 to the 'Velocity' property
filtered_data = position_data.filter_noize('Velocity', 'average', 5)
print(filtered_data)
```
### `statistics(column, bins=10)`
Calculates and returns key statistics and a probability distribution for a selected column in the GeoDataFrame. This method is instrumental for understanding the distribution and central tendencies of data in a particular column, which is crucial for data analysis and decision-making.

#### Parameters:
- `column`: The name of the column for which statistics are to be calculated.
- `bins`: The number of bins to use for the probability distribution histogram, with a default value of 10.

#### Example:
```python
# Assuming position_data is an instance of PositionData
# Calculate statistics for the 'Velocity' column
velocity_stats = position_data.statistics('Velocity')
print(velocity_stats)
```
### `calculate_direction(direction_property)`
Calculates the direction between consecutive points in the GeoDataFrame and stores it in a specified property. This method is valuable for analyzing the directional trends in spatial data, such as determining the course of movement in tracking data or understanding directional patterns.

#### Parameters:
- `direction_property`: The name of the property (column) where the calculated direction values will be stored.

#### Example:
```python
# Assuming position_data is an instance of PositionData
# Calculate the direction between consecutive points and store in a new column 'Direction'
direction_data = position_data.calculate_direction('Direction')
print(direction_data)
```
### `export_as_geojson(self, output_path)`
Exports the current state of the GeoDataFrame to a GeoJSON file. This method is useful for saving processed or analyzed geospatial data in a standardized format, which can then be used in various GIS applications or further data analysis tools.

#### Parameters:
- `output_path`: The file path where the GeoJSON file will be saved.

#### Example:
```python
# Assuming position_data is an instance of PositionData
# Export the data to 'exported_data.geojson'
position_data.export_as_geojson('exported_data.geojson')
```
## WindData Class

The `WindData` class is designed for processing and analyzing wind data in a geospatial context. It includes methods for calculating true wind speed and direction, gridding measurements, and building windrose plots.

## Initialization
### `WindData(position_data, air_speed_prop, air_dir_prop, platform_speed_prop, platform_dir_prop, true_speed_prop, true_dir_prop, sensor_cw_rot=0, sensor_to_north=False)`
Initializes the `WindData` object with an instance of `PositionData` and properties related to wind and platform motion. it automatically calculates tru wind vectors. 

#### Parameters:
- `position_data`: An instance of `PositionData`.
- `air_speed_prop`: Property name for air speed.
- `air_dir_prop`: Property name for air direction.
- `platform_speed_prop`: Property name for platform speed.
- `platform_dir_prop`: Property name for platform direction.
- `true_speed_prop`: Property name for true wind speed.
- `true_dir_prop`: Property name for true wind direction.
- `sensor_cw_rot`: CW rotation of the sensor relative to the platform nose.
- `sensor_to_north`: If true, sensor readings are related to North; otherwise, relative to the platform nose.

#### Example:
```python
wind_data = WindData(position_data, 'Air:Speed', 'Air:Direction', 'Velocity', 'Direction', 'TrueWindSpeed', 'TrueWindDirection')
```
## Methods
### `build_windrose(speed_col, direction_col, output_path, bins=[0,2,4,6,8,10], nsector=16, title="Windrose")`
Builds and saves a windrose plot. This method is valuable for visually representing the distribution of wind speeds and directions, which is crucial in meteorological studies and applications such as sailing, aviation, and architecture.

#### Parameters:
- `speed_col`: Name of the wind speed column.
- `direction_col`: Name of the wind direction column.
- `output_path`: Path to save the generated windrose image.
- `bins`: Binning for wind speed (default is `[0,2,4,6,8,10]`).
- `nsector`: Number of sectors for the windrose (default is `16`).
- `title`: Title of the windrose plot (default is `"Windrose"`).

#### Example:
```python
# Assuming wind_data is an instance of WindData
wind_data.build_windrose('TrueWindSpeed', 'TrueWindDirection', 'windrose.png', bins=[0,2,4,6,8,10], nsector=16, title="Windrose")
```

### `grid_wind(speed_property, direction_property, method='linear', resolution=100)`
Creates a gridded representation of the wind measurements. This method is useful for visualizing and analyzing spatial variations in wind patterns, particularly in applications like meteorology, environmental monitoring, and renewable energy studies.

#### Parameters:
- `speed_property`: The name of the column representing wind speed.
- `direction_property`: The name of the column representing wind direction.
- `method`: The interpolation method for gridding (default is 'linear'). Other options are available as per `scipy.interpolate.griddata`.
- `resolution`: The resolution of the grid (default is `100`). Higher values provide finer grids.

#### Example:
```python
# Assuming wind_data is an instance of WindData
gridded_wind_data = wind_data.grid_wind('TrueWindSpeed', 'TrueWindDirection', method='linear', resolution=100)
```


