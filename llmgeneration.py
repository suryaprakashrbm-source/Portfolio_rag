import os
from google import genai 
from retrieval import get_relevant_context
from dotenv import load_dotenv

load_dotenv()

client=genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))




def llmanswer(query:str):
    context=get_relevant_context(query)
    prompt = f"""Answer the question based on the context below.
        Context:
        {context}
        Question: {query}
        Answer:"""


    response = client.models.generate_content(
        model="gemini-3.8-flash",
        contents=prompt
    )

    
    return response.text


if __name__ == "__main__":
    print(llmanswer("Who is Suryaprakash?"))
