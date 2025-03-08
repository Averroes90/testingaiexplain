import os
from dotenv import load_dotenv
from aixplain.factories import AgentFactory
from aixplain.modules.agent import ModelTool

# Load environment variables from the .env file
load_dotenv()

os.environ["AIXPLAIN_API_KEY"] = os.getenv("AIXPLAIN_API_KEY")


# Define a function to create and run the agent
def run_agent(query: str):
    agent = AgentFactory.create(
        name="Google Search agent",
        description="You are an agent that uses Google Search to answer queries.",
        tools=[
            ModelTool(model="65c51c556eb563350f6e1bb1"),
        ],
    )
    return agent.run(query)
