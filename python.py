import os
import time
import traceback
from flask import Flask, request, jsonify, render_template_string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium_stealth import stealth

DOWNLOAD_DIRECTORY = "C:/Users/D.PAVAN/Desktop/Court PDFs"

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Delhi Courts Cause List Downloader</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background-color: #f4f7f6; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .container { background: white; padding: 40px; border-radius: 12px; box-shadow: 0 8px 16px rgba(0,0,0,0.1); width: 100%; max-width: 500px; text-align: center; }
        h2 { color: #333; margin-bottom: 30px; }
        label { display: block; text-align: left; margin-bottom: 8px; color: #555; font-weight: bold; }
        select, input[type="date"] { width: 100%; padding: 12px; border-radius: 8px; border: 1px solid #ccc; box-sizing: border-box; margin-bottom: 20px; font-size: 16px; }
        button { width: 100%; background-color: #007bff; color: white; padding: 15px; border: none; border-radius: 8px; font-size: 18px; cursor: pointer; transition: background-color 0.3s; }
        button:disabled { background-color: #9ac7f5; cursor: not-allowed; }
        button:hover:enabled { background-color: #0056b3; }
        #status { margin-top: 20px; font-size: 16px; color: #333; height: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Delhi District Courts Cause List Downloader</h2>
        <label for="courtComplex">Select Court Complex:</label>
        <select id="courtComplex">
            <option value="Patiala House Court Complex">Patiala House Court Complex</option>
            <option value="Tis Hazari Court Complex">Tis Hazari Court Complex</option>
            <option value="Karkardooma Court Complex">Karkardooma Court Complex</option>
            <option value="Rohini Court Complex">Rohini Court Complex</option>
            <option value="Dwarka Court Complex">Dwarka Court Complex</option>
            <option value="Saket Court Complex">Saket Court Complex</option>
            <option value="Rouse Avenue Court Complex">Rouse Avenue Court Complex</option>
        </select>
        <label for="causeDate">Select Date:</label>
        <input type="date" id="causeDate" required>
        <button id="downloadBtn">Download All PDFs</button>
        <p id="status"></p>
    </div>
    <script>
        document.getElementById('causeDate').valueAsDate = new Date();
        document.getElementById('downloadBtn').addEventListener('click', async () => {
            const complexSelect = document.getElementById('courtComplex');
            const dateInput = document.getElementById('causeDate');
            const statusP = document.getElementById('status');
            const downloadBtn = document.getElementById('downloadBtn');
            if (!dateInput.value) {
                statusP.textContent = 'Please select a date.';
                statusP.style.color = 'red';
                return;
            }
            downloadBtn.disabled = true;
            downloadBtn.textContent = 'Downloading...';
            statusP.textContent = 'Starting scraper...';
            statusP.style.color = '#333';
            try {
                const response = await fetch('/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        date: dateInput.value,
                        complexName: complexSelect.value
                    })
                });
                const result = await response.json();
                if (result.status === 'success') {
                    statusP.textContent = result.message;
                    statusP.style.color = 'green';
                } else {
                    statusP.textContent = 'Error: ' + result.message;
                    statusP.style.color = 'red';
                }
            } catch (error) {
                statusP.textContent = 'A network error occurred.';
                statusP.style.color = 'red';
            } finally {
                downloadBtn.disabled = false;
                downloadBtn.textContent = 'Download All PDFs';
            }
        });
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/download', methods=['POST'])
def download_causelists():
    driver = None
    try:
        data = request.get_json()
        target_date = data.get('date')
        complex_name = data.get('complexName')
        print(f"\n[INFO] Received request for Date: {target_date}, Complex: {complex_name}")

        if not os.path.exists(DOWNLOAD_DIRECTORY):
            os.makedirs(DOWNLOAD_DIRECTORY)

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        prefs = {"plugins.always_open_pdf_externally": True, "download.default_directory": DOWNLOAD_DIRECTORY}
        chrome_options.add_experimental_option("prefs", prefs)

        print("[INFO] Initializing WebDriver...")
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        print("[INFO] WebDriver Initialized.")

        stealth(driver, languages=["en-US", "en"], vendor="Google Inc.", platform="Win32",
                webgl_vendor="Intel Inc.", renderer="Intel Iris OpenGL Engine", fix_hairline=True)
        print("[INFO] Stealth settings applied.")
        
        url = "https://newdelhi.dcourts.gov.in/cause-list-%e2%81%84-daily-board/"
        print(f"[INFO] Navigating to {url}...")
        driver.get(url)
        print("[INFO] Page loaded.")

        wait = WebDriverWait(driver, 30)

        print("[INFO] Looking for the iframe...")
        wait.until(EC.frame_to_be_available_and_switch_to_it((By.TAG_NAME, "iframe")))
        print("[INFO] Switched to iframe successfully.")
        
    except Exception as e:
        print("\n" + "="*50)
        print("❌ AN ERROR OCCURRED. Please copy the text below:")
        traceback.print_exc()
        print("="*50 + "\n")
        return jsonify({"status": "error", "message": "An error occurred. Check terminal."})

    finally:
        print("[INFO] Script finished. Browser will remain open for debugging.")

if __name__ == '__main__':
    app.run(debug=True)
