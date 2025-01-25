import os
from dotenv import load_dotenv  # Import dotenv to load .env variables

# Load environment variables from the .env file
load_dotenv()

# Set the API key from the environment variable
os.environ["AIXPLAIN_API_KEY"] = os.getenv("AIXPLAIN_API_KEY")

from aixplain.factories import AgentFactory
from aixplain.modules.agent import ModelTool

# Create the agent
agent = AgentFactory.create(
    name="Google Search agent",
    description="You are an agent that uses Google Search to answer queries.",
    tools=[
        # Google Search
        ModelTool(model="65c51c556eb563350f6e1bb1"),
    ],
)

# Run the agent
agent_response = agent.run("What's an AI agent?")
print(agent_response)
