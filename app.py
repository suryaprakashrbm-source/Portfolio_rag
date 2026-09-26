from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from llmgeneration import llmanswer
from pydantic import BaseModel


class Myclass(BaseModel):
    query:str


app=FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # Allows all origins including file:// (origin: null)
    allow_credentials=True,
    allow_methods=["*"],        # Allows POST, OPTIONS, GET, etc.
    allow_headers=["*"],        # Allows Content-Type and custom headers
)


@app.get('/')
def home():
    return {"message":"Server is running"}  

@app.post('/ask')
def ask_suryaprakash(request:Myclass):
    response=llmanswer(request.query)
    return{"message":f"Response : {response}"}  
