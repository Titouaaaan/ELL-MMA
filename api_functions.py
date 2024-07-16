from fastapi import FastAPI, Body

app = FastAPI()

@app.get("/")
def welcomeMessage() -> dict:
    return {"message": "welcome to the chatbot app!!"}

@app.get("/sendAIMessage/{message}")
def sendAIMessage(message: str) -> dict:
    return {"message": message}

@app.post("/")
def getHumanMessage(input: str) -> dict:
    return {"response": input}