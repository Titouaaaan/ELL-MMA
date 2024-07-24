# Project Description:

## Abstract. 
The intersection of Artificial Intelligence (AI) and education
is transforming learning and teaching, with generative AI and large language models (LLMs) offering new possibilities. 
AI and LLMs personalize learning through adaptive study guides, instant feedback, automated
grading, and content creation, making resources more accessible and tailored to individual needs. 
Notably, LLM-based chatbots, such as OpenAI’s ChatGPT, serve as virtual assistants, ideal for language practice.
However, these chatbots often limit themselves to teaching vocabulary
through role-playing conversations or providing instant feedback based
on model-generated content, which may lead to exposure to inaccuracies.
This overlooks the holistic nature of language learning, which includes
pedagogy, effective methods, reliable content, and a supportive teacher-
student relationship. Relying on a single chatbot is inefficient for the entire learning process. A Multi-Agent System (MAS) is proposed, where
each agent specializes in a specific function, working together to provide
personalized, adaptive learning support. This approach breaks down the
complex learning process into manageable parts. It employs the Business Process Model and Notation (BPMN), translated into agent-based
modeling and LLMs to create dynamic, tailored learning environments.
By simulating interactions similar to human tutoring, this model ensures
real-time adjustments to meet each student’s evolving needs.
Our project aims to address these limitations by using language learning books with robust pedagogical resources as primary references. 
We focus on teaching Luxembourgish, adding complexity to our challenges
as it is a low-resource language, ensuring a holistic learning experience.
Our approach employs complex LLM workflows as multi-agent collaborations for reading, conversing, listening, and mastering grammar, based
on GPT-4o, enhanced by Retrieval-Augmented Generation (RAG) and voice recognition features.

### Keywords: 
LLMs · MAS · BPMN · RAG.

### report link:
You can request access to read the paper written for this project:
https://www.overleaf.com/project/6687d7e743c43e829e68264e

# Installation
Follow these steps to set up the project on your local machine:
```
git clone https://github.com/Titouaaaan/ELL-MMA.git
cd ELL-MMA
```

# Running the Application
Note: This project is currently under development and should be considered a prototype. It is not yet a finished product and may contain incomplete features and bugs that will be addressed in future updates.

## 1. Create environment
This will allow you to keep the project dependencies separate and not interfere with other Python projects or the global Python installation on your machine.

Open the command prompt, and go into the project's directory. Create the virtual environment by running:
```
python -m venv env_name
```
Replace 'env_name' by the name you want to give to your venv.
To activate the virtual environment, use the following command:
```
.\env_name\Scripts\activate
```

After running this, you should see (env) appear at the beginning of your command prompt line, indicating that the virtual environment is active.

## 2. Install Required Libraries
This project relies on several Python libraries. You can install them using pip. Make sure you have Python 3.7 or later installed.
- fastapi
- uvicorn
- pydantic
- langgraph/langchain
- openai

to do so run the following command:

```
pip install -r requirements.txt
```

REMINDER: make sure you have a .env file at the root of the project and add your OPENAI_API_KEY

## 3. Install Postman (OPTIONAL)
Postman is a popular tool for testing APIs. It allows you to send HTTP requests to your API endpoints and inspect the responses. You can download Postman from the official website:
This step is only useful if you want to test the API calls of the project.

Download Postman: www.postman.com

## 4. Start the Application
To start the application, use uvicorn, an ASGI server for serving FastAPI applications. Run the following command in your terminal:
```
uvicorn mainapp:app --reload
```

mainapp is the name of your Python file without the .py extension (replace it with the appropriate filename if it's different).
app is the FastAPI instance defined in your mainapp.py.
--reload enables auto-reloading, which is useful during development.
The application will start and be accessible at http://127.0.0.1:8000.
You can test out the app by clicking 'start conversation' (input the user ID 001 for instance when asked in the pop menu) and sending messages to the AI by clicking the 'send' button after writing your message.

# Contact
If you have any questions or need further assistance, please feel free to contact us:
- Titouan Guerin: Titouan.Guerin@etu.sorbonne-universite.fr
- Meryem Elfatimi: mlle.elfatimi.meryem@gmail.com