from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from retrieval import get_relevant_context


tokenizer = AutoTokenizer.from_pretrained('google/flan-t5-base')

model=AutoModelForSeq2SeqLM.from_pretrained('google/flan-t5-base')




def llmanswer(query:str):
    context=get_relevant_context(query)
    prompt = f"""Answer the question based on the context below.
        Context:
        {context}
        Question: {query}
        Answer:"""

    input=tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)

    output=model.generate(**input,max_new_tokens=500,min_length=60,num_beams=6,no_repeat_ngram_size=3,early_stopping=True)

    result = tokenizer.decode(output[0],skip_special_tokens=True)
    return result   


