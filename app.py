from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from llmgeneration import llmanswer
from pydantic import BaseModel


class Myclass(BaseModel):
    query:str


app=FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
def home():
    return {"message":"Server is running"}  

@app.post('/ask')
def ask_suryaprakash(request: Myclass):
    try:
        response = llmanswer(request.query)
        return {"message": f"{response}"}
    except Exception as e:
        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            return {"message": "The assistant is receiving many requests right now. Please wait a few seconds and try again!"}
        return {"message": "Something went wrong, please try again later."}

