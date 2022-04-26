# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet , UserUtteranceReverted
from rasa_sdk.events import FollowupAction
from rasa_sdk.events import BotUttered
from rasa_sdk.types import DomainDict
from weather import Weather, Version
import sqlite3

# change this to the location of your SQLite file
path_to_db = "actions/bot.db"
connection = sqlite3.connect(path_to_db)
cursor = connection.cursor()

        # get email slot
order_email = (['me@gmail.com'])
print(order_email)
        # retrieve row based on email
# cursor.execute("SELECT * FROM orders WHERE (order_email) = ?", order_email)
cursor.execute("SELECT * FROM inventory WHERE (size) = ? AND (color) = ?", [(int('9')),'blue'])
data_row = cursor.fetchone()
print(data_row)

class ActionProductSearch(Action):
    def name(self) -> Text:
        return "action_product_search"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # connect to DB
        connection = sqlite3.connect(path_to_db)
        cursor = connection.cursor()

        # get slots and save as tuple
        shoe = [(int(tracker.get_slot("size")),tracker.get_slot("color"))]
        # place cursor on correct row based on search criteria
        cursor.execute("SELECT * FROM inventory WHERE (size) = ? AND (color) = ?", [int(tracker.get_slot("size")),tracker.get_slot("color")])
        # retrieve sqlite row
        data_row = cursor.fetchone()

        if data_row:
            # provide in stock message
            dispatcher.utter_message(response="utter_in_stock")
            connection.close()
            slots_to_reset = ["size", "color"]
            return [SlotSet(slot, None) for slot in slots_to_reset]
        else:
            # provide out of stock
            dispatcher.utter_message(response="utter_no_stock")
            connection.close()
            slots_to_reset = ["size", "color"]
            return [SlotSet(slot, None) for slot in slots_to_reset]


class ReturnOrder(Action):
    def name(self) -> Text:
        return "action_return"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # connect to DB
        connection = sqlite3.connect(path_to_db)
        cursor = connection.cursor()

        # get email slot
        order_email = ([tracker.get_slot("email")])
        print(order_email)
        # retrieve row based on email
        cursor.execute("SELECT * FROM orders WHERE (order_email) = ?", order_email)
        data_row = cursor.fetchone()

        if data_row:
            # change status of entry
            status = [("returning"), (tracker.get_slot("email"))]
            cursor.execute("UPDATE orders SET status=? WHERE (order_email) = ?", status)
            connection.commit()
            connection.close()

            # confirm return
            dispatcher.utter_message(text="Ok, I've kicked off your return. You should be receiving a return label in your inbox. Please send it in the next 14 days!")
            return [SlotSet("email", None)]
        else:
            # db didn't have an entry with this email
            dispatcher.utter_message(text="Hmm, seems like we don't have an order associated with that email")
            connection.close()
            return [SlotSet("email", None)]


class OrderStatus(Action):
    def name(self) -> Text:
        return "action_order_status"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        # connect to DB
        connection = sqlite3.connect(path_to_db)
        cursor = connection.cursor()

        # get email slot
        order_email = ([tracker.get_slot("email")])
        # retrieve row based on email
        cursor.execute("SELECT * FROM (orders) WHERE (order_email) = ? ", order_email)
        data_row = cursor.fetchone()

        if data_row:
            # convert tuple to list
            data_list = list(data_row)

            # respond with order status
            dispatcher.utter_message(text=f"Based on the latest order from {data_list[3]}, it looks like your order is currently {data_list[5]}.")
            connection.close()
            return [SlotSet("email", None)]
        else:
            # db didn't have an entry with this email
            dispatcher.utter_message(text="Hmm, seems like we don't have an order associated with that email")
            connection.close()
            return [SlotSet("email", None)]


class CheckWeather(Action):

    def name(self) -> Text:
        return "action_tell_weather"

    def run(self, dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        city = (tracker.get_slot("city"))
        temp=int(Weather(city)['temp']-273)
        if not city:
            dispatcher.utter_message(text=f"Sorry, have you given wrong city name ?")
            return [SlotSet("city", None)]

        dispatcher.utter_message(text=f"Today's temperature is {temp} degree Celcius.")
        return [SlotSet("city", None)]


class CheckRasaVersion(Action):

    def name(self) -> Text:
        return "action_bot_challenge"

    def run(self, dispatcher: CollectingDispatcher,
    tracker: Tracker,
    domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        temp=Version()
        dispatcher.utter_message(text=f"{temp}")
        return [SlotSet("version", None)]


def clean_color(color):
    return color.isalpha()
def clean_size(size):
    return size.isnumeric() and int(size) < 15 and int(size) > 0

class ValidateNameForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_product_stock_form"

    def validate_color(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `color."""

        # If the name is super short, it might be wrong.
        color = clean_color(slot_value)
        print(color)
        if not color:
            dispatcher.utter_message(text="That must've been a typo.")
            return {"color": None}
        return {"color": slot_value}

    def validate_size(
        self,
        slot_value: Any,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate `size` value."""

        # If the name is super short, it might be wrong.
        size = clean_size(slot_value)
        print(size)
        if not size:
            dispatcher.utter_message(text="That must've been a typo. the size should be betwwen 1 and 15")
            return {"size": None}
        return {"size": slot_value}