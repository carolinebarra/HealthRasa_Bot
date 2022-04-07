# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
import infermedica_api
import secrets

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

request = api.diagnosis(evidence=evidence, sex=sex, age=age)
symp = api.symptom_list(age);
print(symp)

