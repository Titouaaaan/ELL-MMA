# Project Description:

## Abstract. 
The intersection of Artificial Intelligence (AI) and education
is transforming learning and teaching, with generative AI and large lan-
guage models (LLMs) offering new possibilities. AI and LLMs personal-
ize learning through adaptive study guides, instant feedback, automated
grading, and content creation, making resources more accessible and tai-
lored to individual needs. Notably, LLM-based chatbots, such as Ope-
nAI’s ChatGPT, serve as virtual assistants, ideal for language practice.
However, these chatbots often limit themselves to teaching vocabulary
through role-playing conversations or providing instant feedback based
on model-generated content, which may lead to exposure to inaccuracies.
This overlooks the holistic nature of language learning, which includes
pedagogy, effective methods, reliable content, and a supportive teacher-
student relationship. Relying on a single chatbot is inefficient for the en-
tire learning process. A Multi-Agent System (MAS) is proposed, where
each agent specializes in a specific function, working together to provide
personalized, adaptive learning support. This approach breaks down the
complex learning process into manageable parts. It employs the Busi-
ness Process Model and Notation (BPMN), translated into agent-based
modeling and LLMs to create dynamic, tailored learning environments.
By simulating interactions similar to human tutoring, this model ensures
real-time adjustments to meet each student’s evolving needs.
Our project aims to address these limitations by using language learn-
ing books with robust pedagogical resources as primary references. We
focus on teaching Luxembourgish, adding complexity to our challenges
as it is a low-resource language, ensuring a holistic learning experience.
Our approach employs complex LLM workflows as multi-agent collabo-
rations for reading, conversing, listening, and mastering grammar, based
on GPT-4o, enhanced by Retrieval-Augmented Generation (RAG) and
voice recognition features.

### Keywords: 
LLMs · MAS · BPMN · RAG.

### report link:
https://www.overleaf.com/project/6687d7e743c43e829e68264e

# How to Run the Code
Prerequisites: To run this application, you will need to install the required libraries and tools. Follow the steps below:

 ## 1. Install Required Libraries
This project relies on several Python libraries. You can install them using pip. Make sure you have Python 3.7 or later installed.
-fastapi
-uvicorn
-pydantic
-langgraph/langchain
-openai

## 2. Install Postman
Postman is a popular tool for testing APIs. It allows you to send HTTP requests to your API endpoints and inspect the responses. You can download Postman from the official website:

Download Postman: www.postman.com

## 3. Start the Application
To start the application, use uvicorn, an ASGI server for serving FastAPI applications. Run the following command in your terminal:
'''
uvicorn mainapp:app --reload
'''

mainapp is the name of your Python file without the .py extension (replace it with the appropriate filename if it's different).
app is the FastAPI instance defined in your mainapp.py.
--reload enables auto-reloading, which is useful during development.
The application will start and be accessible at http://127.0.0.1:8000.

## 4. Sending Requests with Postman
Once the application is running, you can interact with it using Postman:

1/ This is done only once to start the backend loop
POST /startConversation: Start the conversation.

URL: http://localhost:8000/startConversation
Method: POST
Body: 
'''
{"startBool": true, "userID": "example_user_id"}
'''

2/ The next three messages are used for user/agent communication
The order must always be: getAIMessages, acknowledgeMessage, userInput

GET /getAIMessage: Retrieve the latest AI message.
URL: http://localhost:8000/getAIMessage
Method: GET

POST /acknowledgeMessage: Send acknowledgment after receiving the AI message.
URL: http://localhost:8000/acknowledgeMessage
Method: POST
Body: 
'''
{"ack": true}
'''

POST /userInput: Send user input after acknowledgment.
URL: http://localhost:8000/userInput
Method: POST
Body: 
'''
{"content": "This is the user input"}
'''

Send the Request:

Click the "Send" button to send the request to your API endpoint.
Review the response in the lower section of Postman.
