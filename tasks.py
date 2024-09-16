import requests
from bs4 import BeautifulSoup
import re
from PIL import Image
import io
import logging
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CodeGeneration:
    def __init__(self, rapidapi_key):
        self.rapidapi_key = rapidapi_key

    def _call_gpt_api(self, prompt):
        url = "https://chatgpt-42.p.rapidapi.com/gpt4"
        headers = {
            "x-rapidapi-key": self.rapidapi_key,
            "x-rapidapi-host": "chatgpt-42.p.rapidapi.com",
            "Content-Type": "application/json"
        }

        payload = {
            "messages": [{"role": "user", "content": prompt}],
            "web_access": False
        }

        response = requests.post(url, json=payload, headers=headers)
        response_data = response.json()

        if 'result' in response_data:
            return response_data['result']
        else:
            raise Exception(f"Unexpected response format: {response_data}")

    def generate_code(self, description, logo_path, business_name, main_color, secondary_color):
        logo_filename = os.path.basename(logo_path) if logo_path else "logo.png"
        prompt = f"""Write the code for a website using HTML, CSS, and JS based on the following description:

        Description
        ------------

        Business Name: {business_name}
        Main Color: {main_color}
        Secondary Color: {secondary_color}

        {description}

    Requirements
    ------------

    1. Start the HTML with <!-- HTML START -->, CSS with /* CSS START */, and JS with // JavaScript START and end the HTML with <!-- HTML END -->, CSS with /* CSS END */, and JS with // JavaScript END
    2. Include a logo image in the HTML with the filename "{logo_filename}", placed at the top left of the page css of the logo to be no more than 100px in height, maintaining its aspect ratio.
    """

        
        return self._call_gpt_api(prompt)

class ImageGeneration:
    def __init__(self, huggingface_api_key):
        self.huggingface_api_key = huggingface_api_key

    def generate_image(self, image_prompt):
        API_URL = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
        headers = {"Authorization": f"Bearer {self.huggingface_api_key}"}

        payload = {
            "inputs": image_prompt,
            "options": {"use_cache": False}
        }

        response = requests.post(API_URL, headers=headers, json=payload)
        
        if response.status_code != 200:
            logging.error(f"Error: {response.status_code} - {response.text}")
            return None

        try:
            image_bytes = response.content
            image = Image.open(io.BytesIO(image_bytes))
            return image
        except Exception as e:
            logging.error(f"Error processing image: {e}")
            return None

def clean_gpt_output(raw_code):
    # Extract HTML
    html_match = re.search(r'<!-- HTML START -->(.*)<!-- HTML END -->', raw_code, re.DOTALL)
    html_content = html_match.group(1).strip() if html_match else ""

    # Extract CSS
    css_match = re.search(r'/\* CSS START \*/(.*/\* CSS END \*/)', raw_code, re.DOTALL)
    css_content = css_match.group(1).strip() if css_match else ""

    # Extract JavaScript
    js_match = re.search(r'// JavaScript START(.*)// JavaScript END', raw_code, re.DOTALL)
    js_content = js_match.group(1).strip() if js_match else ""

    # Remove any remaining markdown code blocks
    html_content = re.sub(r'```html\s*|\s*```', '', html_content)
    css_content = re.sub(r'```css\s*|\s*```', '', css_content)
    js_content = re.sub(r'```javascript\s*|\s*```', '', js_content)

    return html_content, css_content, js_content

def generate_and_process_code(description, rapidapi_key, logo_path, business_name, main_color, secondary_color):
    try:
        code_gen = CodeGeneration(rapidapi_key)
        raw_code = code_gen.generate_code(description, logo_path, business_name, main_color, secondary_color)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Clean and split code
        html_content, css_content, js_content = clean_gpt_output(raw_code)
        
        # Validate content
        if not html_content.strip():
            raise ValueError("HTML content is empty")
        if not css_content.strip():
            logging.warning("CSS content is empty")
        if not js_content.strip():
            logging.warning("JavaScript content is empty")
        
        # Save files locally
        save_path = os.path.join(os.getcwd(), "generated_website")
        os.makedirs(save_path, exist_ok=True)
        
        with open(os.path.join(save_path, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_content)
        with open(os.path.join(save_path, "styles.css"), "w", encoding="utf-8") as f:
            f.write(css_content)
        with open(os.path.join(save_path, "script.js"), "w", encoding="utf-8") as f:
            f.write(js_content)
        
        logging.info(f"Code generated and processed successfully at {timestamp}")
        
        return html_content, css_content, js_content, save_path
    
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return None, None, None, None