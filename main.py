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
        "resumeText": """
<html>
<head>
    <title>John Doe's Resume</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; }
        h1, h2, h3 { color: #333; }
        h1 { font-size: 24px; }
        h2 { font-size: 20px; }
        h3 { font-size: 18px; }
        p { margin: 5px 0; }
        ul { margin: 5px 0; padding-left: 20px; }
    </style>
</head>
<body>
    <h1>John Doe</h1>
    <p>[Your Address]</p>
    <p>[City, State, Zip]</p>
    <p>[Your Email]</p>
    <p>[Your Phone Number]</p>
    <hr>
    <h2>Objective</h2>
    <p>Dedicated and certified AI professional with an engineering background and an MBA, seeking to leverage extensive experience in product operations and machine learning as a Senior Backend Engineer at Aixplain.</p>
    <h2>Professional Experience</h2>
    <h3>Google LLC</h3>
    <p>Product Operations T/ Program Manager – Phones</p>
    <p>Mountain View, CA</p>
    <p>2019-Present</p>
    <ul>
        <li>Managed a third-party team of data scientists to deliver machine learning predictive models for return rates & manufacturing cell qualification, resulting in a 15% reduction in qualification costs.</li>
        <li>Created and executed a new process for management of OpEx product costs, achieving $3.5 million and $7 million in savings for Pixel 2020 and Pixel 2021.</li>
        <li>Drove product headcount resource management for 8 Pixel devices from concept through end of life.</li>
        <li>Managed non-device costs for the Wearables business unit totaling $150 million annually.</li>
    </ul>
    <h3>Hardware, Product Operations MBA Intern – Phones</h3>
    <p>Mountain View, CA</p>
    <p>Summer 2018</p>
    <ul>
        <li>Designed and implemented a new process for Inventory Management Forum for next-gen flagship Pixel phones, resulting in complete automation and an 80% reduction in workload.</li>
    </ul>
    <h3>Philip Morris International</h3>
    <p>Operations Planning Analyst</p>
    <p>Izmir, Turkey</p>
    <p>2015-2017</p>
    <ul>
        <li>Selected for a leadership development assignment to the Turkish affiliate, directing cross-functional teams in resolving a defective data mining tool supporting 40 production lines.</li>
        <li>Launched the first product export project for 23 new products across eight new African markets, representing 15% of annual volume.</li>
    </ul>
    <h2>Education</h2>
    <h3>Columbia University Engineering AI Bootcamp</h3>
    <p>New York, NY</p>
    <p>Certificate in Artificial Intelligence and Machine Learning, June 2024</p>
    <h3>University of Virginia Darden School of Business</h3>
    <p>Charlottesville, VA</p>
    <p>Master of Business Administration, May 2019</p>
    <h3>University of Jordan</h3>
    <p>Amman, Jordan</p>
    <p>Bachelor of Science in Mechatronics Engineering, Jan 2013</p>
    <h2>Key Skills</h2>
    <ul>
        <li>Programming Languages: Python, JavaScript, SQL, C</li>
        <li>Machine Learning: TensorFlow, Keras, Scikit-learn, PyTorch</li>
        <li>Data Science: Pandas, NumPy, Matplotlib, Jupyter</li>
        <li>Cloud Platforms: AWS, Google Cloud</li>
        <li>DevOps & Tools: Docker, Git, Kubernetes</li>
    </ul>
    <h2>Projects</h2>
    <ul>
        <li>Developed an advanced tool for converting spoken language in videos into written subtitles, achieving a Word Error Rate (WER) of 5%.</li>
        <li>Built a full-stack AI-powered application integrating GPT models, reducing API response latency by 40%.</li>
        <li>Designed a Battery Management System for a 10S3P battery pack, improving overall system efficiency by 30%.</li>
    </ul>
</body>
</html>""",
        "coverLetterText": "Hardcoded sample cover letter text...",
    }
