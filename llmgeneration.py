import os
from google import genai 
from groq import Groq
from retrieval import get_relevant_context
from dotenv import load_dotenv

load_dotenv()

client=Groq(api_key=os.environ.get("GROQ_API_KEY"))




def llmanswer(query:str):
    context=get_relevant_context(query)
    prompt = f"""Answer the question based on the context below. Dont answer anything apart from this context 
        Context:
        {context}
        Question: {query}
        Answer:"""


    response = client.chat.completions.create(
        messages=[
            {"role": "user", "content": prompt}
        ],
        model="openai/gpt-oss-120b",
    )

    
    return response.choices[0].message.content


if __name__ == "__main__":
    print(llmanswer("Who is Suryaprakash?"))
