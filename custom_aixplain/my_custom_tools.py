def scrape_and_clean_link(url: str):
    """
    Navigates to the given URL using Selenium (headless Chrome),
    grabs the rendered HTML, removes <script> and <style> tags,
    and returns a cleaned text version of the page content.
    """

    import os

    # 1) Install dependencies at runtime (if needed)
    try:
        os.system("pip install selenium webdriver-manager beautifulsoup4")
    except Exception as e:
        print("Could not install dependencies. Error:", e)
        return None

    try:
        # 2) Import libraries after install
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager

        from bs4 import BeautifulSoup
        import time
        import re

        # 3) Configure Selenium in headless mode
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()), options=chrome_options
        )

        try:
            # 4) Actually scrape the page
            wait_time = 5
            driver.get(url)
            time.sleep(wait_time)  # Adjust as needed for heavy JS sites

            page_source = driver.page_source

        finally:
            driver.quit()

        # 5) Clean the HTML with BeautifulSoup
        soup = BeautifulSoup(page_source, "html.parser")

        for tag in soup(["script", "style"]):
            tag.decompose()

        text = soup.get_text(separator="\n")

        # 6) Strip out extra blank lines
        lines = [line.strip() for line in text.splitlines()]
        lines = [line for line in lines if line]
        cleaned_text = "\n".join(lines)

        return cleaned_text

    except Exception as e:
        print("Scraping/cleaning process failed. Error:", e)
        return None
