from openai import OpenAI
from langchain_core.tools import tool
import json
from langgraph.checkpoint import *
import re

GPT_MODEL = "gpt-4o"

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

    with open('data/relevant_content.txt', 'r') as file: #this will diretcly be the output of the filtered DATA after query
        text = file.read()

    prompt = f'''steps to follow to seprate the text:
            YOU MUST ONLY RETRIEVE CONTENT LINKED TO THE QUERY:
            {query},
            -GROUP BY kapitel
            -then GROUP BY thema
            -then GROUP BY kategorie
            -for each group YOU MUSY CHOOSE the agent that is most present
            -KEEP THE ORDER of the contents
            STRUCTURE of ouput:
            1. list of Agent names (your options are: conversational, reader, listener, questionAnswering and GrammarSummary)
            2. list raw content of ONLY the inhalt of the group 
            DO NOT PUT COMMAS , IN THE RAW CONTENT
            MAKE SURE that each agent's content FITS IN ONE ELEMENT OF THE LIST
            THE TWO LISTS SHOULD BE OF THE SAME SIZE
            template to use as an example:
            [conversational, reader, ...]
            ['raw content for conversational', 'raw content for reader',...]
            OUTPUT ONLY THE TWO LISTS
            '''
    try:
        response = OpenAI().chat.completions.create(
            model= GPT_MODEL,
            messages=[
                {"role": "system", "content": prompt},  # IN THEORY this prompt works (could use 1.few shots or 2.fine tuning for larger datasets)
                {"role": "user", "content": text}
            ],
            temperature=0.0,
        )
        llm_output = response.choices[0].message.content # == ' list 1\n list2 '
        matches = re.findall(r'\[([^]]+)\]', llm_output)
        agents = matches[0].split(',')
        agents = [s.replace(' ', '') for s in agents]
        contents = matches[1].split(',')
        # print(type(list1), list1)
        # print(type(list2), list2)
        global global_prompts_list 
        global_prompts_list = contents

        global agent_activation_order
        agent_activation_order = agents
        #check that the two lists are properly configured
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
def getTutorPrompt() -> str:
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

    '''
    print('Tool not writing anything yet but called properly!') #debugging tool to see something happenend
    return agentName + 'FINAL REPORT placeholder for the actual report'