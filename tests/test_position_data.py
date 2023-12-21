import unittest
from PositionData.position_data import PositionData  

class TestPositionData(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize with a sample methane dataset
        cls.falcon1_data = PositionData('tests/data/methane/falcon1.csv')
        cls.falcon1_rows = 28
        cls.falcon1_columns = 21
        cls.falcon1_rows_nan = 3
        cls.falcon1_column_w_nan = "GAS:Methane"

        # Initialize with a sample wind data
        cls.wind1_data = PositionData('tests/data/wind/wind-trajectory1.csv')
        cls.wind1_clipped_rows = 5156
        cls.wind1_clipped_columns = 19
        cls.wind1_polygon_path = 'tests/data/wind/big-area.json'
        cls.wind1_platform_direction_column = "Direction"

        # Load PositionData from a CSV file
        cls.falcon2_data = PositionData("tests/data/methane/2023-12-07-10-55-42-position.csv")
        # Clip by a GeoJSON polygon (adjust the path to your GeoJSON file)
        cls.clipped_falcon2_data = cls.falcon2_data.clip_by_polygon("tests/data/methane/area-2023-12-07.geojson")
        cls.falcon2_column_methane = "GAS:Methane"
        cls.falcon2_methane_min = 350
        cls.falcon2_methane_max = 500
        cls.falcon2_filtered_rows = 106

    # Test shape
    def test_shape(self):
        shape = self.falcon1_data.shape()
        self.assertEqual(shape, (self.falcon1_rows, self.falcon1_columns)) 

    # Test cleaning rows with nans
    def test_clean_nan(self):
        cleaned = self.falcon1_data.clean_nan([self.falcon1_column_w_nan])
        shape = cleaned.shape()
        self.assertEqual(shape, (self.falcon1_rows - self.falcon1_rows_nan, self.falcon1_columns)) 

    # Test clipping by polygon
    def test_clip_by_polygon(self):
        clipped = self.wind1_data.clip_by_polygon(self.wind1_polygon_path)
        shape = clipped.shape()
        self.assertEqual(shape, (self.wind1_clipped_rows, self.wind1_clipped_columns)) 

    # Test direction 
    def test_calculate_direction(self):
        clipped = self.wind1_data.clip_by_polygon(self.wind1_polygon_path)
        direction = clipped.calculate_direction(self.wind1_platform_direction_column)
        self.assertTrue(self.wind1_platform_direction_column in direction.data.columns)

    # Test filter range
    def test_filter_range(self):
        filtered = self.clipped_falcon2_data.filter_range(self.falcon2_column_methane, self.falcon2_methane_min, self.falcon2_methane_max)
        self.assertEqual(filtered.shape()[0], self.falcon2_filtered_rows)


if __name__ == '__main__':
    unittest.main()

