from openai import OpenAI
from langchain_core.tools import tool
import json
from langgraph.checkpoint import *
import re
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings
import chromadb
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from state import message_state
import ast


GPT_MODEL = "gpt-4-turbo"

@tool
def getFiles(userID: str) -> str:
    ''' read the user profile, user progress file and the curriculum '''
    #init the values we need as None to check later if we were able to retrieve data
    #ideally find more efficient way to do this
    profile = None
    progress = None

    # retrieving the user's profile NOT USEFUL RN
    with open('data/user_profile_file.json', 'r') as json_file:
        profile = json.load(json_file).get(userID, None)
    if profile == None: #in case we couldnt find user profile
        return f'User profile not existant for user {userID}. Please double check user ID'
    
    #retrieving the user progress
    with open('data/user_progress_file.json', 'r') as json_file:
        progress = json.load(json_file).get(userID, None)

    if progress == None: #in case we couldnt find user progress
        return f'User progress not existant for user {userID}. Please double check user ID'  

    with open('data/curriculum.txt', 'r') as file:
        curriculum = file.read()
    if not curriculum:
        return f'Could not retrieve any text from curriculum.txt, please double check file contents'

    # testing output for debugging
    # print(f'User profile {profile} \nUser progress: {progress} \nCurriculum: {curriculum}')

    return f'User profile {profile} \nUser progress: {progress} \nCurriculum: {curriculum}'

@tool #! right now we will not implement this
def updateUserPreferences(userID: str, newPreferences: list) -> str:
    ''' tool to update the entries in user_profile_file for a specific user'''
    with open('data/user_profile_file.json', 'r') as json_file:
        data = json.load(json_file)
    
    if userID in data:
        data[userID]['preferences'] = newPreferences
    else:
        print(f"No user found with ID: {userID}")
        return
    
    with open('data/user_profile_file.json', 'w') as file:
        json.dump(data, file, indent=4)

    return 'Successfully updated the user profile'

@tool
def getChunks(query: str) -> str:
    ''' use an llm to seperate the texts '''
    #print('seperating chunks...')
    ''' add: fulldata -> apply query -> get all_contents (filtered in this case)'''

    model_name = "BAAI/bge-large-en-v1.5"
    encode_kwargs = {'normalize_embeddings': True} # set True to compute cosine similarity
    model_norm = HuggingFaceBgeEmbeddings(
        model_name=model_name,
        model_kwargs={'device': 'cpu'},
        encode_kwargs=encode_kwargs
    )
    embeddings = model_norm
    persist_directory = "data/bge_test_"
    vectordb = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})
    docs = retriever.invoke(query)

    new_docs = '' #change name
    for doc in docs:
        new_docs += doc.page_content

    print('--retrieved docs: \n')
    print(new_docs)

    print('\n\n')

    message_state.update_content('succesfully retrieved content!', 'system')
    # # WAIT FOR ACK TO SEE IF CLIENT RECIEVED AIMESSAGE
    # await message_state.wait_for_acknowledgment()

    prompt = f'''for this query : {query} you decide witch chunk is adequate and relevant . 
    A chunk of content is a raw block of test preceded by a kapitel and a thema.
    For each chunk, assign an agent to this chunk. Keep ALL OF THE INHALT of a content block
    Agent names must be strictly (exact same spelling) one of 'conversational', 'listening', 'reader', 'questionAnswering', 'grammarSummary'
    Make sure they are strings 

    output template:
    [agent1, agent2, agent3 ...] 
    [content1, content2, content3 ...] (raw content from the retrieved docs), each contentN needs to match agentN)

    IT IS MANDATORY THAT both lists are THE SAME SIZE
    OUTPUT ONLY THE TWO LISTS
            '''
    try:
        response = OpenAI().chat.completions.create(
            model= GPT_MODEL,
            messages=[
                {"role": "system", "content": prompt},  # IN THEORY this prompt works (could use 1.few shots or 2.fine tuning for larger datasets)
                {"role": "user", "content": new_docs}
            ],
            temperature=0.0,
        )
        print("\n\n\n the output \n\n\n ")
        print(response.choices[0].message.content)
        print("\n\n\n")

        output_string = response.choices[0].message.content # == ' list 1\n list2 '
        # Applying regex patterns to extract the lists
        list1_matches = re.findall(r'"\s*([^"]+?)\s*"', output_string.splitlines()[0])
        list2_matches = re.findall(r'"\s*([^"]+?)\s*"', output_string.splitlines()[1])

        global agent_activation_order

        global global_prompts_list

        # Using ast.literal_eval to safely evaluate the lists
        agent_activation_order = ast.literal_eval('[' + ', '.join(f'"{m}"' for m in list1_matches) + ']')
        global_prompts_list = ast.literal_eval('[' + ', '.join(f'"{m}"' for m in list2_matches) + ']')
        

        #check that the two lists are properly configured
        print('Testing getChunks output:')
        for elem in global_prompts_list:
            print('-----')
            print(elem)
        print(agent_activation_order)

        assert len(global_prompts_list) == len(agent_activation_order), f'should have as many topics as tutor lessons!, {len(global_prompts_list), len(agent_activation_order)}'
        return 'continue'
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e
    
''' TOOLS FOR THE TRACKER 
'''
@tool
def start_signal() -> str:
    ''' function to determine what agent need to be woken up
    ex: agentName <-> the ID present in the shared list between orchestrator and tracker
    output -> "conversational" <-> used by the router to know where to go in the graph
    '''
    #print(agent_activation_order)
    if len(agent_activation_order) != 0: #if there are agents left to execute
        agent = agent_activation_order[0]
        assert type(agent) == str, f'type of agent incorrect (should be string but got {type(agent)})'
        #print(agent)
        return agent
    else: #list is empty here
        return 'no_more_lesson'
    
''' tool function for all tutor agents to retrieve their prompts 
this function will probably need some tuning and tests to ensure there are no problems coming from the orchester
'''
@tool 
def getLearningContent() -> str:
    ''' return the first element of the global prompts list '''
    prompt = global_prompts_list[0] # -> 'Content' -> retrive content
    assert type(prompt) == str, 'prompt is not a string...'
    # print(f'BEFORE RETRIEVAL: \ncontents = {global_prompts_list} \nagents = {agent_activation_order}')
    global_prompts_list.pop(0)
    agent_name = agent_activation_order[0]
    # debugging
    # print(f"Retrieved content {prompt} for agent {agent_name}")
    agent_activation_order.pop(0)
    #print(f'AFTER RETRIEVAL: \ncontents = {global_prompts_list} \nagents = {agent_activation_order}')
    return agent_name + ' lesson: ' + prompt #what is gonna be returned to the tutor agent

@tool
def create_progress_report(agentName: str, reportAndFeedback=None) -> str: 
    ''' write all the reports in file 'address' 
    THIS TOOL DOES NOT AFFECT THE PROCESS IN ANY WAY, SINCE THE LEARNING PROCESS ONLY STOPS WHEN THERE ARE NO MORE AGENTS
    convert reportandfeedback in json format
    write/add to global user_progress file this string
    return str -> Updated user progress file
    The tutor has succesfully updated the user progress file! 
    user_progress_file structure:
    #this 
    {
        "UserID": "id", 
        "Kapitel": "1",
        "Thema": "Moien",
        "agent": "conversational",
        "goals": "explain basic greetings",
        "feedback": "the user learned ......"
    }
    IGNORE THIS
    '''
    return agentName + 'FINAL REPORT'