from crewai import Agent, Task, Crew, Process
from agents.tools import KafkaDataTool  # if used
from crewai import LLM
from dotenv import load_dotenv
import os
import time
import json

# Load environment variables from .env file
load_dotenv()


# Load Gemini via Groq (you can also wrap it with a custom provider)
llm = LLM(
    model="openai/gpt-4o-mini",
    api_key=os.getenv('OPENAI_API_KEY'),
    temperature=0.3,
)

kafka_tool = KafkaDataTool()

intent_agent = Agent(
    role="Intent Classifier",
    goal="Understand user's movie query and extract filters",
    backstory="You classify what the user is looking for (genre, theme, etc).",
    tools=[kafka_tool],
    llm=llm
)

user_context_agent = Agent(
    role="User Contextualizer",
    goal="Enhance filters using user preferences",
    backstory="You know the user profile and improve the recommendation filters.",
    tools=[kafka_tool],
    llm=llm
)

movie_recommender_agent = Agent(
    role="Movie Recommender",
    goal="Find the best matching movies",
    backstory="You find movies based on the enhanced filters.",
    tools=[kafka_tool],
    llm=llm
)

summary_agent = Agent(
    role="Summary Presenter",
    goal="Summarize recommendations in a user-friendly way",
    backstory="You explain results clearly to the user.",
    llm=llm
)

intent_task = Task(
    agent=intent_agent,
    description="Extract movie search filters from user query: {input}",
    expected_output="A JSON object with filters like genre, theme, era, etc.",
    verbose=True
)

user_context_task = Task(
    agent=user_context_agent,
    description="Use user profile to enhance search filters: {input}",
    expected_output="Refined filters based on user preferences",
    verbose=True
)

movie_task = Task(
    agent=movie_recommender_agent,
    description="Recommend movies using filters: {input}",
    expected_output="A list of recommended movie titles with reasons",
    verbose=True
)

summary_task = Task(
    agent=summary_agent,
    description="Summarize the final recommendations for user: {input}",
    expected_output="A user-friendly summary explaining the recommendations",
    verbose=True
)

# ✅ Define Crew
movie_crew = Crew(
    tasks=[intent_task, user_context_task, movie_task, summary_task],
    process=Process.sequential,
    verbose=True
)
