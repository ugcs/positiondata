import unittest
from PositionData.position_data import PositionData  

class TestPositionData(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize with a sample methane dataset
        cls.position_data_methane = PositionData('tests/data/methane/falcon1.csv')
        cls.falcon1_rows = 28
        cls.falcon1_columns = 21
        cls.falcon1_rows_nan = 3
        cls.falcon1_column_w_nan = "GAS:Methane"

        # Initialize with a sample wind data
        cls.position_data_wind1 = PositionData('tests/data/wind/wind-trajectory1.csv')
        cls.wind1_clipped_rows = 5156
        cls.wind1_clipped_columns = 19
        cls.wind1_polygon_path = 'tests/data/wind/big-area.json'

    # Test shape
    def test_shape(self):
        shape = self.position_data_methane.shape()
        self.assertEqual(shape, (self.falcon1_rows, self.falcon1_columns)) 

    # Test cleaning rows with nans
    def test_clean_nan(self):
        cleaned = self.position_data_methane.clean_nan([self.falcon1_column_w_nan])
        shape = cleaned.shape()
        self.assertEqual(shape, (self.falcon1_rows - self.falcon1_rows_nan, self.falcon1_columns)) 

    # Test clipping by polygon
    def test_clip_by_polygon(self):
        clipped = self.position_data_wind1.clip_by_polygon(self.wind1_polygon_path)
        shape = clipped.shape()
        self.assertEqual(shape, (self.wind1_clipped_rows, self.wind1_clipped_columns)) 


if __name__ == '__main__':
    unittest.main()

