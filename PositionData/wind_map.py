import math
from PositionData import PositionData

class WindMap:
    def __init__(self, position_data,air_speed_prop, air_dir_prop, platform_speed_prop, platform_dir_prop, true_speed_prop, true_dir_prop):
        """
        Initialize the WindMap with an instance of PositionData.

        :param position_data: An instance of PositionData.
        :param air_speed_prop: Property name for air speed.
        :param air_dir_prop: Property name for air direction.
        :param platform_speed_prop: Property name for platform speed.
        :param platform_dir_prop: Property name for platform direction.
        :param true_speed_prop: Property name for true wind speed.
        :param true_dir_prop: Property name for true wind direction.
        """
        if not isinstance(position_data, PositionData):
            raise ValueError("position_data must be an instance of PositionData")
        
        # process true wind columns
        self.position_data = self._true_wind(position_data, air_speed_prop, air_dir_prop, platform_speed_prop, platform_dir_prop, true_speed_prop, true_dir_prop)
    
    def _true_wind(self, position_data, air_speed_prop, air_dir_prop, platform_speed_prop, platform_dir_prop, true_speed_prop, true_dir_prop):
        """
        Calculate the true wind speed and direction based on platform and measured wind data.

        :param air_speed_prop: Property name for air speed.
        :param air_dir_prop: Property name for air direction.
        :param platform_speed_prop: Property name for platform speed.
        :param platform_dir_prop: Property name for platform direction.
        :param true_speed_prop: Property name for true wind speed.
        :param true_dir_prop: Property name for true wind direction.
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
