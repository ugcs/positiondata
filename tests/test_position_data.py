import unittest
from PositionData.position_data import PositionData  

class TestPositionData(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Initialize with a sample dataset
        cls.position_data = PositionData('tests/data/methane/falcon1.csv')
        cls.falcon1_rows = 28
        cls.falcon1_columns = 21
        cls.falcon1_rows_nan = 3
        cls.falcon1_column_w_nan = "GAS:Methane"

    # Test shape
    def test_shape(self):
        shape = self.position_data.shape()
        self.assertEqual(shape, (self.falcon1_rows, self.falcon1_columns)) 

    # Test cleaning rows with nans
    def test_clean_nan(self):
        cleaned = self.position_data.clean_nan([self.falcon1_column_w_nan])
        shape = cleaned.shape()
        self.assertEqual(shape, (self.falcon1_rows - self.falcon1_rows_nan, self.falcon1_columns)) 

if __name__ == '__main__':
    unittest.main()

