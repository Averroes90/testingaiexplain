import os
from dotenv import load_dotenv
from aixplain.factories import AgentFactory
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from custom_aixplain.pipelines import first_pass_pipeline


# 1) Define a Pydantic model that matches the expected input payload
class GenerateRequest(BaseModel):
    url: str
    doc_type: list[str]
    style: list[str]
    page_count: list[str]


# Load environment variables from the .env file
load_dotenv()

os.environ["AIXPLAIN_API_KEY"] = os.getenv("AIXPLAIN_API_KEY")


# Define a function to create and run the agent
# def run_agent(query: str):
#     agent = AgentFactory.create(
#         name="Google Search agent",
#         description="You are an agent that uses Google Search to answer queries.",
#         tools=[
#             ModelTool(model="65c51c556eb563350f6e1bb1"),
#         ],
#     )
#     return agent.run(query)


app = FastAPI()
# Set all CORS enabled origins
origins = [
    "http://localhost:5173",  # or whatever your frontend's origin is
    "http://127.0.0.1:3000",
    # ...add more if needed
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # e.g., ["POST", "GET", "OPTIONS"], or "*"
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    return {"status": "OK"}


# 2) Example: Hello World Endpoint returning a string
@app.get("/hello")
async def hello():
    return {"message": "Hello from your AI server!"}


@app.post("/api/generate")
async def generate_docs(request: GenerateRequest):
    # Now you have:
    # request.url        -> str
    # request.doc_type   -> List[str]
    # request.style      -> List[str]
    # request.page_count -> List[str]

    # Pass the data to your pipeline function:
    output_data = first_pass_pipeline(
        url=request.url,
        doc_types=request.doc_type,
        styles=request.style,
        page_counts=request.page_count,
    )

    # Return the pipeline’s output directly
    return output_data
