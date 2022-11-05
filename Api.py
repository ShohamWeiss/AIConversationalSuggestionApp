from urllib import response
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
import uvicorn
from Conversation import Conversation
from Generator import Generator
from Conversational import Conversational
from QA import QA
import json
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pyngrok import ngrok
from Diarization import Diarization
import os
from io import BytesIO
import librosa
import soundfile as sf

from Speech2Text import Speech2Text

app = FastAPI()
# allow cross origin requests
origins = [    
    "http://localhost",
    "http://localhost:8080",
    "file://",
    "null",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SuggestFromResponseModel(BaseModel):
    ''' DTO for suggest from response '''
    conversation: list[list]
    aboutme: str

@app.get("/", response_class=HTMLResponse)
async def root():
    # return the index.htm file
    return open("index.htm").read()

@app.get("/{filename}", response_class=HTMLResponse)
async def resources(filename: str):
    # return the index.htm file
    return open(f"{filename}").read()

@app.post("/suggest_next_word")
async def suggest_next_word(conversation: list[list], suggestion_sizes: list = [1,1,2,2,4]):
    ''' Generate suggestions using Generative model '''
        
    # Parse Context to Conversation object
    conversation = Conversation(conversation_list=conversation)
    # Run Generative model on Conversation object
    suggestions = generative_model.generate_options(conversation, suggestion_sizes)    
    return suggestions

@app.post("/suggest_from_response")
async def suggest_from_response(request: SuggestFromResponseModel):
    ''' Generate suggestions using Generative, Conversational, and QA model '''
    
    # example input: [[["me", "hello"], ["them", "are you a student?"]], "I am a student"]
    # Parse Context to Conversation object
    conversation = Conversation(conversation_list=request.conversation)
    # Run Generative model on Conversation object -> ["I", "am", "a", "student"]
    gen_suggestions = generative_model.generate_options(conversation, [1,1,2,2,4])
    # Run Conversational model on Conversation object -> "I am a student"
    conv_suggestions = conversational_model.generate_option(conversation)
    # Run QA model on last Conversation object with aboutme -> "I am a student"
    qa_suggestions = qa_model.generate_options(conversation, request.aboutme)
    # Combine suggestions        
    suggestions = { "gen": gen_suggestions, "conv": conv_suggestions, "qa": qa_suggestions }
    return suggestions

@app.post("/transcribe_from_audio")
async def transcribe_from_audio(file: UploadFile):
    ''' Generate suggestions using Generative, Conversational, and QA model '''
    # save file to disk
    filepath = "audio.wav"
    contents = await file.read()
    with open(filepath, "wb") as f:
        f.write(contents)            
    print("Running diarization on audio file...")
    diarization.run_diarization("audio.wav")
    print("Running speech2text on audio files...")
    conversation = speech2text.run_speech2text("diarization")
    
    return conversation.conversation
    

if __name__ == "__main__":
    print("loading generative model")
    generative_model = Generator()
    print("loading conversational model")
    conversational_model = Conversational()
    print("loading QA model")
    qa_model = QA()
    print("loading diarization model")
    diarization = Diarization()
    print("loading speech2text model")
    speech2text = Speech2Text()
    
    # Get the dev server port (defaults to 8000 for Uvicorn, can be overridden with `--port`
    # when starting the server
    port = 8000
    # Open a ngrok tunnel to the dev server
    public_url = ngrok.connect(port).public_url
    print(f"ngrok tunnel {public_url} -> http://localhost:{port}")
    
    print("starting server")    
    uvicorn.run(app)    