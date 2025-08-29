from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.conditions import TextMentionTermination 
from dotenv import load_dotenv
from autogen_agentchat.base import TaskResult
from autogen_agentchat.ui import Console
import os


load_dotenv()

async def team_Config(plastic_type="PET Bottles, 10 tons/day, no constraints"):

    model_client = OpenAIChatCompletionClient(model="gemini-2.5-flash",api_key='') #Enter you API key from Gemini

    # Defining our Agent
    # 1. User Agent
    # 2. Process Analyzer Agent
    # 3. Sustainability Evaluator Agent

    plastic_type = plastic_type

    User = UserProxyAgent(
        name = "User",
        description=f"An agent that simulates a human user (e.g., a plant engineer or policymaker) who wants to decide the best recycling pathway for {plastic_type}.",
        input_func=input
    )

    Process_Analyzer = AssistantAgent(
        name="Process_Analyzer",
        model_client=model_client,
        description=f"Technical expert in chemical process engineering for {plastic_type} type of polymer/plastic.",
        system_message=f'''
        You are a Technical expert in chemical process engineering for {plastic_type} type of polymer/plastic.
        Responsibilities:

Evaluate possible recycling technologies for the given polymer:

Mechanical recycling (shredding, remelting).
Chemical depolymerization (glycolysis, hydrolysis, methanolysis).
Pyrolysis/gasification.
Incineration with energy recovery.

Provide technical details:
Yield (%) of recycled product.
Required operating conditions (temperature, pressure, catalyst).
Energy demand (kWh/ton or MJ/ton).

Pass results to Assistant Agent 2 for sustainability evaluation.

Example Output:
“For 10 tons/day PET bottles, glycolysis at 200 °C with zinc acetate catalyst gives ~85% yield, energy demand 2.1 GJ/ton.”
        After asking 3 questions, say 'TERMINATE' at the end of the interview.
        Make question under 50 words.
    '''
    )

    

    Sustainability_Evaluator = AssistantAgent(
        name="Sustainability_Evaluator",
        model_client=model_client,
        description=f"An AI agent that is an Environmental and economic decision-maker for the processing of {plastic_type} plastic through the method(s) suggested by Process_Analyzer.",
        system_message=f'''
        Environmental and economic decision-maker for the processing of {plastic_type} plastic through the method(s) suggested by Process_Analyzer.
        Responsibilities:

Assess the process proposed by Process_Analyzer on:
CO₂ footprint (kg CO₂/ton).
Energy efficiency (% of input energy recovered).
Circularity score (how well it reintroduces material into the economy).
Cost/ton of waste treated.
Compare against user's constraints (from User Agent).
Suggest modifications:
Switch methods (e.g., chemical depolymerization instead of pyrolysis).
Adjust operating conditions (e.g., lower temperature to cut energy demand).
Add pre-treatment steps (e.g., cleaning, sorting).
Send feedback back to Process_Analyzer for re-analysis.

Example Output:
“At 200 °C glycolysis, CO₂ emissions = 1.2 tons/day. Reducing T to 180 °C cuts emissions by 15% with minimal yield loss. Recommend adjustment.”
    '''
    )

    terminate_condition = TextMentionTermination(text="TERMINATE")

    team = RoundRobinGroupChat(
        participants=[User, Process_Analyzer, Sustainability_Evaluator],
        termination_condition=terminate_condition,
        max_turns=20
    )
    return team


async def analyzer(team):
# Running the analysis
    async for message in team.run_stream(task=''):
        if isinstance(message,TaskResult):
            message = f'Task Completed: {message.stop_reason}'
            yield message
        else:
            message = f'{message.source}: {message.content}'
            yield message



