from fastapi import FastAPI

from llmgeneration import llmanswer
from pydantic import BaseModel


class Myclass(BaseModel):
    query:str


app=FastAPI()

@app.get('/')
def home():
    return {"message":"Server is running"}  

@app.post('/ask')
def ask_suryaprakash(request:Myclass):
    response=llmanswer(request.query)
    return{"message":f"Response : {response}"}  
