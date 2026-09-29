import json
import os
from dotenv import load_dotenv
from groq import Groq
from retrieval import get_relevant_context
from tools.tools import TOOLS_SCHEMA, execute_tool

load_dotenv()

client=Groq(api_key=os.environ.get("GROQ_API_KEY"))




def llmanswer(query: str) -> str:
    context = get_relevant_context(query)
    system_prompt = f"""You are an intelligent, professional AI Assistant representing Suryaprakash B on his personal portfolio website.

You have access to two sources of information:
1. **Surya's Knowledge Base Context** (provided below).
2. **Google Calendar Tools** (which you can call to check schedule, upcoming meetings, or availability).

### Instructions:
- For questions about Surya's background, work experience, projects, skills, education, or contact info, answer using the retrieved context.
- For questions about Surya's schedule, availability, upcoming events, or booking a meeting, call the appropriate calendar tool.
- Maintain a polite, professional, and helpful tone.
- Do NOT use Markdown table format.

Retrieved Context:
{context}
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": query},
    ]

    # Multi-step tool execution loop (up to 4 steps)
    for _ in range(4):
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=messages,
            tools=TOOLS_SCHEMA,
            tool_choice="auto",
        )

        response_message = response.choices[0].message

        # If no tool calls, return text response
        if not response_message.tool_calls:
            return response_message.content or "I could not find an answer to that."

        # Otherwise execute tool calls and continue
        messages.append(response_message)
        for tool_call in response_message.tool_calls:
            function_name = tool_call.function.name
            try:
                function_args = json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}
            except Exception:
                function_args = {}
            tool_output = execute_tool(function_name, function_args)
            messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": str(tool_output),
                }
            )

    return "The request took too many steps to complete. Please try again."


if __name__ == "__main__":
    import sys
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8")

    print("Testing RAG Query:")
    print(llmanswer("tell about rently"))
    print("\n------------------\n")
    print("Testing Calendar Tool Query:")
    print(llmanswer("book a meeting with surya on 30th sep 5pm to 6pm"))
