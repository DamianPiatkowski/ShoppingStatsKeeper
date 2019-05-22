import datetime
from dateutil.relativedelta import relativedelta
from email.message import EmailMessage
import json
import os
import smtplib
#import matplotlib.pyplot as plt
#import matplotlib.rcsetup as rcsetup
#import matplotlib

WELCOME = """
Hello there!
You went shopping, didn't you?
I will need some numbers now.
"""

EMAIL_ADDRESS = os.environ.get('EMAIL_USER')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASS')


def main():
  today = datetime.date.today()
  
  load_settings('settings.json')
  print(WELCOME)

  collect_data(settings["vegetarian?"])
  load_json()
  save_new_entry(today, data, new)

  if len(data["weekly"][today.strftime("%B %Y")]) == 1 and len(data["weekly"]) > 1:
      do_statistics(
          settings["vegetarian?"], settings["currency"], settings["goal"], data, today
      )
  #make_graph()
  send_email(today)
  save_to_json('data.json', data)
  change_goal('settings.json')

  input("Hit the enter to exit. Thanks!")


def load_settings(json_file):
    """If it's the first time the program is run, 
    create a json to store the settings.
    Otherwise, just load them from the already existing json.
    """
    global settings

    try:
        with open(json_file) as f:
            settings = json.load(f)

    except FileNotFoundError:
        settings = {}
        while True:
            settings["currency"] = input("What's your currency?")
            
            confirmation = input(
                "Your currency is {}, correct?".format(settings["currency"])
            )
            if confirmation.lower() == "yes":
                break
            else:
                print("Oops! Try again")

        while True:
            settings["vegetarian?"] = input("Are you a vegetarian?")
            if settings["vegetarian?"].lower() in ["yes", "no"]:
                break
            else:
                print("Invalid input, only 'Yes' or 'No' please, try again!")

        while True:
            settings["goal"] = input(
                "What's the maximum amount you want to spend monthly on shopping?"
            )

            if settings["goal"].isdigit() == True:
                break
            else:
                print("Oops! I need a number, try again")

        with open(json_file, 'w') as f:
            json.dump(settings, f)


def collect_data(veg):
    """Ask three questions, make sure that the input is correct.
    Assign a list of three answers to a variable 'new'.
    """

    global new
    meat = 0

    while True:

        while True:
            try:
                total = int(input("What was the total spent today? "))
                break

            except ValueError:
                print("Oops! It wasn't a valid number, please try again.")

        if veg.lower() == "no":
            while True:
                try:
                    meat = int(input("How much did you spend on meat today? "))
                    if meat == 0:
                        print("Going vegeterian are you?")

                    elif meat > 50:
                        print("You promised to eat less meat, didn't you?")
                    break

                except ValueError:
                    print("Oops! It wasn't a valid number, please try again.")

        while True:
            try:
                extra = int(input("And how much was spent on extra items? "))
                break

            except ValueError:
                print("Oops! It wasn't a valid number, please try again.")

        while True:

            if veg.lower() == "no":
                is_correct = input(
                    "You spent {} PLN in total,"
                                   "\n{} PLN on meat and {} PLN on extra items. Is that correct?"
                                   "\nEnter Yes or No. ".format(str(total), str(meat), str(extra))
                )
            else:
                is_correct = input(
                    "You spent {} PLN in total,"
                                   "\nand {} PLN was on extra items. Is that correct?"
                                   "\nEnter Yes or No. ".format(str(total), str(extra))
                )

            if is_correct.lower() in ["yes", "no"]:
                break

            else:
                print("Invalid input, try again!")

        if is_correct.lower() == "yes":
            print("Great!")
            break

        else:
            print("Let's start over then")

    new = [total, meat, extra]


def load_json():
    """Load the json file.
    If it's the first time the program is used, create a new json file.
    The dictionary 'data' has two keys: 'weekly' is for storing weekly
    statistics for each month. 'average' key is used for memoization of average
    monthly values. Lists (only one a month) in "average" have 4 values:
    average total sum spent every week, average meat and extra items expenses
    and the total of money spent in the month.
    """
    try:
        with open('data.json') as f:
            global data
            data = json.load(f)

    except FileNotFoundError:
        data = {"weekly": {}, "average": {}}
        with open('data.json', 'w') as f:
            json.dump(data, f)


def save_to_json(json_file, updated_dict):
    """Save the updated dictionary to the json file."""
    with open(json_file, 'w') as f:
        json.dump(updated_dict, f)
        
def save_new_entry(date, data, new_entry):
    """Display the date in the format 'month year'.
    Create a new list for this month if it's the first shopping of the month,
    otherwise append this month's list with the new entry.
    The new entry is stored as a list in the variable 'new'.
    """

    if date.strftime("%B %Y") in data["weekly"]:
        data["weekly"][date.strftime("%B %Y")].append(new_entry)
        #return data #tests were failing to recognise this variable when there is no return
    else:
        data["weekly"][date.strftime("%B %Y")] = [new_entry]
        #return data

def do_statistics(veg, curr, g, data, date):
    """
    Compare this month's average to the average of the 3 previous months.
    If there are not enough records, display the shorter information, otherwise
    show the longer version.
    a = average total of the last 3 months
    b = average meat expenses
    c = average extra items expenses
    """

    global onemonth_before, twomonths_before, threemonths_before, report_month, msg_content, num_of_entries

    report_month = (date - relativedelta(months=1)).strftime("%B %Y")

    num_of_entries = len(data["weekly"][report_month])

    onemonth_before = (date - relativedelta(months=2)).strftime("%B %Y")

    twomonths_before = (date - relativedelta(months=3)).strftime("%B %Y")

    threemonths_before = (date - relativedelta(months=4)).strftime("%B %Y")                          

    stat_total = 0
    stat_meat = 0
    stat_extra = 0

    for item in data["weekly"][report_month]:
        stat_total += item[0]
        stat_meat += item[1]
        stat_extra += item[2]

    aver_total = stat_total / num_of_entries
    aver_meat = stat_meat / num_of_entries
    aver_extra = stat_extra / num_of_entries

    data["average"][report_month] = [
        aver_total, aver_meat, aver_extra, stat_total
    ]

    try:
        a = (data['average'][onemonth_before][0] +
             data['average'][twomonths_before][0] +
             data['average'][threemonths_before][0]) / 3

        b = (data['average'][onemonth_before][1] +
             data['average'][twomonths_before][1] +
             data['average'][threemonths_before][1]) / 3

        c = (data['average'][onemonth_before][2] +
             data['average'][twomonths_before][2] +
             data['average'][threemonths_before][2]) / 3

        msg_content = (
            f"Ready for some statistics? There were {str(num_of_entries)} "
            "shopping days "
            f"this month.\nThis is how this month's expenses compare to "
            f"the average of the previous 3 months..."
            f"\nThis month's total average is {str(aver_total)} {curr}, "
            f"compared to {str(a)} {curr} "
            f"in the previous months.\nMeat expenses: "
            f"{str(aver_meat)} {curr} this month "
            f"and {str(b)} {curr} in the previous 3 months."
            f"\nYou spent on average {str(aver_extra)} {curr} a week on extra items, "
            f"{str(c)} {curr} in the compared period."
            f"\nIn total you spent {str(stat_total)} this month. "
            f"In {onemonth_before} it was {str(data['average'][onemonth_before][3])}. "
            f"Your goal is to spend no more than {g}. So "
            f"{'congrats' if stat_total <= int(g) else 'better luck next time.'}"
        )

        print(msg_content)

    except KeyError:
        msg_content = (
            f"Ready for statistics?\nThere were {str(num_of_entries)} shopping "
            f"days this month.\nYou spent {str(stat_total)} {curr} in total. "
            f"Your goal is to spend no more than {g}, "
            f"so {'congrats' if stat_total <= int(g) else 'better luck next time.'}"
            f"\nOn average you spent {str(aver_total)} {curr} a week, "
            f"{str(aver_meat)}on meat and {str(aver_extra)} on "
            f"extra items.\nWhen there is enough data, I will tell "
            f"you how the current month compares to the average of "
            f"the three previous ones.\nStay tuned."
        )

        print(msg_content)


def make_graph():
    try:

        month = [
            threemonths_before, twomonths_before, onemonth_before, report_month
        ]

        average_totals = [
            data["average"][threemonths_before][0], 
            data["average"][twomonths_before][0],
            data["average"][onemonth_before][0], 
            data["average"][report_month][0]
        ]

        average_meat = [
            data["average"][threemonths_before][1], 
            data["average"][twomonths_before][1],
            data["average"][onemonth_before][1], 
            data["average"][report_month][1]
        ]

        average_extra = [
            data["average"][threemonths_before][2], 
            data["average"][twomonths_before][2],
            data["average"][onemonth_before][2], 
            data["average"][report_month][2]
        ]

        totals = [
            data["average"][threemonths_before][3], 
            data["average"][twomonths_before][3],
            data["average"][onemonth_before][3], 
            data["average"][report_month][3]
        ]

        plt.plot(month, average_totals, color='green')
        plt.plot(month, average_meat, color='red')
        plt.plot(month, average_extra, color='yellow')
        plt.plot(month, totals, color='black')
        plt.xlabel('average totals, meat, extra and total sums')
        plt.ylabel(f'{settings["currency"]}')
        plt.title('Last 4 months')
        plt.show()


    except KeyError:
        print("When there are enough statistics, a graph will be shown for visualization")


def change_goal(json_file):
    """Each time the program is run, 
    the user will have a chance to change their set goal. 
    If they dedide to do so, the new value will replace the old one
    in the settings.json file which is required as a parameter.
    """
    while True:
        should_change = input(
            f'Would you like to keep {settings["goal"]} '
            f'{settings["currency"]} as your monthly maximum goal?'
        )

        if should_change.lower() == "no":
            while True:
                settings["goal"] = input(
                    "What's the maximum amount you want to spend monthly on shopping?"
                )

                if settings["goal"].isdigit() == True:
                    break
                else:
                    print("Oops! I need a number, try again")

            with open(json_file, 'w') as f:
                json.dump(settings, f)

            break

        elif should_change.lower() == "yes":
            break

        else:
            print("Oops, something went wrong. Try again with 'yes' or 'no'")


def send_email(date):
    if len(data["weekly"][date.strftime("%B %Y")]) == 1 and len(data["weekly"]) > 1:
        msg = EmailMessage()
        msg['Subject'] = "Shopping Report"
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = EMAIL_ADDRESS
        msg.set_content(msg_content)

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            smtp.send_message(msg)


if __name__ == '__main__':
    main()

