# A Python CLI program collecting statistics of the user's shopping spending and storing them in a json file.

In the beginning of each month it summarizes the stats of the previous one and sends an email report message. It does comparisions with the combined previous 3 months' average values if there is enough data in the json.

For example: after collecting new data for a first entry of May, the program summarizes April and creates a message like the following:

*"Ready for statistics?
There were 5 shopping days last month.
You spent 323 PLN in total. Your goal is to spend no more than 500, so congrats.
On average you spent 162 PLN a week, 37 on meat and 47 on extra items.
When there is enough data, I will tell you how the reported month compares to the average of 
the three previous ones.
Stay tuned."*

And if there are already entries in the json file for the months of January, February and March, the message would look like this:

*"Ready for some statistics? There were 3 shopping days last month.
This is how last month's expenses compare to the average of the previous 3 months...
Last month's total average is 234 PLN, compared to 272 PLN in the previous months.
Meat expenses: 15 PLN last month and 52 PLN in the previous 3 months.
You spent on average 27 PLN a week on extra items, 59 PLN in the compared period.
In total you spent 702 last month. In March 2019 it was 1600. 
Your goal is to spend no more than 500. So better luck next time."*

There is some customization when the program is run the first time. It asks:
- whether the user is vegetarian
- what their maximum spending in a month goal is (and later uses it in the report message)
- what the user's currency is

**The app is tested using the Unittest framework.**

