import os
import shutil
import tempfile
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
        cls.falcon2_data = PositionData("tests/data/methane/2023-12-07-flight2.csv")
        # Clip by a GeoJSON polygon (adjust the path to your GeoJSON file)
        cls.clipped_falcon2_data = cls.falcon2_data.clip_by_polygon("tests/data/methane/area-2023-12-07-flight2.geojson")
        cls.falcon2_column_methane = "GAS:Methane"
        cls.falcon2_methane_min = 350
        cls.falcon2_methane_max = 500
        cls.falcon2_filtered_rows = 106
        cls.falcon2_columns = 21
        cls.falcon2_deduplicated_rows = 23320

        # Create temp dir
        cls.temp_dir = tempfile.mkdtemp()
        cls.csv_path = os.path.join(cls.temp_dir, 'export.csv')
        cls.clean_temp = True  # Set to True to clean up temp directory after tests
        print("Position temp: ", cls.temp_dir)

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

    # Test export as csv
    def test_export_as_csv(self):
        self.falcon1_data.export_as_csv(self.csv_path)
        from_file = PositionData(self.csv_path)

        # Get the columns from both GeoDataFrames
        columns_from_file = from_file.columns()
        columns_from_falcon1 = self.falcon1_data.columns()

        # Check if the columns are equal
        self.assertEqual(list(columns_from_file), list(columns_from_falcon1))

        # Check if the shape is equal
        self.assertEqual(self.falcon1_data.shape(), from_file.shape())

    def test_defuplicate_skyhub_data(self):
        deduplicated = self.falcon2_data.deduplicate_skyhub_data()
        
        # Check if the columns are equal
        self.assertEqual(list(deduplicated.columns()), list(self.falcon2_data.columns()))
        
        #check row number
        self.assertEqual(deduplicated.shape(),(self.falcon2_deduplicated_rows, self.falcon2_columns))
    
    @classmethod
    def tearDownClass(cls):
        # Remove the temporary directory
        if os.path.exists(cls.temp_dir) and cls.clean_temp:
            shutil.rmtree(cls.temp_dir)


if __name__ == '__main__':
    unittest.main()
