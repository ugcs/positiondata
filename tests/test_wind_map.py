import unittest
from PositionData.position_data import PositionData
from PositionData.wind_data import WindData

class TestWindMap(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize with a sample wind data
        cls.wind1_clipped_rows = 5156
        cls.wind1_clipped_columns = 19
        cls.wind1_polygon_path = 'tests/data/wind/big-area.json'
        cls.wind1_grid_size = 100
        cls.wind1_grid_columns= 3
        cls.air_speed_prop = "AIR:Speed"
        cls.air_dir_prop = "AIR:Direction"
        cls.platform_speed_prop = "Velocity"
        cls.platform_dir_prop = "Direction"
        cls.true_speed_prop = "AIR:TrueSpeed"
        cls.true_dir_prop = "AIR:TrueDirection"
        cls.position_data_wind1 = PositionData('tests/data/wind/wind-trajectory1.csv').calculate_direction(cls.platform_dir_prop)

    # Test shape
    def test_grid_wind(self):
        wind_data = WindData(self.position_data_wind1, self.air_speed_prop, self.air_dir_prop, self.platform_speed_prop, self.platform_dir_prop,
                           self.true_speed_prop, self.true_dir_prop )
        gridded = wind_data.grid_wind(self.true_speed_prop, self.true_dir_prop)
        shape = gridded.shape()
        self.assertEqual(shape, (self.wind1_grid_size * self.wind1_grid_size, self.wind1_grid_columns)) 