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
load_dotenv()



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


# %%
def parse_trip(transcript):
# parse the text to extract the fields
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
    prompt = PromptTemplate.from_template("""you are a voice assistant of a taxi driver, you have to extract from his query the following fields, the starting point should be or a address or a point of interest (include the city in the address), if it is a point of interest just say the name and the place without conjunction: starting_point, end_point, number_of_passengers(int), date, time, language(en, de, it) .Format it as a JSON. The query is  {query}?""")
    p = prompt.format(query=transcript)
    reply = llm.invoke(p)
    trip = json.loads(reply.content)

    return trip


# %%
# get google place id

def get_place_id(trip):

    url =  'https://dev.api.mooovex.com/hackathon/autocomplete'

    data_autocomplete_start = {
        'query': trip['starting_point'],
        'language': trip['language']
    }

    data_autocomplete_end = {
        'query': trip['end_point'],
        'language': trip['language']
    }


    try:
        start_response = requests.post(url, json = data_autocomplete_start)
        place_id_start = start_response.json()[0]['google_place_id']

    except:
        print("Error with start point")
        place_id_start = 'ChIJNfJk6gq0LBMREIhQvO0vKB4'

    try:
        end_response = requests.post(url, json = data_autocomplete_end)
        place_id_end = end_response.json()[0]['google_place_id']
    except:
        print("Error with end point")
        place_id_end = 'ChIJLzmuIxNxgUcR4D4x6kxMH4c'

    return place_id_start, place_id_end


# %% search the route
def search_route(place_id_start, place_id_end, trip):
    url_route = 'https://dev.api.mooovex.com/hackathon/routedetails'

    data_route = {
        'origin_google_place_id': str(place_id_start),
        'destination_google_place_id': str(place_id_end),
        'passenger_count': trip['number_of_passengers'],
        'when':{
            'date': "2023-11-10",
            'time':  "12:30:00"
        },
        'language': trip['language']
    }

    route_response = requests.post(url_route, json = data_route)

    return route_response.json()






# %%
