import unittest
from unittest.mock import patch
import ShoppingStatsKeeper
from freezegun import freeze_time
import os
import datetime
import json
from dateutil.relativedelta import relativedelta


# https://stackoverflow.com/questions/33767627/python-write-unittest-for-console-print

class TestApp(unittest.TestCase):

    def test_load_settings_existing(self):
        ShoppingStatsKeeper.load_settings('fixtures/test_existing_settings.json')

        self.assertEqual(ShoppingStatsKeeper.settings, {"currency": "PLN", "vegetarian?": "no", "goal": "500"})

    def test_load_settings_creating(self):
        with patch('builtins.input') as mocked_input:
            mocked_input.side_effect = ('PLN', 'yes', 'yes', 600)

            ShoppingStatsKeeper.load_settings('fixtures/test_not_existing_settings.json')

            #self.assertEqual(
            #assert os.path.exists('fixtures/test_not_existing_settings.json'), True)

            self.assertTrue(os.path.exists('fixtures/test_not_existing_settings.json'))

            with open('fixtures/test_not_existing_settings.json') as t:
                testing = json.load(t)

            self.assertDictEqual(testing, {"currency": "PLN", "vegetarian?": "yes", "goal": 600})

            self.addCleanup(os.remove, 'fixtures/test_not_existing_settings.json')

    @freeze_time("2019-05-08")
    def test_do_statistics_variables(self):
        data = {"weekly": {"April 2019": [[123, 23, 23], [456, 23, 34], [123, 0, 23]], "May 2019": [145, 23, 23]},
                "average": {"January 2019": [120, 55, 44, 600], "February 2019": [240, 88, 99, 900],
                            "March 2019": [455, 12, 34, 1600], "April 2019": [700, 23, 34, 2000]}}

        ShoppingStatsKeeper.do_statistics("no", "PLN", "500", data, datetime.date.today())
        #self.assertEqual(ShoppingStatsKeeper.onemonth_before, "March 2019")
        #self.assertEqual(ShoppingStatsKeeper.twomonths_before, "February 2019")
        #self.assertEqual(ShoppingStatsKeeper.threemonths_before, "January 2019")
        self.assertEqual(ShoppingStatsKeeper.report_month, "April 2019")
        #self.assertEqual(ShoppingStatsKeeper.num_of_entries, 3)

    def test__prints_great(self):
        with patch('builtins.print') as mocked_print:
            with patch('builtins.input') as mocked_input:
                mocked_input.side_effect = (55, 23, 3, 'yes')

                ShoppingStatsKeeper.collect_data("no")

                mocked_print.assert_called_with("Great!")

    def test__creates_variable(self):

        with patch('builtins.input') as mocked_input:
            mocked_input.side_effect = (55, 23, 3, 'yes')

            ShoppingStatsKeeper.collect_data("no")

            self.assertEqual(ShoppingStatsKeeper.new, [55, 23, 3])


if __name__ == '__main__':
    unittest.main()