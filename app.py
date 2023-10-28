# from flask import Flask
from typing import Any
from flask import Flask, request, jsonify
from typing import Dict, Any
from flask_cors import CORS


from typing import Optional, Type, Union
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from gcsa.google_calendar import GoogleCalendar
from gcsa.recurrence import Recurrence, YEARLY, DAILY, WEEKLY, MONTHLY
from gcsa.event import Event
from os import environ
from datetime import date, datetime
from langchain.agents import AgentType, initialize_agent
from langchain.tools import BaseTool, StructuredTool, Tool, tool
from langchain import OpenAI, LLMChain
from dotenv import load_dotenv
import agent_prompt
from langchain.llms import OpenAI
from langchain.llms.openai import OpenAI
from langchain.agents.agent_types import AgentType
from langchain.memory import ConversationBufferMemory
from langchain.agents import ZeroShotAgent
from langchain.memory import ConversationBufferMemory
from langchain.agents.initialize import initialize_agent
from typing import List, Union
from dateutil import tz
import os

from gcsa.google_calendar import GoogleCalendar


from main_google_agent import CalenderCreateEventTool, CalenderViewEventTool

load_dotenv()

from langchain.callbacks.manager import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from enum import Enum, auto
from typing import Optional

# app = Flask(__name__)

app: Flask = Flask(__name__)

CORS(app)

@app.route("/")
def hello() -> str:
    return "Hello, World!"


@app.route("/query/<string:query>", methods=["GET", "POST"])
def query_string(query: str) -> str:
    # query_string = request.json.get('query')

    tools = [
        CalenderCreateEventTool(),
            CalenderViewEventTool()
    ]


    prefix = agent_prompt.prefix
    suffix = """Begin!"

    {chat_history}
    Question: {input}
    {agent_scratchpad}"""

    prompt = ZeroShotAgent.create_prompt(
        prefix=prefix,
        suffix=suffix,
        input_variables=["input", "chat_history", "agent_scratchpad"],
        tools=tools,
    )

    memory = ConversationBufferMemory(memory_key="chat_history")


    llm = OpenAI(temperature=0)

    agent_executor = initialize_agent(
        tools,
        llm,
        agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
        prompt=prompt,
    )


    # agent_executor.run("set up an weekly event for 5pm where i jog for an hour")
    query = query.replace("+", " ")

    # print(query)
    # print(query_string )
    # message: str = request.args.get("message", "No message provided")
    agent_executor.run(query)

    return "Okay" , 200
    # return f"You sent the message: {message}"
    # return f"You sent the message: {message}"


@app.route("/get_events")
def get_events() -> Dict[str, Any]:

    

    GOOGLE_EMAIL = environ.get('GOOGLE_CALENDER_EMAIL')
    GMAIL_CREDENTIALS_PATH = environ.get('GMAIL_CREDENTIALS_PATH')

    # calendar = GoogleCalendar('isayahai08@gmail.com')
    # calendar = GoogleCalendar(
    #     GOOGLE_EMAIL
    #                           credentials_path=GMAIL_CREDENTIALS_PATH
    #                           )
    
    calendar = GoogleCalendar( GOOGLE_EMAIL, credentials_path=GMAIL_CREDENTIALS_PATH)
    # calendar = GoogleCalendar(
    #     GOOGLE_EMAIL, 
    #     GMAIL_CREDENTIALS_PATH=GMAIL_CREDENTIALS_PATH
    #     )

    x = 0
# for event in calendar:
#     print(event)
#     events: Dict[str, Any] = {
#         "events": [
#             {"name": "Event1", "location": "Location1", "date": "2023-11-01"},
#             {"name": "Event2", "location": "Location2", "date": "2023-12-15"},
#             {"name": "Event3", "location": "Location3", "date": "2024-01-20"}
#         ]
#     }
#     return jsonify(events)
    calendar = GoogleCalendar('isayahai08@gmail.com', credentials_path='/home/isayahc/projects/Liberty-DAO-Hackathon/.credentials/credentials.json')
    for event in calendar:
        print(event)

    calendar = [ str(event) for event in calendar]

    formatted_events = format_events(calendar)
    return jsonify(formatted_events)
    # print(json.dumps(formatted_events, default=str, indent=4))
    # return jsonify(calendar)
    # return "Okay"


def format_events(events: List[str]) -> List[Dict]:
    formatted_events = []
    for event in events:
        date_time, title = event.split(" - ")
        formatted_event = {
            'title': title,
            'start': datetime.fromisoformat(date_time),
            'end': datetime.fromisoformat(date_time),  # Assuming the end time is the same as the start time
            'url': None,
            'allDay': False,
            'editable': False,
            'extendedProps': {
                'category': None,
            },
            'description': None
        }
        formatted_events.append(formatted_event)
    return formatted_events

if __name__ == "__main__":
    app.run(port=8080)
