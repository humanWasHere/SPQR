import unittest
# from unittest.mock import MagicMock
from ..app.hss_modules.dataframe_to_eps_data import DataFrameToEPSData
import pandas as pd


class TestHssCreator(unittest.TestCase):

    def setUp(self):
        self.creator = DataFrameToEPSData()
        self.eps_data = pd.DataFrame({'EPS': [1.0, 2.0, 3.0], 'Year': [2018, 2019, 2020]})
        self.creator.eps_data = self.eps_data

    def test_get_eps_data(self):
        # Test that the function returns the correct dataframe
        result = self.creator.get_eps_data()
        self.assertEqual(result.equals(self.eps_data), True)


if __name__ == '__main__':
    unittest.main()
