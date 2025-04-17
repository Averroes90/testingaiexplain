import os
from dotenv import load_dotenv
from aixplain.factories import AgentFactory
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware


# 1) Define a Pydantic model that matches the expected input payload
class GenerateRequest(BaseModel):
    jobLink: str
    includeCoverLetter: bool


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


# 3) Example: Another test endpoint
@app.post("/api/generate")
async def generate_docs(request: GenerateRequest):
    # request.jobLink -> str
    # request.includeCoverLetter -> bool

    # For now, return hardcoded data for testing
    return {
        "relevantBackground": [
            "Relevant background #1",
            "Relevant background #2",
            "Relevant background #3",
        ],
        "resumeText": "\\n\\n---\\n\\n**[Your Name]**  \\n[Your Address]  \\n[City, State, Zip]  \\n[Your Email]  \\n[Your Phone Number]  \\n\\n---\\n\\n**Objective**  \\nDynamic and results-driven AI/ML professional with over 7 years of experience in machine learning, product operations, and cross-functional team leadership. Seeking to leverage expertise in designing and implementing machine learning models, particularly in NLP, at aiXplain.\\n\\n---\\n\\n**Education**  \\n\\n**Columbia University Engineering AI Bootcamp**  \\nCertificate in Artificial Intelligence and Machine Learning, Expected June 2024  \\n- Key skills: Python, Pandas, TensorFlow, Keras, Scikit-learn, NLP, Computer Vision  \\n\\n**University of Virginia Darden School of Business**  \\nMaster of Business Administration, May 2019  \\n\\n**University of Jordan**  \\nBachelor of Science in Mechatronics Engineering, Jan 2013  \\n\\n---\\n\\n**Professional Experience**  \\n\\n**Google LLC**  \\n*Product Operations T/ Program Manager – Phones*  \\n2018-Present, Mountain View, CA  \\n- Managed a third-party team of data scientists to deliver machine learning predictive models, achieving a 15% reduction in qualification costs.  \\n- Drove product headcount resource management for 8 Pixel devices from concept through end of life.  \\n- Led early engagement product investigation and feature definition for new Pixel devices.  \\n\\n**Philip Morris International**  \\n*Operations Planning Analyst*  \\n2015-2017, Izmir, Turkey  \\n- Directed cross-functional teams to resolve a defective data mining tool, supporting 40 production lines.  \\n- Supervised the operations team for the revamp of seven strategic products, achieving a 100% hit rate for in-market sales timelines.  \\n\\n---\\n\\n**Projects**  \\n\\n**Auto Transcribe and Translate**  \\n- Developed an advanced tool converting spoken language in videos into written subtitles, achieving a Word Error Rate (WER) of 5%.  \\n- Leveraged Google’s Chirp models and OpenAI’s Whisper for high accuracy in transcription.  \\n\\n**GPT Interface**  \\n- Built a full-stack AI-powered application integrating GPT models, focusing on self-education and skill development.  \\n- Implemented caching with Redis, reducing API response latency by 40%.  \\n\\n---\\n\\n**Technical Skills**  \\n- **Programming Languages:** Python, JavaScript, SQL, C  \\n- **Machine Learning:** TensorFlow, Keras, Scikit-learn, PyTorch  \\n- **Data Science:** Pandas, NumPy, Matplotlib, Jupyter  \\n- **Cloud Platforms:** AWS, Google Cloud  \\n- **DevOps & Tools:** Docker, Git, Kubernetes  \\n\\n---\\n\\n**Certifications**  \\n- Certified AI professional with hands-on experience in building predictive models and managing cross-functional teams.  \\n\\n---\\n\\n**References**  \\nAvailable upon request.",
        "coverLetterText": "Hardcoded sample cover letter text...",
    }
