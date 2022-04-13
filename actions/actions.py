# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals
from tkinter.messagebox import QUESTION
from typing import Any, Text, Dict, List
from urllib import response
from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet, FollowupAction
from rasa_sdk.executor import CollectingDispatcher
import requests
import infermedica_api
import secrets
import json

modification = 0
choice_array = []
api = infermedica_api.APIv3Connector(
            app_id="ebde5b4c", app_key="e12a3525de781b52ae5b0356d21a0a8c"
        )
class InitialQuery(Action):
    def name(self):
        return "action_initial_query"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[List, Any]):
        gender_provided = str(tracker.get_slot("gender"))
        age_provided = str(tracker.get_slot("age"))
        symptom_initial_provided = str(tracker.get_slot("symptom_initial"))
       
        age = int(age_provided)
        gender = str(gender_provided.lower())
        symptom_query = str(symptom_initial_provided)
        symp = api.parse(text=symptom_query, age=age)
      
        # Staring of the List:
        possibleSymptomsIDs = {}
        for symid in symp["mentions"]:
            # Considering one of the symptoms as Initial
            if "Initial" not in possibleSymptomsIDs:
                possibleSymptomsIDs["Initial"] = symid["id"]
                possibleSymptomsIDs[symid["id"]] = symid["choice_id"]


        print(possibleSymptomsIDs)
        return [SlotSet("ids", possibleSymptomsIDs)]    

    
class DiagnosisQuery(Action):
    def name(self):
        return "action_diagnosis_query"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[List, Any]):
        gender_provided = str(tracker.get_slot("gender"))
        age_provided = str(tracker.get_slot("age"))
        name_provided = str(tracker.get_slot("name"))
        SymptomsIDs = (tracker.get_slot("ids"))
        age = int(age_provided)
        gender = (str(gender_provided.lower()))
        name = (str(name_provided.lower()))
        evidenceList = []
        Initial_True = SymptomsIDs["Initial"]
        for id, choiceID in SymptomsIDs.items():
            if id == "Initial":
                continue
            elif id == Initial_True:  # Only for considering Initial as Initial.
                evidenceList.append({"id": id, "choice_id": choiceID, "source": "initial"})
            else:
                evidenceList.append({"id": id, "choice_id": choiceID})      

        request = api.diagnosis(evidence=evidenceList, sex=gender, age=age, interview_id=name)
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
        print(question, questions_to_ask, IDs)

        dispatcher.utter_message(question)
    
        return [SlotSet("prompts", questions_to_ask), SlotSet("idkey", IDs)]


class ResponseQuery(Action):
    global modification
    
    def name(self):
        return "action_response_query"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
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
                return [FollowupAction('action_listen')] 
        else:
            modification = 0
            return [SlotSet("choice", "null")]
		

class StorageQuery(Action):
    global choice_array

    def name(self):
        return "action_storage_query"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]):
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
            print(choice_array)
            return [SlotSet("ids", SymptomsIDs), SlotSet("flag", True)]




class ResetSlots(Action):
    def name(self):
        return "action_reset_slots"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict):
        return [SlotSet("choice", None), SlotSet("idkey", None), SlotSet("prompts", None), SlotSet("flag", False)]