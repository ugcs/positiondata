import unittest
from PositionData import PositionData
from PositionData import Trajectory
import tempfile
import os
import shutil

class TestTrajectory(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create a mock PositionData instance
        # Assuming the PositionData class can be initialized with a CSV file path
        cls.position_data = PositionData('tests/data/methane/2023-12-07-flight1.csv').clean_nan(['Latitude', 'Longitude'])

        # Create temp dir
        cls.temp_dir = tempfile.mkdtemp()
        cls.trajectory_path = os.path.join(cls.temp_dir, 'flight1-traj.json')
        cls.clean_temp = True  # Set to True to clean up temp directory after tests
        print("Trajectory temp: ", cls.temp_dir)

    def test_initialization(self):
        trajectory = Trajectory(self.position_data, 'Date', 'Time', 2, 'EPSG:32635')
        self.assertIsInstance(trajectory, Trajectory)

    def test_duration_seconds(self):
        trajectory = Trajectory(self.position_data, 'Date', 'Time', 2, 'EPSG:32635')
        duration = trajectory.duration(unit='seconds')
        self.assertEqual(duration, 827.179)  # Adjust this expected value as needed

    def test_duration_minutes(self):
        trajectory = Trajectory(self.position_data, 'Date', 'Time', 2, 'EPSG:32635')
        duration = trajectory.duration(unit='minutes')
        self.assertEqual(round(duration), 14)  # Adjust this expected value as needed

    def test_polyline_generation(self):
        trajectory = Trajectory(self.position_data, 'Date', 'Time', 2, 'EPSG:32635')
        _, length = trajectory.polyline()
        self.assertEqual(round(length), 3069)  # Check that the length of the trajectory is greater than 0

    def test_export_to_geojson(self):
        trajectory = Trajectory(self.position_data, 'Date', 'Time', 2, 'EPSG:32635')
        gdf, _ = trajectory.polyline()
        gdf.to_file(self.trajectory_path, driver='GeoJSON')
        self.assertTrue(os.path.exists(self.trajectory_path))

    @classmethod
    def tearDownClass(cls):
        # Remove the temporary directory
        if os.path.exists(cls.temp_dir) and cls.clean_temp:
            shutil.rmtree(cls.temp_dir)

if __name__ == '__main__':
    unittest.main()
