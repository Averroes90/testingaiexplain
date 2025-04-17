import gradio as gr
import html

# escaped_str = "\\n\\n---\\n\\n**[Your Name]**  \\n[Your Address]  \\n[City, State, Zip]  \\n[Your Email]  \\n[Your Phone Number]  \\n\\n---\\n\\n**Objective**  \\nDynamic and results-driven AI/ML professional with over 7 years of experience in machine learning, product operations, and cross-functional team leadership. Seeking to leverage expertise in designing and implementing machine learning models, particularly in NLP, at aiXplain.\\n\\n---\\n\\n**Education**  \\n\\n**Columbia University Engineering AI Bootcamp**  \\nCertificate in Artificial Intelligence and Machine Learning, Expected June 2024  \\n- Key skills: Python, Pandas, TensorFlow, Keras, Scikit-learn, NLP, Computer Vision  \\n\\n**University of Virginia Darden School of Business**  \\nMaster of Business Administration, May 2019  \\n\\n**University of Jordan**  \\nBachelor of Science in Mechatronics Engineering, Jan 2013  \\n\\n---\\n\\n**Professional Experience**  \\n\\n**Google LLC**  \\n*Product Operations T/ Program Manager – Phones*  \\n2018-Present, Mountain View, CA  \\n- Managed a third-party team of data scientists to deliver machine learning predictive models, achieving a 15% reduction in qualification costs.  \\n- Drove product headcount resource management for 8 Pixel devices from concept through end of life.  \\n- Led early engagement product investigation and feature definition for new Pixel devices.  \\n\\n**Philip Morris International**  \\n*Operations Planning Analyst*  \\n2015-2017, Izmir, Turkey  \\n- Directed cross-functional teams to resolve a defective data mining tool, supporting 40 production lines.  \\n- Supervised the operations team for the revamp of seven strategic products, achieving a 100% hit rate for in-market sales timelines.  \\n\\n---\\n\\n**Projects**  \\n\\n**Auto Transcribe and Translate**  \\n- Developed an advanced tool converting spoken language in videos into written subtitles, achieving a Word Error Rate (WER) of 5%.  \\n- Leveraged Google’s Chirp models and OpenAI’s Whisper for high accuracy in transcription.  \\n\\n**GPT Interface**  \\n- Built a full-stack AI-powered application integrating GPT models, focusing on self-education and skill development.  \\n- Implemented caching with Redis, reducing API response latency by 40%.  \\n\\n---\\n\\n**Technical Skills**  \\n- **Programming Languages:** Python, JavaScript, SQL, C  \\n- **Machine Learning:** TensorFlow, Keras, Scikit-learn, PyTorch  \\n- **Data Science:** Pandas, NumPy, Matplotlib, Jupyter  \\n- **Cloud Platforms:** AWS, Google Cloud  \\n- **DevOps & Tools:** Docker, Git, Kubernetes  \\n\\n---\\n\\n**Certifications**  \\n- Certified AI professional with hands-on experience in building predictive models and managing cross-functional teams.  \\n\\n---\\n\\n**References**  \\nAvailable upon request."
# clean_str = escaped_str.encode().decode("unicode_escape")

# resume_html = f"""
#     <div style="
#         background-color: white;
#         padding: 2rem;
#         margin: auto;
#         width: 8.5in;
#         min-height: 11in;
#         box-shadow: 0 0 10px rgba(0,0,0,0.2);
#         font-family: 'Arial', sans-serif;
#         line-height: 1.6;
#         color: black;
#     ">
#         {clean_str.replace('\n', '<br>')}
#     </div>
#     """


def handle_submission(job_link: str = None, include_cover_letter: bool = False):
    # Clean up the raw string inside the function
    escaped_str = "\\n\\n---\\n\\n**[Your Name]**  \\n[Your Address]  \\n[City, State, Zip]  \\n[Your Email]  \\n[Your Phone Number]  \\n\\n---\\n\\n**Objective**  \\nDynamic and results-driven AI/ML professional with over 7 years of experience in machine learning, product operations, and cross-functional team leadership. Seeking to leverage expertise in designing and implementing machine learning models, particularly in NLP, at aiXplain.\\n\\n---\\n\\n**Education**  \\n\\n**Columbia University Engineering AI Bootcamp**  \\nCertificate in Artificial Intelligence and Machine Learning, Expected June 2024  \\n- Key skills: Python, Pandas, TensorFlow, Keras, Scikit-learn, NLP, Computer Vision  \\n\\n**University of Virginia Darden School of Business**  \\nMaster of Business Administration, May 2019  \\n\\n**University of Jordan**  \\nBachelor of Science in Mechatronics Engineering, Jan 2013  \\n\\n---\\n\\n**Professional Experience**  \\n\\n**Google LLC**  \\n*Product Operations T/ Program Manager – Phones*  \\n2018-Present, Mountain View, CA  \\n- Managed a third-party team of data scientists to deliver machine learning predictive models, achieving a 15% reduction in qualification costs.  \\n- Drove product headcount resource management for 8 Pixel devices from concept through end of life.  \\n- Led early engagement product investigation and feature definition for new Pixel devices.  \\n\\n**Philip Morris International**  \\n*Operations Planning Analyst*  \\n2015-2017, Izmir, Turkey  \\n- Directed cross-functional teams to resolve a defective data mining tool, supporting 40 production lines.  \\n- Supervised the operations team for the revamp of seven strategic products, achieving a 100% hit rate for in-market sales timelines.  \\n\\n---\\n\\n**Projects**  \\n\\n**Auto Transcribe and Translate**  \\n- Developed an advanced tool converting spoken language in videos into written subtitles, achieving a Word Error Rate (WER) of 5%.  \\n- Leveraged Google’s Chirp models and OpenAI’s Whisper for high accuracy in transcription.  \\n\\n**GPT Interface**  \\n- Built a full-stack AI-powered application integrating GPT models, focusing on self-education and skill development.  \\n- Implemented caching with Redis, reducing API response latency by 40%.  \\n\\n---\\n\\n**Technical Skills**  \\n- **Programming Languages:** Python, JavaScript, SQL, C  \\n- **Machine Learning:** TensorFlow, Keras, Scikit-learn, PyTorch  \\n- **Data Science:** Pandas, NumPy, Matplotlib, Jupyter  \\n- **Cloud Platforms:** AWS, Google Cloud  \\n- **DevOps & Tools:** Docker, Git, Kubernetes  \\n\\n---\\n\\n**Certifications**  \\n- Certified AI professional with hands-on experience in building predictive models and managing cross-functional teams.  \\n\\n---\\n\\n**References**  \\nAvailable upon request."
    clean_str = escaped_str.encode().decode("unicode_escape")
    safe_str = (
        clean_str.replace("{", "&#123;").replace("}", "&#125;").replace("\n", "<br>")
    )
    # Placeholder: You can modify this later to call your vector DB or resume generator
    retrieved_info = "📄 *Retrieved background info matching job:* \n- ML Engineer at Google\n- M.Sc. in AI\n..."

    if include_cover_letter:
        clean_str += "\n\n## Cover Letter\nDear Hiring Manager, ..."

    # Render inside a styled div
    resume_html = f"""
    <style>
        .doc-container {{
            display: flex;
            justify-content: center;
            background-color: #eee;
            padding: 2rem;
            height: 100vh;
            overflow: auto;
        }}
        .doc-page {{
            background-color: white;
            width: 8.5in;
            min-height: 11in;
            box-shadow: 0 0 4px rgba(0,0,0,0.3);
            border: 1px solid #ccc;
            padding: 1in;
            overflow-y: auto;
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: black;
            position: relative;
        }}
    </style>

    <div class='doc-container'>
        <div class='doc-page'>
            {safe_str}
        </div>
    </div>
    """

    return retrieved_info, resume_html


def chat_with_agent(message, chat_history):
    # Placeholder: simulate AI response
    reply = f"📬 AI: Okay! I’ve added ‘{message}’ to your resume."
    chat_history.append((message, reply))
    return "", chat_history


with gr.Blocks() as demo:
    gr.Markdown("## 🧠 rezoMe")

    with gr.Row():
        job_link_input = gr.Textbox(label="Paste Job Link Here")
        cover_letter_checkbox = gr.Checkbox(label="Include Cover Letter?")
        submit_btn = gr.Button("Submit")

    escaped_str = "\\n\\n---\\n\\n**[Your Name]**  \\n[Your Address]  \\n[City, State, Zip]  \\n[Your Email]  \\n[Your Phone Number]  \\n\\n---\\n\\n**Objective**  \\nDynamic and results-driven AI/ML professional with over 7 years of experience in machine learning, product operations, and cross-functional team leadership. Seeking to leverage expertise in designing and implementing machine learning models, particularly in NLP, at aiXplain.\\n\\n---\\n\\n**Education**  \\n\\n**Columbia University Engineering AI Bootcamp**  \\nCertificate in Artificial Intelligence and Machine Learning, Expected June 2024  \\n- Key skills: Python, Pandas, TensorFlow, Keras, Scikit-learn, NLP, Computer Vision  \\n\\n**University of Virginia Darden School of Business**  \\nMaster of Business Administration, May 2019  \\n\\n**University of Jordan**  \\nBachelor of Science in Mechatronics Engineering, Jan 2013  \\n\\n---\\n\\n**Professional Experience**  \\n\\n**Google LLC**  \\n*Product Operations T/ Program Manager – Phones*  \\n2018-Present, Mountain View, CA  \\n- Managed a third-party team of data scientists to deliver machine learning predictive models, achieving a 15% reduction in qualification costs.  \\n- Drove product headcount resource management for 8 Pixel devices from concept through end of life.  \\n- Led early engagement product investigation and feature definition for new Pixel devices.  \\n\\n**Philip Morris International**  \\n*Operations Planning Analyst*  \\n2015-2017, Izmir, Turkey  \\n- Directed cross-functional teams to resolve a defective data mining tool, supporting 40 production lines.  \\n- Supervised the operations team for the revamp of seven strategic products, achieving a 100% hit rate for in-market sales timelines.  \\n\\n---\\n\\n**Projects**  \\n\\n**Auto Transcribe and Translate**  \\n- Developed an advanced tool converting spoken language in videos into written subtitles, achieving a Word Error Rate (WER) of 5%.  \\n- Leveraged Google’s Chirp models and OpenAI’s Whisper for high accuracy in transcription.  \\n\\n**GPT Interface**  \\n- Built a full-stack AI-powered application integrating GPT models, focusing on self-education and skill development.  \\n- Implemented caching with Redis, reducing API response latency by 40%.  \\n\\n---\\n\\n**Technical Skills**  \\n- **Programming Languages:** Python, JavaScript, SQL, C  \\n- **Machine Learning:** TensorFlow, Keras, Scikit-learn, PyTorch  \\n- **Data Science:** Pandas, NumPy, Matplotlib, Jupyter  \\n- **Cloud Platforms:** AWS, Google Cloud  \\n- **DevOps & Tools:** Docker, Git, Kubernetes  \\n\\n---\\n\\n**Certifications**  \\n- Certified AI professional with hands-on experience in building predictive models and managing cross-functional teams.  \\n\\n---\\n\\n**References**  \\nAvailable upon request."
    clean_str = escaped_str.encode().decode("unicode_escape")
    retrieved_output = gr.Markdown("*(Retrieved background info will appear here)*")
    # resume_display = gr.Markdown(clean_str)
    resume_display = gr.HTML()
    # resume_display.update(value=resume_html)

    submit_btn.click(
        handle_submission,
        inputs=[job_link_input, cover_letter_checkbox],
        outputs=[retrieved_output, resume_display],
    )

    gr.Markdown("### 💬 Chat with the AI to refine resume")

    with gr.Row():
        user_msg = gr.Textbox(
            label="Your message", placeholder="e.g., Emphasize Python expertise"
        )
        send_btn = gr.Button("Send")

    chat_history = gr.Chatbot()

    send_btn.click(
        chat_with_agent,
        inputs=[user_msg, chat_history],
        outputs=[user_msg, chat_history],
    )

demo.launch()
