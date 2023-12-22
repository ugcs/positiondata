import unittest
from PositionData import PositionData
from PositionData import Trajectory
import geopandas as gpd
from shapely.geometry import Point
import tempfile
import os
import shutil

class TestTrajectory(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Create a mock PositionData instance
        cls.position_data = PositionData('tests/data/methane/2023-12-07-flight1.csv').clean_nan(['Latitude','Longitude'])

        # create temp dir
        cls.temp_dir = tempfile.mkdtemp() 
        cls.trajectory_path = os.path.join(cls.temp_dir, 'flight1-traj.json')
        cls.clean_temp = False
        print("Trajectory temp: ", cls.temp_dir)

    def test_initialization(self):
        trajectory = Trajectory(self.position_data, 'Date', 'Time')
        self.assertIsInstance(trajectory, Trajectory)

    def test_duration_seconds(self):
        trajectory = Trajectory(self.position_data, 'Date', 'Time')
        duration = trajectory.duration(unit='seconds')
        self.assertEqual(duration, 827.179)

    def test_duration_minutes(self):
        trajectory = Trajectory(self.position_data, 'Date', 'Time')
        duration = trajectory.duration(unit='minutes')
        self.assertEqual(round(duration), 14) 

    def test_polyline_generation(self):
        trajectory = Trajectory(self.position_data, 'Date', 'Time')
        trajectory.polyline(self.trajectory_path, 0.5, 'EPSG:32635')
        self.assertTrue(os.path.exists(self.trajectory_path))

    @classmethod
    def tearDownClass(cls):
        # Remove the temporary directory
        if os.path.exists(cls.temp_dir) and cls.clean_temp:
            shutil.rmtree(cls.temp_dir)

if __name__ == '__main__':
    unittest.main()
