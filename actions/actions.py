# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
import json
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, FollowupAction
from rasa_sdk.executor import CollectingDispatcher
import requests
import infermedica_api
import secrets


class ActionMed(Action):
    def name(self):
        return "action_medicine"

    def run(self, dispatcher, tracker, domain):
        api = infermedica_api.APIv3Connector(
            app_id="ebde5b4c", app_key="e12a3525de781b52ae5b0356d21a0a8c"
        )
        choices = {}
        buttons = []

        # Prepare initial patients diagnostic information.
        sex = "female"
        age = 32
        evidence = [
            {"id": "s_21", "choice_id": "present", "source": "initial"},
            {"id": "s_98", "choice_id": "present", "source": "initial"},
            {"id": "s_107", "choice_id": "present"},
        ]
        symp = tracker.get_slot("symptom")
        request = api.diagnosis(evidence=evidence, sex=sex, age=age)
        symp = api.parse(symp, age)
        symp_id = symp["mentions"][0]["id"]
        evidence.append(
            {
                "id": symp_id,
                "choice_id": request["question"]["items"][0]["choices"][0][
                    "id"
                ],  # Just example, the choice_id shall be taken from the real user answer
            }
        )
        # call diagnosis
        request = api.diagnosis(evidence=evidence, sex=sex, age=age)
        #print(response["question"])
        #print(response["question"]["text"])  # actual text of the question
        # list of related evidence with possible answers
        items = request["question"]["items"]

        for choice in items:
            choices[choice["id"]] = choice["name"]
        # actual text of the question
        response = request["question"]["text"]

        for key, value in choices.items():
            title = value
            evidence.append({"id": key, "choice_id": "present"})
            request = api.diagnosis(evidence=evidence, sex=sex, age=age)
            text = request["question"]["text"]
            buttons.append({"title": title, "payload": text})
            response = "Tell me more about it"

        dispatcher.utter_button_message(response, buttons)
        return [SlotSet("symptom", symp)]


