import datetime
from dateutil.relativedelta import relativedelta
from freezegun import freeze_time
import json
import os
import ShoppingStatsKeeper
import unittest
from unittest.mock import patch

class TestApp(unittest.TestCase):

    def setUp(self):
        self.data = {
            "weekly": {
                "April 2019": [[123, 23, 23], [456, 23, 34], [123, 0, 23]], 
                                "May 2019": [145, 23, 23]
            },
            "average": {
                "January 2019": [120, 55, 44, 600], "February 2019": [240, 88, 99, 900],
                            "March 2019": [455, 12, 34, 1600], "April 2019": [700, 23, 34, 2000]
            }
        }
        
        self.short_data = {"weekly": {"April 2019": [[123, 23, 23]]}}

        self.short_message = (             
            "Ready for statistics?\nThere were 3 shopping "
            "days this month.\nYou spent 702 PLN in total. "
            "Your goal is to spend no more than 500, so better luck next time."
            "\nOn average you spent 234 PLN a week, 15 on meat and 27 on "
            "extra items.\nWhen there is enough data, I will tell "
            "you how the current month compares to the average of "
            "the three previous ones.\nStay tuned."
        )

    def test_load_settings_existing(self):
        ShoppingStatsKeeper.load_settings('fixtures/test_existing_settings.json')

        self.assertEqual(ShoppingStatsKeeper.settings, {"currency": "PLN", "vegetarian?": "no", "goal": "500"})

    def test_load_settings_creating(self):
        with patch('builtins.input') as mocked_input:
            mocked_input.side_effect = ('PLN', 'yes', 'yes', '600')

            ShoppingStatsKeeper.load_settings('fixtures/test_not_existing_settings.json')

            self.assertTrue(os.path.exists('fixtures/test_not_existing_settings.json'))

            with open('fixtures/test_not_existing_settings.json') as t:
                testing = json.load(t)

            self.assertDictEqual(testing, {"currency": "PLN", "vegetarian?": "yes", "goal": '600'})

            self.addCleanup(os.remove, 'fixtures/test_not_existing_settings.json')

    @freeze_time("2019-05-08")
    def test_do_statistics_variables(self):
       
        ShoppingStatsKeeper.do_statistics("no", "PLN", "500", self.data, datetime.date.today())
        self.assertEqual(ShoppingStatsKeeper.onemonth_before, "March 2019")
        self.assertEqual(ShoppingStatsKeeper.twomonths_before, "February 2019")
        self.assertEqual(ShoppingStatsKeeper.threemonths_before, "January 2019")
        self.assertEqual(ShoppingStatsKeeper.report_month, "April 2019")
        self.assertEqual(ShoppingStatsKeeper.num_of_entries, 3)
        self.assertEqual(ShoppingStatsKeeper.stat_total, 702)
        self.assertEqual(ShoppingStatsKeeper.aver_total, 234)
        self.assertEqual(ShoppingStatsKeeper.aver_meat, 15)
        self.assertEqual(ShoppingStatsKeeper.aver_extra, 27)
        self.assertEqual(ShoppingStatsKeeper.data["average"][report_month], [234, 15, 27, 702])
        self.assertEqual(ShoppingStatsKeeper.msg_content, self.short_message)
    
    def test_prints_great(self):
        with patch('builtins.print') as mocked_print:
            with patch('builtins.input') as mocked_input:
                mocked_input.side_effect = (55, 23, 3, 'yes')

                ShoppingStatsKeeper.collect_data("no")

                mocked_print.assert_called_with("Great!")

    def test_creates_variable(self):

        with patch('builtins.input') as mocked_input:
            mocked_input.side_effect = (55, 23, 3, 'yes')

            ShoppingStatsKeeper.collect_data("no")

            self.assertEqual(ShoppingStatsKeeper.new, [55, 23, 3])
    
    def test_save_to_json(self):
        with open("test.json", "w") as write_file:
            json.dump({"weekly": {"April 2019": [123, 12, 23]}}, write_file)

        ShoppingStatsKeeper.save_to_json("test.json", self.data)
        with open('test.json') as f:
            data_from_saved_json = json.load(f)
        self.assertEqual(data_from_saved_json, self.data)
        self.addCleanup(os.remove, "test.json")    
   
    @freeze_time("2019-05-08")
    def test_save_new_entry(self):
        # "May 2019" already exists, so the new entry should only be appended
        ShoppingStatsKeeper.save_new_entry(datetime.date.today(), self.data, [1, 2, 3])
        self.assertEqual(
            ShoppingStatsKeeper.data, 
            {
                "weekly": {
                    "April 2019": [[123, 23, 23], [456, 23, 34], [123, 0, 23]], 
                           "May 2019": [[145, 23, 23], [1, 2, 3]]
                },
                "average": {
                    "January 2019": [120, 55, 44, 600], "February 2019": [240, 88, 99, 900],
                            "March 2019": [455, 12, 34, 1600], "April 2019": [700, 23, 34, 2000]
                }
            }
        )   
                         
        # New entry, "May 2019" should be added
        ShoppingStatsKeeper.save_new_entry(datetime.date.today(), self.short_data, [1, 2, 3])
        self.assertEqual(
            ShoppingStatsKeeper.data, 
            {"weekly": {"April 2019": [[123, 23, 23]], "May 2019": [[1, 2, 3]}}
        )
                
    def test_change_goal(self):
        with open("test_settings.json", "w") as write_file:
            json.dump({"currency": "PLN", "vegetarian?": "no", "goal": "500"}, write_file)   
        with patch('builtins.input') as mocked_input:
            mocked_input.side_effect = ('no', 800)                                                                                                   
            ShoppingStatsKeeper.change_goal(test_settings.json)
        with open('test_settings.json') as f:
            settings_from_saved_json = json.load(f)  
            self.assertEqual(settings_from_saved_json, {"currency": "PLN", "vegetarian?": "no", "goal": "800"})
        with patch('builtins.print') as mocked_print:                                                                                                   
            with patch('builtins.input') as mocked_input:
                mocked_input.side_effect = 'whatever'
                ShoppingStatsKeeper.change_goal(test_settings.json)
                mocked_print.assert_called_with("Oops, something went wrong. Try again with 'yes' or 'no'")                                                                                              
        self.addCleanup(os.remove, 'test_settings.json')   
                                                                                                           
if __name__ == '__main__':
    unittest.main()
