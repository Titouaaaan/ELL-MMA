import os
import base64
import requests
from openai import OpenAI
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    ToolMessage,
)
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langgraph.graph import END, StateGraph, START
from langchain_core.tools import tool
import functools
from langchain_core.messages import AIMessage
import operator
from typing import Sequence , List
from langchain_openai import ChatOpenAI
import json
from langchain_core.messages import ToolMessage

os.environ["LANGSMITH_API_KEY"] = "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"
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_PROJECT"] = "tutor agents"
os.environ["OPENAI_API_KEY"] = "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"
GPT_MODEL = "gpt-4-turbo"
client = OpenAI()
llm = ChatOpenAI(model=GPT_MODEL)

all_txt = """ Kapitel: 1
Thema: Moien!... an Addi!
Kategorie: Gespréich
Agent(en): Lies-Agent, Konversatiouns-Agent
Inhalt:
  
Persoun 1: Moien!
Persoun 2: Moien!
Gudde Mëtteg soen
Persoun 1: Gudde Mëtteg, Madame!
Persoun 2: Moien!
Nimm benotzen wann ee sech begréisst
Persoun 1: Moien Anna!
Persoun 2: Hallo!
Persoun 1: Salut Jang!
Persoun 2: Moie Pierre

Kapitel: 1
Thema: Moien!... an Addi!
Kategorie: Gespréich
Agent(en): Lies-Agent, Konversatiouns-Agent
Inhalt:
  
Gudden Owend, Madame Wagner - Oh, gudden Owend, Här Michels! An Äddi!
Awadame Medinger! Nach e scheinen Dag! - Merci gläichfalls! Awar!
Äddi! - Merci fir d'Invitatioun! Nach e scheinen Owend!
Gutt Nuecht! Schlof gutt! - Gutt Nuecht!"

Kapitel: 1
Thema: Moien!... an Addi!
Kategorie: Liesen
Agent(en): Lies-Agent
Inhalt:
  
Fir dës Fotoen, virstellen, datt dës Leit schwätzen Moien ze soen.

Kapitel: 1
Thema: Moien!... an Addi!
Kategorie: Gespréich
Agent(en): Lies-Agent, Konversatiouns-Agent
Inhalt:
  
Bonjour
Salut
Moien
Gudde Moien
Gudde Mëtteg
Gudden Owend
Awar/Awuer
Addi
Scheine Meneg
Gutt Nuecht
Scheinen Owend

Optrag:
Wat soen d'Leit? Schreift eppes an d'Spriechblosen.
Gitt an der Klass ronderëm a sot de Leit Moien.
"""

prompt = '''steps to follow to seprate the text:
            -GROUP BY kapitel
            -then GROUP BY thema
            -then GROUP BY kategorie
            -for each group YOU MUSY CHOOSE the agent that is most present
            -KEEP THE ORDER of the contents
            STRUCTURE of ouput:
            1. list of Agent names (your options are: conversational, reader, listener, questionAnswering and GrammarSummary)
            2. list raw content of ONLY the inhalt of the group
            template to use as an example:
            ['conversational', 'reader', ...]
            ['raw content for conversational', 'raw content for reader',...]
            OUTPUT ONLY THE TWO LISTS
            '''

#! THIS IS LANGCHAIN SYNTAX NEED TO MODIFY
def content_extraction(text, prompt):
    try:
        response = client.chat.completions.create(
            model= GPT_MODEL,
            messages=[
                {"role": "system", "content": prompt},  # IN THEORY this prompt works (could use 1.few shots or 2.fine tuning for larger datasets)
                {"role": "user", "content": text}
            ],
            temperature=0.0,
        )
        llm_output = response.choices[0].message.content # == ' list 1\n list2 '
        return response.choices[0].message.content
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e
    
print(content_extraction(all_txt, prompt))