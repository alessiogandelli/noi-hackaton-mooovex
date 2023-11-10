#%%
import pandas as pd 
from utils import get_random_string
from dotenv import load_dotenv
import os
import langchain

load_dotenv()



# %%
from openai import OpenAI
client = OpenAI()

audio_file= open("//Users/alessiogandelli/dev/cantiere/noi-hackaton-mooovex/data/taxi.mp3", "rb")
transcript = client.audio.transcriptions.create(
  model="whisper-1", 
  file=audio_file
)






# %%
from langchain.prompts import PromptTemplate
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

#%%

prompt = PromptTemplate.from_template("""you are a voice assistant of a taxi driver, you have to extract from his query the following fields: starting_point, end_point, number_of_passengers, date, time.Format it as a JSON. The query is  {query}?""")
p = prompt.format(query=transcript.text)


reply = llm.invoke(p)
# %%
import json 

json.loads(reply.content)

# %%
