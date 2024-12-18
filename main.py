import os
import pdfkit
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


OUTPUT_FOLDER = "pdf_output"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Install wkhtmltopdf from official site
PDFKIT_CONFIG = pdfkit.configuration(wkhtmltopdf=r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe")


chrome_options = Options()
chrome_options.add_argument("--start-maximized")
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

START_URL = "https://www.exactsciences.com/"

try:
    driver.get(START_URL)
    wait = WebDriverWait(driver, 30)

    
    try:
        cookie_button = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
        cookie_button.click()
        print("Cookie consent accepted.")
    except TimeoutException:
        print("No cookie consent popup found.")

    
    wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Investor Relations"))).click()
    driver.switch_to.window(driver.window_handles[1])
    wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Press Releases"))).click()

    while True:
       
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, "evergreen-container-content")))

        
        press_links = driver.find_elements(By.CLASS_NAME, "evergreen-item-title")
        links = [
            (link.text.strip().replace("/", "-").replace("\\", "-"), link.get_attribute("href"))
            for link in press_links
        ]

       
        for title, href in links:
            if href:
                try:
                    print(f"Processing: {title}")
                    driver.get(href)
                    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))

                    pdf_filename = os.path.join(OUTPUT_FOLDER, f"{title}.pdf")
                    pdfkit.from_url(href, pdf_filename, configuration=PDFKIT_CONFIG)
                    print(f"Saved PDF: {pdf_filename}")
                except Exception as e:
                    print(f"Error processing link '{title}': {e}")

        
        try:
            pagination_buttons = driver.find_elements(By.CLASS_NAME, "evergreen-pager-button")
            for i, button in enumerate(pagination_buttons):
                if "js--active" in button.get_attribute("class"):
                    if i + 1 < len(pagination_buttons):
                        pagination_buttons[i + 1].click()
                        break
            else:
                print("No more pages to visit.")
                break
        except NoSuchElementException:
            print("Pagination not found or no more pages.")
            break

finally:
    driver.quit()
    print("Process complete. PDFs saved in:", OUTPUT_FOLDER)
