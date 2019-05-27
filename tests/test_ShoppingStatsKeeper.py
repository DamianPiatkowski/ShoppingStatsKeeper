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

        self.maxDiff = None

        self.data = {
            "weekly": {        
                "April 2019": [[123, 23, 23], [456, 23, 34], [123, 0, 23]],
                "May 2019": [[145, 23, 23], [1, 2, 3]]
            }, 
            "average": {
                "January 2019": [120, 55, 44, 600], 'February 2019': [240, 88, 99, 900], 
                'March 2019': [455, 12, 34, 1600], 'April 2019': [700, 23, 34, 2000]
            }
        }
        
        self.short_data = {"weekly": {"April 2019": [[123, 23, 23], [200, 50, 60]]}}

        self.settings = {"currency": "PLN", "vegetarian?": "no", "goal": "800"}

        self.short_message = (             
            "Ready for statistics?\nThere were 2 shopping "
            "days last month.\nYou spent 323 PLN in total. "
            "Your goal is to spend no more than 500, so congrats."
            "\nOn average you spent 162 PLN a week, 37 on meat and 47 on "
            "extra items.\nWhen there is enough data, I will tell "
            "you how the reported month compares to the average of "
            "the three previous ones.\nStay tuned."
        )

        self.long_message = (
            "Ready for some statistics? There were 3 shopping days "
            "last month.\nThis is how last month's expenses compare to "
            "the average of the previous 3 months..."
            "\nLast month's total average is 234 PLN, "
            "compared to 272 PLN "
            "in the previous months.\nMeat expenses: "
            "15 PLN last month and 52 PLN in the previous 3 months."
            "\nYou spent on average 27 PLN a week on extra items, "
            "59 PLN in the compared period."
            "\nIn total you spent 702 last month. "
            "In March 2019 it was 1600. "
            "Your goal is to spend no more than 500. So "
            "better luck next time."
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
    
    @freeze_time("2019-05-08")
    def test_do_statistics_messages(self):
        
        ShoppingStatsKeeper.do_statistics("no", "PLN", "500", self.data, datetime.date.today())
        self.assertEqual(ShoppingStatsKeeper.msg_content, self.long_message)
        
        ShoppingStatsKeeper.do_statistics("no", "PLN", "500", self.short_data, datetime.date.today())
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
            json.dump({"weekly": {"April 2019": [[123, 12, 23]]}}, write_file)

        ShoppingStatsKeeper.save_to_json("test.json", self.data)
        with open('test.json') as f:
            data_from_saved_json = json.load(f)
        self.assertEqual(data_from_saved_json, self.data)
        self.addCleanup(os.remove, "test.json")    
   
    @freeze_time("2019-05-08")
    def test_save_new_entry(self):
        # "May 2019" already exists, so the new entry should only be appended
        result = ShoppingStatsKeeper.save_new_entry(datetime.date.today(), self.data, [1, 2, 3])
        print(result)
        self.assertEqual(
            result,
            {
                "weekly": {
                    "April 2019": [[123, 23, 23], [456, 23, 34], [123, 0, 23]], 
                           "May 2019": [[145, 23, 23], [1, 2, 3], [1, 2, 3]]
                },
                "average": {
                    "January 2019": [120, 55, 44, 600], "February 2019": [240, 88, 99, 900],
                            "March 2019": [455, 12, 34, 1600], "April 2019": [700, 23, 34, 2000]
                }
            }
        )   
                         
        # New entry, "May 2019" should be added
        result2 = ShoppingStatsKeeper.save_new_entry(datetime.date.today(), self.short_data, [1, 2, 3])
        self.assertEqual(
            result2,
            {
                "weekly": {
                    "April 2019": [[123, 23, 23], [200, 50, 60]],
                           "May 2019": [[1, 2, 3]]
                }
            }
        )
                
    def test_change_goal(self):
        with open("test_settings.json", "w") as write_file:
            json.dump(self.settings, write_file)
        with patch('builtins.input') as mocked_input:
            mocked_input.side_effect = ('no', '900')
            ShoppingStatsKeeper.change_goal('test_settings.json', self.settings)
        with open('test_settings.json') as f:
            settings_from_saved_json = json.load(f)  
            self.assertEqual(settings_from_saved_json, {"currency": "PLN", "vegetarian?": "no", "goal": '900'})

        #with patch('builtins.print') as mocked_print:
            #with patch('builtins.input') as mocked_input:
                #mocked_input.side_effect = 'whatever'
                #ShoppingStatsKeeper.change_goal('test_settings.json', self.settings)
                #mocked_print.assert_called_with("Oops, something went wrong. Try again with 'yes' or 'no'")

        self.addCleanup(os.remove, 'test_settings.json')
                                                                                                           
if __name__ == '__main__':
    unittest.main()
