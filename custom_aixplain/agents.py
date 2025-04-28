from aixplain.factories import AgentFactory
from custom_aixplain import my_custom_tools

scrape_tool = AgentFactory.create_custom_python_code_tool(
    my_custom_tools.scrape_and_clean_link
)
model_tool_4o = AgentFactory.create_model_tool(
    model="6646261c6eb563165658bbb1",  # gpt-4o
)
web_scrape_agent = AgentFactory.create(
    name="JobListingScraper",
    description="Scrapes a job listing from a provided URL, extracting the company name, job title, and a detailed job description (including requirements and qualifications).",
    instructions="",
    # instructions="""
    #     You are a specialized scraping assistant.
    #     When the user provides a URL (e.g., "scrape this link: X"),
    #     use the 'scrape_tool' with the parameter 'url=X' as its input.
    #     Then parse and return the following information in JSON format with keys:
    #       - company
    #       - title
    #       - summary   (the full job description, including requirements and responsibilities)
    #     Do not include extraneous commentary. If any data is missing, return an empty string for that field.
    # """,
    tools=[scrape_tool],
    # llm_id="6646261c6eb563165658bbb1",
)


writer_agent = AgentFactory.create(
    name="DocumentWriter",
    description="Generates or updates resumes or cover letters using job info, background data, and user instructions.",
    instructions="""
You can:
1) CREATE a new document (resume or cover letter), given:
   - doc_type ("resume" or "cover_letter")
   - job_info
   - background_info
   - page_count (number of A4 pages)
2) UPDATE an existing document, given:
   - doc_type
   - current_text
   - new_background_snippet (optional)
   - user_request
   - page_count

Respect page_count when deciding how much detail to include. If current_text is provided, preserve it but integrate new info or changes. Return plain text or minimal JSON only—no extra commentary.

For 'resume', keep it concise and relevant, with all the contact information on one line, do not include a top title.  
For 'cover_letter', address the company/role and highlight key qualifications.
""",
    tools=[AgentFactory.create_model_tool(model="6646261c6eb563165658bbb1")],  # gpt-4o
)

formatter_agent = AgentFactory.create(
    name="DocumentFormatter",
    description="Formats job-application documents (resume/cover letter) into polished HTML, respecting style and page-count constraints.",
    instructions="""
You convert or update resume/cover-letter text into HTML. You may receive:
- 'raw_text' (new or updated content),
- 'existing_formatted_html' (previous styling),
- 'style' (e.g. 'professional', 'modern'),
- 'page_count' (A4 pages),
- 'doc_type' ('resume' or 'cover_letter').
- 'user_request' (user styling requests if any)

When both 'existing_formatted_html' and 'raw_text' are provided, merge or adjust them as needed. 
Respect 'page_count' by keeping the content concise, but avoid removing critical details. 
Return only the final HTML—no extra commentary.
""",
    tools=[AgentFactory.create_model_tool(model="6646261c6eb563165658bbb1")],  # gpt-4o
)
