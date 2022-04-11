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
from rasa_sdk.events import SlotSet, FollowupAction
from rasa_sdk.executor import CollectingDispatcher
import requests
import infermedica_api
import secrets
import json

modification = 0
choice_array = []

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
    

modification = 0
choice_array = []


class InitialQuery(Action):

    def name(self) -> Text:
        return "action_initial_query"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        gender_provided = str(tracker.get_slot("gender"))
        age_provided = str(tracker.get_slot("age"))
        symptom_initial_provided = str(tracker.get_slot("symptom_initial"))
        SymptomIDs = InitialQuery.firstSymptomCollector(gender_provided, age_provided, symptom_initial_provided)

        # Run close:
        return [SlotSet("ids", SymptomIDs)]

    def firstSymptomCollector(gender_provided, age_provided, symptom_initial_provided):

        url = "https://api.infermedica.com/v3/parse"
        App_ID = 'ebde5b4c'
        App_Key = 'e12a3525de781b52ae5b0356d21a0a8c'
        age = int(age_provided)
        gender = (str(gender_provided.lower()))
        symptom_query = str(symptom_initial_provided)

        payload = json.dumps({
            "text": symptom_query,
            "age": {
                "value": age
            },
            "sex": gender
        })
        headers = {
            'App-Id': App_ID,
            'App-Key': App_Key,
            'Authorization': 'Basic ZThlYzNhMjM6IGJiNWY5OWZkZjI5MDg4MTA4OWYzYzE1MTA5N2RlNTEzCSA=',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        # Converting the response received to the JSON Format
        info = response.json()

        # Staring of the List:
        possibleSymptomsIDs = {}
        for symid in info["mentions"]:
            # Considering one of the symptoms as Initial
            if "Initial" not in possibleSymptomsIDs:
                possibleSymptomsIDs["Initial"] = symid["id"]
            possibleSymptomsIDs[symid["id"]] = symid["choice_id"]

        return possibleSymptomsIDs

class DiagnosisQuery(Action):

    def name(self) -> Text:
        return "action_diagnosis_query"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        gender_provided = str(tracker.get_slot("gender"))
        age_provided = str(tracker.get_slot("age"))
        SymptomsIDs = (tracker.get_slot("ids"))
        Question, Ques_Ans, IDs = DiagnosisQuery.diagnosis(gender_provided, age_provided, SymptomsIDs)

        dispatcher.utter_message(Question)
        # Run close:
        return [SlotSet("prompts", Ques_Ans), SlotSet("idkey", IDs)]

    def diagnosis(gender_provided, age_provided, possibleSymptomsIDs):
        url = "https://api.infermedica.com/v3/diagnosis"
        App_ID = 'ebde5b4c'
        App_Key = 'e12a3525de781b52ae5b0356d21a0a8c'
        age = int(age_provided)
        gender = (str(gender_provided.lower()))

        evidenceList = []
        # Getting the varible Initial
        Initial_True = possibleSymptomsIDs["Initial"]

        for id, choiceID in possibleSymptomsIDs.items():
            if id == "Initial":
                continue
            elif id == Initial_True:  # Only for considering Initial as Initial.
                evidenceList.append({"id": id, "choice_id": choiceID, "source": "initial"})
            else:
                evidenceList.append({"id": id, "choice_id": choiceID})

        print(evidenceList)
        payload = json.dumps({
            "sex": gender,
            "age": {
                "value": age
            },
            "evidence": evidenceList
        })
        headers = {
            'App-Id': App_ID,
            'App-Key': App_Key,
            'Authorization': 'Basic ZThlYzNhMjM6IGJiNWY5OWZkZjI5MDg4MTA4OWYzYzE1MTA5N2RlNTEzCSA=',
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        r = response.json()
        #  print(r['question']['items'])

        questions_to_ask = []
        IDs = []
        for i in (r['question']['items']):
            response_str = ""
            response_str += str(i['name']) + "\n"
            # Storing the ID
            IDs.append(i['id'])
            # print(ID)
            # print(i['name'])
            order = 1
            for j in (i['choices']):
                response_str += str(order) + ". " + str(j['label']) + "\n"
                order += 1
            questions_to_ask.append(response_str)

        return (r["question"]["text"], questions_to_ask, IDs)

class ResponseQuery(Action):
    global modification
    
    def name(self) -> Text:
        return "action_response_query"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        global modification
        gender_provided = str(tracker.get_slot("gender"))
        age_provided = str(tracker.get_slot("age"))
        Choice = str(tracker.get_slot("choice"))
        Ques_Ans = (tracker.get_slot("prompts"))

        if Choice != 'a' and Choice != 'A' and Choice != 'a.' and Choice != "A." and Choice != "null":
            count = 0
            for q in Ques_Ans:
                if count != modification:
                    count += 1
                    continue
                dispatcher.utter_message(q)
                modification += 1
                return [FollowupAction('action_listen')]  # CHECK!!
        else:
            modification = 0
            return [SlotSet("choice", "null")]
		# elif mod = 0 and count =5:                                        # check on this!!!
			# return [SlotSet("choice", "null"),SlotSet("breaker", true)]

class StorageQuery(Action):
    global choice_array

    def name(self) -> Text:
        return "action_storage_query"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        global choice_array
        Choice = str(tracker.get_slot("choice"))
        choice_array.append(Choice)
        IDs = (tracker.get_slot("idkey"))
        SymptomsIDs = (tracker.get_slot("ids"))

        if len(choice_array) >= len(IDs):
            for i in range(len(IDs)):
                if 'a' == choice_array[i] or 'A' == choice_array[i] or 'a.' == choice_array[i] or 'A.' == choice_array[i]:
                    SymptomsIDs[IDs[i]] = "present"
                elif 'b' == choice_array[i] or 'B' == choice_array[i] or 'b.' == choice_array[i] or 'B.' == \
                        choice_array[i]:
                    SymptomsIDs[IDs[i]] = "absent"
                elif 'c' == choice_array[i] or 'C' == choice_array[i] or 'c.' == choice_array[i] or 'C.' == \
                        choice_array[i]:
                    SymptomsIDs[IDs[i]] = "unknown"
            choice_array=[]
            return [SlotSet("ids", SymptomsIDs), SlotSet("flag", True)]




class ResetSlots(Action):
    def name(self) -> Text:
        return "action_reset_slots"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> List[Dict[Text, Any]]:
        return [SlotSet("choice", None), SlotSet("idkey", None), SlotSet("prompts", None), SlotSet("flag", False)]