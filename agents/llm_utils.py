from openai import OpenAI
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
import os
from groq import Groq
import os
import time
import json

# Load environment variables from .env file
load_dotenv()

def predict(user_query: str) ->str:

    model ="openai"
    if model=="openai":
        print("[Info] Running for Open AI..")
        try:
            client = OpenAI()

            response = client.responses.create(
                model="gpt-4o",
                input=user_query
            )

            print(response)
            print("="*50)

            return response.output_text
        except Exception as e:
            print(e)
            print("Open AI Key is not working redirecting to gemini")
            return predict("gemini",user_query)
    
    elif model=="gemini":
        llm = ChatGoogleGenerativeAI(model="gemini-1.5-pro", convert_system_message_to_human=True)

        response = llm.invoke(
            [
                SystemMessage(content="You are an helpful assistant. Whose role is to asnwer the user query"),
                HumanMessage(content=f"{user_query}"),
            ]
        )
        
        return response.content