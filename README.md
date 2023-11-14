# Mooovex challenge 
This is the winner [project](https://hackathon.bz.it/project/studybuddy) of the NOI Techpark Hackathon 2023.

The goal of the challenge is to develop a voice interface that allows the taxi driver to add rides to the system. 
The user should send a voice message to the telegram bot with the following information:
- Origin
- Destination
- Date
- Time
- Number of passengers

## Pipeline 

1) The user sends a voice message to the telegram bot
2) The server transcript the voice message to text using [whisper](https://openai.com/research/whisper) 
3) The server parses the text to extract the information using a specific prompt to the chat model gpt-3.5-turbo
3.1) [optional] if the number of users is not provided the model will ask for it using a voice message
4) The server sends the parsed information to Mooovex API to get a route back 
5) The server formats the route in a human readable way using a language model (gpt3.5-turbo)
6) The server creates a voice message using the tts-1 (Text to speech) model of OpenAI
7) The server sends the voice message to the user using telegram bot asking for confirmation
8) The user confirms the ride

## Features
- multilingual
- user flexibility while talking


