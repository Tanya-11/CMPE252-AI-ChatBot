# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, UserUtteranceReverted
from rasa_sdk.events import FollowupAction
from rasa_sdk.events import BotUttered
from rasa_sdk.types import DomainDict
from api import Weather, Version
import sqlite3

# location of your SQLite file
path_to_db = "actions/bot.db"


def clean_color(color):
    return color.isalpha()


def clean_size(size):
    return (isinstance(size, float) or isinstance(size, int)) and int(size) < 15 and int(size) > 0


class ActionProductSearch(Action):
    def name(self) -> Text:
        return "action_product_search"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        slots_to_reset = ["size", "color"]
        # size = clean_size(tracker.get_slot("size"))
        # print(size)
        # if not size:
        #     dispatcher.utter_message(
        #         text="That must've been a typo. the size should be between 1 and 15")
        #     return [SlotSet("size", None)]

        # connecting to DB
        connection = sqlite3.connect(path_to_db)
        cursor = connection.cursor()

        # place cursor on correct row based on search criteria
        cursor.execute("SELECT * FROM inventory WHERE (size) = ? AND (color) = ?",[int(tracker.get_slot("size")), tracker.get_slot("color")])
        # retrieve sqlite row
        data_row = cursor.fetchone()

        if data_row:
            # provide in stock message
            dispatcher.utter_message(response="utter_in_stock")
            connection.close()
            return [SlotSet(slot, None) for slot in slots_to_reset]
        else:
            # provide out of stock
            dispatcher.utter_message(response="utter_no_stock")
            connection.close()

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
        cursor.execute(
            "SELECT * FROM orders WHERE (order_email) = ?", order_email)
        data_row = cursor.fetchone()

        if data_row:
            # change status of entry
            status = [("returning"), (tracker.get_slot("email"))]
            cursor.execute(
                "UPDATE orders SET status=? WHERE (order_email) = ?", status)
            connection.commit()
            connection.close()

            # confirm return
            dispatcher.utter_message(
                text="Ok, I've kicked off your return. You should be receiving a return label in your inbox. Please send it in the next 14 days!")
            return [SlotSet("email", None)]
        else:
            # db didn't have an entry with this email
            dispatcher.utter_message(
                response="utter_no_order")
            return [SlotSet("email", None)]


class OrderStatus(Action):
    def name(self) -> Text:
        return "action_order_status"

    async def run(
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
        cursor.execute(
            "SELECT * FROM (orders) WHERE (order_email) = ? ", order_email)
        data_row = cursor.fetchone()

        if data_row:
            # convert tuple to list
            data_list = list(data_row)
            connection.close()
            # respond with order status
            dispatcher.utter_message(
                text=f"Based on the latest order for {data_list[3]} shoes, it looks like your order is currently {data_list[5]}.")           
            return [SlotSet("email", None)]
        else:
            # db didn't have an entry with this email
            dispatcher.utter_message(
                response="utter_no_order")
            return [SlotSet("email", None)]


class CheckWeather(Action):

    def name(self) -> Text:
        return "action_tell_weather"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        city = (tracker.get_slot("city"))
        print("weather")
        print(city)
        if not city:
            dispatcher.utter_message(
                text=f"Sorry, have you given wrong city name ?")
            return [SlotSet("city", None)]
        temp = int(Weather(city)['temp']-273)
        print(temp)
        dispatcher.utter_message(
            text=f"Today's temperature is {temp} degree Celsius.")
        return [SlotSet("city", None)]


class CheckRasaVersion(Action):

    def name(self) -> Text:
        return "action_bot_challenge"

    async def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        temp = Version()
        # print(temp)
        dispatcher.utter_message(
            text=f"Beep, bop! I am a bot, powered by Rasa {temp}")
        return []


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
            dispatcher.utter_message(
                text="That must've been a typo. the size should be betwwen 1 and 15")
            return {"size": None}
        return {"size": slot_value}
