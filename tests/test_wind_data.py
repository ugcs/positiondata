import unittest
from PositionData.position_data import PositionData
from PositionData.wind_data import WindData
import numpy as np
import os
import tempfile
import shutil

class TestWindData(unittest.TestCase):

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

        cls.position_data_wind2 = PositionData('tests/data/wind/true_wind_samples.csv')
        cls.reference_speed_prop = "Reference:TrueWindSpeed"
        cls.reference_direction_prop = "Reference:TrueWindDirection"

        cls.position_data_wind3 = PositionData('tests/data/wind/wind_rose1.csv')
        cls.position_data_wind4= PositionData('tests/data/wind/wind_rose2.csv')

        # create temp dir
        cls.temp_dir = tempfile.mkdtemp() 
        cls.wind_rose1_img = os.path.join(cls.temp_dir, 'wind_rose1.jpg')
        cls.wind_rose2_img = os.path.join(cls.temp_dir, 'wind_rose2.jpg')
        cls.clean_temp = True
        print("Wind temp: ", cls.temp_dir)
    
    @classmethod
    def tearDownClass(cls):
        # This is executed after each test
        # Remove the temporary directory
        if os.path.exists(cls.temp_dir) and cls.clean_temp:
            shutil.rmtree(cls.temp_dir)

    # Test shape
    def test_grid_wind(self):
        wind_data = WindData(self.position_data_wind1, self.air_speed_prop, self.air_dir_prop, self.platform_speed_prop, self.platform_dir_prop,
                           self.true_speed_prop, self.true_dir_prop )
        gridded = wind_data.grid_wind(self.true_speed_prop, self.true_dir_prop)
        shape = gridded.shape()
        self.assertEqual(shape, (self.wind1_grid_size * self.wind1_grid_size, self.wind1_grid_columns))

    # test true wind calculation
    def test_true_wind(self):
        true_wind_samples = WindData(self.position_data_wind2, self.air_speed_prop, self.air_dir_prop, self.platform_speed_prop, self.platform_dir_prop,
                           self.true_speed_prop, self.true_dir_prop)
        gdf = true_wind_samples.position_data.data
        tolerance = 0.001
        # speed mismatch
        # Use numpy.isclose for comparison with a tolerance
        speed_mismatching_rows = gdf[~np.isclose(gdf[self.reference_speed_prop], gdf[self.true_speed_prop], atol=tolerance)]

        if(speed_mismatching_rows.shape[0] > 0): 
            print(speed_mismatching_rows[[self.reference_speed_prop, self.true_speed_prop]])
        self.assertTrue(speed_mismatching_rows.shape[0] == 0)
        # direction mismatch
        # Define a tolerance level, e.g., 0.001 for very close matches
        direction_mismatching_rows = gdf[~np.isclose(gdf[self.reference_direction_prop], gdf[self.true_dir_prop], atol=tolerance)]
        if(direction_mismatching_rows.shape[0] > 0): 
            print(direction_mismatching_rows[[self.reference_direction_prop, self.true_dir_prop]])
        self.assertTrue(direction_mismatching_rows.shape[0] == 0)

    # wind rose: movement to north, headwind
    def test_wind_rose_north(self):
        wind_rose = WindData(self.position_data_wind3, self.air_speed_prop, self.air_dir_prop, self.platform_speed_prop, self.platform_dir_prop,
                           self.true_speed_prop, self.true_dir_prop)
        wind_rose.build_windrose(self.true_speed_prop, self.true_dir_prop, self.wind_rose1_img)
        self.assertTrue(os.path.exists(self.wind_rose1_img))

    # wind rose: movement to north, sw wind
    def test_wind_rose_sw(self):
        wind_rose = WindData(self.position_data_wind4, self.air_speed_prop, self.air_dir_prop, self.platform_speed_prop, self.platform_dir_prop,
                           self.true_speed_prop, self.true_dir_prop)
        wind_rose.build_windrose(self.true_speed_prop, self.true_dir_prop, self.wind_rose2_img)
        self.assertTrue(os.path.exists(self.wind_rose2_img))