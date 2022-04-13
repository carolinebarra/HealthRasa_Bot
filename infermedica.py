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
name = "caroline"
symp = api.parse(text="fever and headache", age=age)
possibleSymptomsIDs = {}
for symid in symp["mentions"]:
            # Considering one of the symptoms as Initial
    if "Initial" not in possibleSymptomsIDs:
        possibleSymptomsIDs["Initial"] = symid["id"]
        possibleSymptomsIDs[symid["id"]] = symid["choice_id"]


print(possibleSymptomsIDs)
evidenceList = []
Initial_True = possibleSymptomsIDs["Initial"]
for id, choiceID in possibleSymptomsIDs.items():
    if id == "Initial":
        continue
    elif id == Initial_True:  # Only for considering Initial as Initial.
        evidenceList.append({"id": id, "choice_id": choiceID, "source": "initial"})
    else:
        evidenceList.append({"id": id, "choice_id": choiceID})      

request = api.diagnosis(evidence=evidenceList, sex=sex, age=age, interview_id=name)
#  print(r['question']['items'])
#print(response["question"]["text"])  # actual text of the question
# list of related evidence with possible answers
question = request["question"]["text"]
items = request["question"]["items"]

questions_to_ask = []
IDs = []
for i in items:
    response_str = ""
    response_str += str(i['name']) + "\n"
    # Storing the ID
    IDs.append(i['id'])
    print(IDs)
    print(i['name'])
    order = 1
    for j in (i['choices']):
        response_str += str(order) + ". " + str(j['label']) + "\n"
        order += 1
    questions_to_ask.append(response_str)
print(questions_to_ask, IDs)







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
    