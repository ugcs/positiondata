import shutil
import tempfile
import unittest
import os
from PositionData.position_data import PositionData  # Import your PositionData class
from PositionData.methane_data import MethaneData  # Import your MethaneData class

class TestMethaneData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load PositionData from a CSV file
        cls.position_data = PositionData("tests/data/methane/2023-12-07-flight1.csv")

        # Clip by a GeoJSON polygon (adjust the path to your GeoJSON file)
        cls.clipped_position_data = cls.position_data.clip_by_polygon("tests/data/methane/area-2023-12-07-flight1.geojson")

        # create temp dir
        cls.temp_dir = tempfile.mkdtemp() 
        cls.methane_map = os.path.join(cls.temp_dir, 'methane_map.tif')
        cls.deduplicated_methane_map = os.path.join(cls.temp_dir, 'deduplicated_methane_map.tif')
        cls.clean_temp = True
        print("Methane temp: ", cls.temp_dir)

    def test_clipped_methane_data_tiff_creation(self):
        # Create a MethaneData instance
        methane_data = MethaneData(self.clipped_position_data)

        # Call the map_methane method
        methane_data.map_methane(self.methane_map, '32635')

        # Check if TIFF file is created
        self.assertTrue(os.path.exists(self.methane_map))

    def test_deduplicated_methane_data_tiff_creation(self):
        # Create a MethaneData instance
        methane_data = MethaneData(self.clipped_position_data.deduplicate_skyhub_data().cut_useless_skyhub_columns())

        # Call the map_methane method
        methane_data.map_methane(self.deduplicated_methane_map, '32635')

        # Check if TIFF file is created
        self.assertTrue(os.path.exists(self.deduplicated_methane_map))

    def test_methane_data_tiff_creation(self):
        # Create a MethaneData instance
        methane_data = MethaneData(self.position_data)

        # Call the map_methane method
        methane_data.map_methane(self.methane_map, '32635')

        # Check if TIFF file is created
        self.assertTrue(os.path.exists(self.methane_map))
    
    @classmethod
    def tearDownClass(cls):
        # Remove the temporary directory
        if os.path.exists(cls.temp_dir) and cls.clean_temp:
            shutil.rmtree(cls.temp_dir)

if __name__ == '__main__':
    unittest.main()
