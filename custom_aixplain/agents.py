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
    description="Outputs résumé / cover-letter in Markdown with YAML front-matter.",
    instructions="""
You must return **only**:

1. A 3-to-10-line YAML front-matter block.
2. Well-formed Markdown that follows these exact rules:

• Section heading = `## SECTION NAME` (all-caps).  
• Org line       = `### left<TAB>right` (real tab).  
• Sub line       = `#### left<TAB>right` (real tab, italic).  
• Bullets        = `- ` at left indent 1 cm.  
• No HTML, no back-ticks, no smart quotes.

Front-matter keys (all required unless noted):

doc_type, style, page_count.

Content **must fit** the requested page_count on A-4.

DO NOT add explanation or code fences.
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
