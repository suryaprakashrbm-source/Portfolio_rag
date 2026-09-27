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

    output = model.generate(
        **input,
        max_new_tokens=150,
        num_beams=1,
        do_sample=False,
        early_stopping=True
    )

    result = tokenizer.decode(output[0],skip_special_tokens=True)
    return result   


