#%%
import pandas as pd 
from utils import get_random_string
from dotenv import load_dotenv
import os
import langchain
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from openai import OpenAI
import json 
import requests
import datetime

load_dotenv()


llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

base_city = 'Bolzano'

# %%
# speech to text 
def speech_to_text():
    
    client = OpenAI()
    audio_file= open("//Users/alessiogandelli/dev/cantiere/noi-hackaton-mooovex/data/taxi.mp3", "rb")
    transcript = client.audio.transcriptions.create(
    model="whisper-1", 
    file=audio_file
    )
    return transcript.text


def text_to_speech(text):
    client = OpenAI()

    speech_file_path = "data/speech.mp3"
    response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input=text
    )
    response.stream_to_file(speech_file_path)
    

# %%
def parse_trip(transcript):
# parse the text to extract the fields
    prompt = PromptTemplate.from_template("""you are a voice assistant of a taxi driver, you have to extract from his query the following fields, the starting point should be or a address or a point of interest (include the city in the address) if no city is provided it is bolzano by default, if it is a point of interest just say the name and the place without conjunctions, if no date is provided write None, if no time is provided write None, infer the language: starting_point, end_point, number_of_passengers(int), date("%Y-%m-%d"), time("%H:%M:%S"), language(en, de, it) .Format it as a JSON. The query is  {query}?""")
    p = prompt.format(query=transcript)
    reply = llm.invoke(p)
    trip = json.loads(reply.content)

    if trip['date'] == 'None': 
        trip['date'] = datetime.datetime.now().strftime("%Y-%m-%d")
    
    if trip['time'] == 'None':
        trip['time'] = datetime.datetime.now().strftime("%H:%M:%S")

    return trip

def confirm_trip(transcript):
    prompt = PromptTemplate.from_template("the user have been asked if something is correct,< {query}> is the reply, you have to tell me if the user is confirming, you can only reply <yes> or <no>, lower case, without punctuation. The user could talk in italian or english or german")
    p = prompt.format(query=transcript)
    reply = llm.invoke(p)
    print(reply.content)
    return reply.content


def number_of_passangers(transcript):

    prompt = PromptTemplate.from_template("how many passengers? reply with json format with field named 'passengers' type int: {query}")
    p = prompt.format(query=transcript)
    reply = llm.invoke(p)
    n = json.loads(reply.content)['passengers']
    print(n)
    return n
# %%
# get google place id

def get_place_id(trip, context, update):

    url =  'https://dev.api.mooovex.com/hackathon/autocomplete'

    data_autocomplete_start = {
        'query': trip['starting_point'],
        'language': trip['language']
    }

    data_autocomplete_end = {
        'query': trip['end_point'],
        'language': trip['language']
    }

    print(trip)


    try:
        start_response = requests.post(url, json = data_autocomplete_start)
        place_id_start = start_response.json()[0]['google_place_id']

    except:
        print("did not understand the starting point\n")
        # wait for user message 
        place_id_start = None

    try:
        end_response = requests.post(url, json = data_autocomplete_end)
        place_id_end = end_response.json()[0]['google_place_id']
    except:
        print("did not understand the destination \n")        
        place_id_end = None

    return place_id_start, place_id_end


# %% search the route
def search_route(place_id_start, place_id_end, trip):
    url_route = 'https://dev.api.mooovex.com/hackathon/routedetails'

    data_route = {
        'origin_google_place_id': str(place_id_start),
        'destination_google_place_id': str(place_id_end),
        'passenger_count': trip['number_of_passengers'],
        'when':{
            'date': trip['date'],
            'time':  trip['time']
        },
        'language': trip['language']
    }

    route_response = requests.post(url_route, json = data_route)

    return route_response.json()






# %%
