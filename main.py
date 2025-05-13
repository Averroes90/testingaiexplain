import os, io, uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from custom_aixplain.pipelines import first_pass_pipeline
from utils.utils import load_object_from_pickle
from my_validators.schema import GenerateRequest, DSCallback
import asyncio
from builders import fetch_docx
import time, jwt
import secrets
from settings import STORAGE_DIR, redis_cli, sign_full, JWT_SECRET_KEY
import httpx
from versioning import _write_version

# from jwt_helpers import sign_cfg
from seed_placeholder import ensure_placeholder
from contextlib import asynccontextmanager

# Load environment variables from the .env file
load_dotenv()

os.environ["AIXPLAIN_API_KEY"] = os.getenv("AIXPLAIN_API_KEY")
BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
PUBLIC_BASE = os.getenv("BACKEND_PUBLIC_URL", "http://backend:8000")
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ---------- startup ----------------------------------------------------
    ensure_placeholder()  # create file + Redis hash if missing
    yield
    # ---------- shutdown ---------------------------------------------------
    # (nothing to clean up right now, so just return)
    # If you add cleanup logic later, put it *after* the yield.


app = FastAPI(lifespan=lifespan)
# Set all CORS enabled origins
origins = [
    "http://localhost:5173",  # or whatever your frontend's origin is
    "http://127.0.0.1:3000",
    "http://localhost:82",  # OnlyOffice Document Server
    # ...add more if needed
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # e.g., ["POST", "GET", "OPTIONS"], or "*"
    allow_headers=["*"],
)
app.mount(
    "/files",
    StaticFiles(directory="storage/docs", html=False),
    name="files",
)


@app.get("/health")
async def health_check():
    return {"status": "OK"}


# 2) Example: Hello World Endpoint returning a string
@app.get("/hello")
async def hello():
    return {"message": "Hello from your AI server!"}


# @app.post("/api/generate")
# async def generate_docs(request: GenerateRequest):
#     # Convert the Pydantic model instance into a plain dict:
#     # {
#     #   "url": "...",
#     #   "doc_type": [...],
#     #   "style": [...],
#     #   "page_count": [...]
#     # }
#     pipeline_input = request.model_dump()
#     html_resume = load_object_from_pickle(f"pkl/html_resume.pkl")
#     # Now pass that single dict to your pipeline function directly

#     output_data = {
#         "job_info": {
#             "company": "aiXplain",
#             "title": "Senior Backend Engineer",
#             "summary": "The Senior Backend Engineer will design and create services and system architecture for projects, improve code quality through writing unit tests, automation and performing code reviews, and collaborate with a multidisciplinary team. They will also participate in brainstorming sessions and contribute ideas to technology, algorithms and products. The candidate should have 7+ years of recent hands-on coding and software design experience, a Bachelor’s degree or more in Computer Science or a related field, experience with all phases of the software development life cycle, best practices, and Agile software development. They should also have experience using Django, solid OOP and software design knowledge, strong familiarity with web server technologies including Nginx, Apache, and J2EE, experience with Java or Ruby, and knowledge of database systems and NoSQL databases such as DynamoDB. Experience deploying machine learning models is a plus.",
#         },
#         "background_info": {
#             "professional_experience": "2018-Present\tGoogle LLC\nProduct Operations T/ Program Manager – Phones (2019-Present) Mountain View, CA\nManaged oversees third party team of data scientists to deliver machine learning predictive models for return rates & manufacturing cell qualification resulting in reduction of 15% in qualification costs\nCreated and executed new process for management of OpEx product costs in tandem with cross-regional team resulting in $3.5 million and $7 million in savings for Pixel 2020 and Pixel 2021\nDrove product headcount resource management for 8 Pixel devices from concept through end of life\nManaged non-device costs for Wearables business unit totaling $150 million annually\nLed early engagement Product investigation and feature definition for a new segment Pixel device\nHardware, Product Operations MBA Intern – Phones (Summer 2018) Mountain View, CA\nDesigned and implemented new process for Inventory Management Forum for next-gen flagship Pixel phones resulting in complete automation of the process and 80% reduction in work load\nEstablished standard Key Part Release and Master Production Schedule model and input templates\nCompletely revamped Clear to Build management process leading to strategic SKU-level visibility\n2013-2017\tPhilip Morris International\nOperations Planning Analyst (2015-2017) Izmir, Turkey\nSelected out of 50 candidates for leadership development assignment to the Turkish affiliate, the cluster head for EEMA region and the largest CPG in Turkey\nDirected cross-functional domestic and international project team in successful resolution of a defective company-wide data mining and reporting tool in support of 40 production line operations representing annual volume of 70 billion sticks Led cross functional effort across five teams to successfully launch the first product export project for 23 new products across eight new African markets representing 15% of annual volume\nSupervised the operations team for the revamp of seven strategic products including Marlboro and L&M brands achieving 100% hit rate for in-market-sales timeline requirements\nProcess Engineer (2014-2015) Amman, Jordan\nLed two five-person teams on two production facility operations improvement projects setting four new all-time records and achieving recognition for two key performance indicators\nInitiated factory inventory management and categorization process for spare parts and raw materials resulting in the reduction local spare parts inventory by $1 million representing 40% of total inventory; received Philip Morris International Above and Beyond the Call of Duty award\nElectrical Maintenance Engineer (2013-2014) Amman, Jordan\nDesigned and installed of track and trace weight measurement system",
#             "education": "Columbia University Engineering AI Bootcamp\tNew York, NY\nCertificate in Artificial Intelligence and Machine Learning, June 2024\nKey skills: Python, Pandas, TensorFlow, Keras, Scikit-learn, NLP, Computer Vision\nProjects: Developed a sentiment analysis model using NLP techniques; built a convolutional neural network for image classification; analyzed machine failure data using multivariate analysis to identify key contributors\nUniversity of Virginia Darden School of Business\tCharlottesville, VA\nMaster of Business Administration, May 2019\nGMAT: 720\nDarden Foundation Scholarship: Awarded merit-based scholarship recognizing academic excellence\nClubs: Consulting, Technology, Finance, Adam Smith Society, and Soccer\nUniversity of Jordan\tAmman, Jordan\nBachelor of Science in Mechatronics Engineering, Jan 2013\nKey skills: Embedded Systems, Microcontroller Programming, Assembly Language, Robotics\nVolunteering: lecturer for Assembly & Microprocessors and Design of Embedded Systems classes",
#             "other_resume": [
#                 "Certified AI professional with an engineering background and an MBA, transitioning from product operations to machine learning operations and engineering. Hands-on experience in building predictive models, big data manipulation, and managing cross-functional teams",
#                 "Programming Languages: Python, JavaScript, SQL, C\nMachine Learning: TensorFlow, Keras, Scikit-learn, PyTorch\nData Science: Pandas, NumPy, Matplotlib, Jupyter\nCloud Platforms: AWS (SageMaker, EC2), Google Cloud\nDevOps & Tools: Docker, Git, Kubernetes, Vue.js",
#                 "Auto Transcribe and Translate (Mar 2024 - present)\nPython, NLP, Jupyter, spaCy, pydub, PyTorch, OpenAI API, Google STT API\nDeveloped an advanced tool converting spoken language in videos into written subtitles in any desired language\nAchieved a Word Error Rate (WER) of 5%, improving transcription accuracy by\xa020%\xa0over baseline models.\nLeveraged Google’s Chirp models and OpenAI’s Whisper for broad language coverage and high accuracy, implementing DTW (Dynamic Time Warping) for effective subtitle alignment and consolidation\nImplemented backend AI prompting techniques to refine transcriptions, reducing errors by 15% and enhancing clarity and readability.\nGPT Interface (Jun 2023 - present)\nVue.js, Flask, FastAPI, Webpack, Pydantic, SQLite, SQLAlchemy, Poetry, Redis, OpenAI API, Gemini API\nBuilt a full-stack AI-powered application integrating GPT models using OpenAI and Gemini APIs.\nFocused on self-education and skill development, mastering end-to-end development from frontend (Vue.js) to backend (Flask, FastAPI, SQLAlchemy)\nImplemented caching with Redis, reducing API response latency by 40% and decreasing server load by 30% for efficient model response handling and scalability.\nBattery Management System (Jan 2023 - Jun 2023)\nPython, C, STM32, ADC, FRAM, Wi-Fi, Kalman Filter, Active Cell Balancing\nDesigned a BMS for a 10S3P battery pack utilizing Epoch 21700 cells with active cell balancing and advanced protection mechanisms, increasing battery life by 20% and reducing cell imbalance by 25%.\nDeveloped a hybrid memory management system using the MCU flash, FRAM, and an SD card to manage high-frequency data logging and efficient communication to cloud servers\nOptimized the system for real-time data handling, advanced cell protection, and wireless updates, improving overall system efficiency by 30% and reducing maintenance time by 40%.",
#             ],
#             "essays": [
#                 "Dear Hiring Team at Roblox,\n\nI am excited to apply for the Senior Product Manager role in the Creator organization at\nRoblox.\n---\nWith a multidisciplinary background in AI, machine learning, and platform\ndevelopment, combined with a passion for empowering creators and reimagining digital\nexperiences, I am eager to contribute my expertise to your mission of connecting people\nthrough immersive 3D experiences.\n\n\n---\nRecognizing the transformative potential of generative AI, I transitioned my career toward this\nﬁeld, completing an AI and Machine Learning Bootcamp at Columbia Engineering.\n---\n•Custom ML Models: Designed a speech-to-text transcription system that improved baseline\naccuracy by 20%, leveraging ﬁne-tuning and domain-speciﬁc data.\n\n",
#                 "Collaborating with talented engineers, designers, and analysts to\ndeliver tools that empower users and advance the platform’s capabilities would be an\nincredible challenge that I am ready to embrace.\n\n",
#                 "I have led\nself-driven projects, such as an AI-powered transcription tool with 20% improved accuracy\nand a full-stack AI-powered application integrating GPT models.\n---\nAt Google, I managed cross-functional teams to deploy machine-learning models, achieving\noperational cost savings of over $10 million and optimizing processes at scale.\n---\nThese projects\nhoned my skills in coordinating diverse teams, managing complex timelines, and delivering\nresults in fast-paced environments.",
#                 "Dear Hiring Team at UBS,\n\nI am excited to apply for the Product Manager, GenAI Products position at UBS.\n---\nThis\nrealization led me to upskill and reskill deliberately, completing an AI and Machine Learning\nBootcamp at Columbia Engineering, where I gained hands-on experience with frameworks like\nTensorFlow and PyTorch.\n---\nI complemented this formal learning with self-driven projects,\nincluding the development of an AI-powered interface integrating multiple AI models and APIs.\n",
#                 "Dear Hiring Team,\n\nI am excited to apply for the GenAI/Machine Learning Technical Project Manager position\nwithin Deloitte’s Human Capital Oﬀering Portfolio.\n---\nThe opportunity to spearhead generative AI\ninitiatives that enhance organizational performance and engagement aligns closely with my\ntechnical expertise, leadership experience, and passion for leveraging AI to solve real-world\nchallenges.\n\n\n---\nOver the past 18 months, I have transitioned into a more technical role in AI and machine\nlearning, recognizing the transformative potential of this ﬁeld.\n---\nDuring this time, I completed a\ncertiﬁcation in AI and machine learning at Columbia Engineering, where I gained hands-on\nexperience with frameworks like TensorFlow, PyTorch, and OpenAI’s GPT models.",
#             ],
#         },
#         "resume": html_resume,
#         "cover_letter": '```html\n<!DOCTYPE html>\n<html>\n<head>\n    <style>\n        body {\n            font-family: Arial, sans-serif;\n            margin: 0;\n            padding: 0;\n            font-size: 12pt;\n            line-height: 1.15;\n        }\n        .header {\n            text-align: center;\n            font-size: 16pt;\n            font-weight: bold;\n            margin-bottom: 20px;\n        }\n        .section {\n            margin-bottom: 10px;\n        }\n        .section h2 {\n            font-size: 14pt;\n            font-weight: bold;\n            margin-bottom: 5px;\n        }\n        .section p {\n            margin: 0;\n        }\n        .bullet-list {\n            margin: 0;\n            padding-left: 20px;\n        }\n        .bullet-list li {\n            margin-bottom: 5px;\n        }\n    </style>\n</head>\n<body>\n    <div class="header">\n        <p>[Your Name]</p>\n        <p>[Your Contact Info] | [Your Address]</p>\n    </div>\n    <div class="section">\n        <p>Dear Hiring Team at aiXplain,</p>\n    </div>\n    <div class="section">\n        <p>I am writing to express my interest in the Senior Backend Engineer position. With a multidisciplinary background in AI, machine learning, and platform development, combined with a passion for empowering creators and reimagining digital experiences, I am eager to contribute my expertise to your mission.</p>\n    </div>\n    <div class="section">\n        <h2>Education</h2>\n        <p>I hold a Bachelor of Science in Mechatronics Engineering from the University of Jordan and an MBA from the University of Virginia Darden School of Business. Recently, I completed an AI and Machine Learning Bootcamp at Columbia Engineering, where I gained hands-on experience with Python, TensorFlow, Keras, and Scikit-learn. This formal learning was complemented by self-driven projects, including the development of an AI-powered interface integrating multiple AI models and APIs.</p>\n    </div>\n    <div class="section">\n        <h2>Professional Experience</h2>\n        <p>In my current role at Google, I manage a third-party team of data scientists to deliver machine learning predictive models, achieving operational cost savings of over $10 million and optimizing processes at scale. I have also led projects such as:</p>\n        <ul class="bullet-list">\n            <li>An AI-powered transcription tool with 20% improved accuracy</li>\n            <li>A full-stack AI-powered application integrating GPT models</li>\n        </ul>\n        <p>These experiences have honed my skills in coordinating diverse teams, managing complex timelines, and delivering results in fast-paced environments.</p>\n    </div>\n    <div class="section">\n        <h2>Skills</h2>\n        <p>I am confident that my experience with Python, Django, and Java, along with my familiarity with web server technologies including Nginx, Apache, and J2EE, aligns well with the requirements of the Senior Backend Engineer role. My knowledge of database systems and NoSQL databases such as DynamoDB, coupled with my experience deploying machine learning models, will allow me to contribute effectively to your team.</p>\n    </div>\n    <div class="section">\n        <p>I am excited about the opportunity to participate in brainstorming sessions and contribute ideas to technology, algorithms, and products at aiXplain. I look forward to the possibility of bringing my unique blend of skills and experience to your team.</p>\n    </div>\n    <div class="section">\n        <p>Thank you for considering my application.</p>\n        <p>Sincerely,</p>\n        <p>[Your Name]</p>\n    </div>\n</body>\n</html>\n```',
#     }
#     # Return the pipeline's result to the front end
#     return output_data
#     # Now pass that single dict to your pipeline function directly
#     output_data = first_pass_pipeline(pipeline_input)


# 3.1  generate endpoint --------------------------------------------------- #
@app.post("/api/generate")
async def generate_docs(request: GenerateRequest):
    """
    Runs first_pass_pipeline in a thread to avoid blocking the event loop.
    Returns { "resume": {doc_id, doc_url}, ... }
    """
    try:
        result = await asyncio.to_thread(first_pass_pipeline, request.model_dump())
    except Exception as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    return result


# 3.2  doc streaming endpoint (OnlyOffice consumes this) ------------------ #
@app.get("/api/docs/{doc_id}")
async def get_doc(doc_id: str):
    buf = fetch_docx(doc_id)
    if buf is None:
        raise HTTPException(404, "expired or unknown key")

    return StreamingResponse(
        io.BytesIO(buf),
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{doc_id}"'},
    )


@app.get("/api/docs/{doc_id}/view")
async def view_doc(doc_id: str, request: Request):
    meta = redis_cli.hgetall(f"doc:{doc_id}") or HTTPException(404, "unknown document")

    version = int(meta["version"])
    filename = f"v{version}.docx"
    file_url = f"{PUBLIC_BASE}/files/{doc_id}/{filename}"
    callback = f"{PUBLIC_BASE}/api/docs/{doc_id}/callback"
    doc_key = meta["dsKey"]  # ≤20 chars

    cfg = {
        # ── minimum fields the editor itself needs
        "fileUrl": file_url,  # legacy field, still read by DS
        "fileName": filename,
        "key": doc_key,
        "callbackUrl": callback,
        # ── block the JWT-validator checks
        "document": {
            "title": filename,
            "fileType": "docx",
            "key": doc_key,
            "url": file_url,
        },
        "editorConfig": {
            "callbackUrl": callback,
            # …add lang, mode, user, etc. if you want
        },
        # permissions, userInfo, etc. may be added here too
    }

    cfg["token"] = sign_full(cfg)  # ← one-shot signature
    # Log token info for debugging
    print(f"Token type: {type(cfg['token'])}")
    print(f"Token preview: {cfg['token'][:60]}...")
    print(f"Token length: {len(cfg['token'])}")

    # Verify if token is correctly formatted
    parts = cfg["token"].split(".")
    if len(parts) != 3:
        print("Warning: Token does not have 3 parts as expected in JWT format")
    return cfg


@app.post("/api/docs/{doc_id}/callback")
async def ds_callback(
    doc_id: str,
    payload: DSCallback,
    authorization: str | None = Header(None),  # DS also sends it as a header
):
    # ── 0. validate JWT ───────────────────────────────────────────
    token = authorization or payload.token
    try:
        jwt.decode(token, JWT_SECRET_KEY, algorithms=["HS256"])
    except Exception:
        raise HTTPException(401, "Invalid JWT")

    # ── 1. ignore statuses that are not 'finished-save' / 'force-save'
    if payload.status not in (2, 6):
        return {"error": 0}

    # ── 2. fetch meta and new content exactly as before ───────────
    meta = redis_cli.hgetall(f"doc:{doc_id}")
    if not meta:
        raise HTTPException(404, "unknown document")

    new_bytes = httpx.get(payload.url, timeout=20).content
    new_ver = int(meta["version"]) + 1
    path = _write_version(doc_id, new_ver, new_bytes)

    redis_cli.hset(
        f"doc:{doc_id}",
        mapping={
            "version": new_ver,
            "relpath": str(path.relative_to(STORAGE_DIR.parent)),
            "dsKey": f"{doc_id}-{new_ver}",
            "jwtKey": secrets.token_hex(16),
            "updatedAt": int(time.time()),
        },
    )
    return {"error": 0}


@app.get("/api/docs/{doc_id}/download")
async def download_doc(doc_id: str):
    meta = redis_cli.hgetall(f"doc:{doc_id}")
    if not meta:
        raise HTTPException(404, "unknown document")

    path = STORAGE_DIR.parent / meta["relpath"]
    if not path.exists():
        raise HTTPException(500, "file missing on disk")

    return FileResponse(
        path,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=path.name,
    )


if __name__ == "__main__":
    uvicorn.run("app.main:app", reload=True, port=8000)
