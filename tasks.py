import base64
import requests
import re
import os
import io
import logging
from datetime import datetime
from PIL import Image
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class CodeGeneration:
    def __init__(self):
        self.api_key = os.getenv("NVIDIA_API_KEY")
        
    def _call_llm_api(self, prompt):
        url = "https://integrate.api.nvidia.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "nvidia/llama-3.1-nemotron-ultra-253b-v1",
            "messages": [
                {"role": "system", "content": "detailed thinking on"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.6,
            "top_p": 0.95,
            "max_tokens": 16384
        }
        
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 200:
            raise Exception(f"API Error: {response.status_code} - {response.text}")
            
        response_data = response.json()
        return response_data['choices'][0]['message']['content']
            
    def generate_code(self, description, logo_path, business_name, main_color, secondary_color, images_data=None):
        logo_filename = os.path.basename(logo_path) if logo_path else "logo.png"
        
        # Create separate image information for content images
        images_info = ""
        if images_data and len(images_data) > 0:
            images_info = "Content Images:\n"
            for i, img in enumerate(images_data):
                images_info += f"{i+1}. Content Image URL: {img['url']}, Alt Text: {img['alt']}\n"
        
        prompt = f"""Generate a complete website using HTML, CSS, and JavaScript based on this information:

        Business Name: {business_name}
        Main Color: {main_color}
        Secondary Color: {secondary_color}
        Description: {description}
        
        Logo: The website should include a logo image with filename "{logo_filename}" in the header or top-left of the page.
        
        {images_info}
        
        Requirements:
        1. Structure your response with clearly separated sections:
        - HTML (between <!-- HTML START --> and <!-- HTML END -->)
        - CSS (between /* CSS START */ and /* CSS END */)
        - JavaScript (between // JavaScript START and // JavaScript END)
        2. Create a responsive, mobile-friendly design
        3. Include the logo image with max height of 100px (maintain aspect ratio)
        4. Incorporate the provided content images URLs directly in the HTML (do NOT change the URLs)
        5. Add subtle animations, hover effects, and transitions to interactive elements
        6. Ensure all text has sufficient contrast with background colors
        
        First, think about the overall structure and design approach, then provide the complete code.
        """
        
        return self._call_llm_api(prompt)


class ImageGeneration:
    def __init__(self):
        self.api_key = os.getenv("NVIDIA_API_KEY")

    def generate_image(self, image_prompt):
        invoke_url = "https://ai.api.nvidia.com/v1/genai/black-forest-labs/flux.1-dev"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
        }
        
        payload = {
            "prompt": image_prompt,
            "mode": "base",
            "cfg_scale": 3.5,
            "width": 512,  # Smaller size for logo is adequate
            "height": 512,
            "seed": 0,
            "steps": 40  # Slightly fewer steps for faster generation
        }
        
        try:
            response = requests.post(invoke_url, headers=headers, json=payload)
            response.raise_for_status()
            response_body = response.json()
            
            # Extract image data from response - adjust based on actual response structure
            if 'image_data' in response_body:
                image_data = response_body['image_data']
                # Assuming the image data is base64 encoded
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
                return image
            else:
                logging.error("No image data in NVIDIA API response")
                return None
                
        except Exception as e:
            logging.error(f"Error generating logo image with NVIDIA Flux: {e}")
            # Fall back to Pexels as a backup solution
            return self._fallback_logo_generation(image_prompt)
    
    def _fallback_logo_generation(self, image_prompt):
        """Fallback method using Pexels if NVIDIA API fails"""
        try:
            pexels_api_key = os.getenv("PEXELS_API_KEY")
            search_term = " ".join([word for word in image_prompt.split() if word.lower() not in ('logo', 'for', 'a', 'an', 'the')])
            
            url = f"https://api.pexels.com/v1/search?query={search_term}&per_page=1&orientation=square"
            headers = {"Authorization": pexels_api_key}
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if 'photos' in data and len(data['photos']) > 0:
                image_url = data['photos'][0]['src']['medium']
                image_response = requests.get(image_url)
                image_response.raise_for_status()
                
                image = Image.open(io.BytesIO(image_response.content))
                return image
            
            return None
        except Exception as e:
            logging.error(f"Fallback image generation also failed: {e}")
            return None


class PexelsImageFetcher:
    def __init__(self):
        self.api_key = os.getenv("PEXELS_API_KEY")
        
    def fetch_images(self, keyword, count=5):
        url = f"https://api.pexels.com/v1/search?query={keyword}&per_page={count}"
        headers = {
            "Authorization": self.api_key
        }
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            images = []
            for photo in data.get('photos', []):
                images.append({
                    'url': photo['src']['medium'],  # Using medium size for website
                    'width': photo['width'],
                    'height': photo['height'],
                    'alt': photo['alt'] or photo['photographer'],
                    'photographer': photo['photographer'],
                    'original_url': photo['url']
                })
            
            return images
            
        except Exception as e:
            logging.error(f"Error fetching images from Pexels: {e}")
            return []


def clean_gpt_output(raw_code):
    # Extract code sections using markers first
    html_match = re.search(r'<!-- HTML START -->(.*)<!-- HTML END -->', raw_code, re.DOTALL)
    css_match = re.search(r'/\* CSS START \*/(.*?)/\* CSS END \*/', raw_code, re.DOTALL)
    js_match = re.search(r'// JavaScript START(.*?)// JavaScript END', raw_code, re.DOTALL)
    
    # If any section wasn't found with markers, try code blocks
    if not html_match:
        html_block = re.search(r'```html\s*(.*?)\s*```', raw_code, re.DOTALL)
        html_content = html_block.group(1).strip() if html_block else ""
    else:
        html_content = html_match.group(1).strip()
        
    if not css_match:
        css_block = re.search(r'```css\s*(.*?)\s*```', raw_code, re.DOTALL)
        css_content = css_block.group(1).strip() if css_block else ""
    else:
        css_content = css_match.group(1).strip()
        
    if not js_match:
        js_block = re.search(r'```(javascript|js)\s*(.*?)\s*```', raw_code, re.DOTALL)
        js_content = js_block.group(2).strip() if js_block else ""
    else:
        js_content = js_match.group(1).strip()
    
    # Additional cleanup - remove any triple backticks that might remain
    html_content = re.sub(r'```html\s*|\s*```', '', html_content)
    css_content = re.sub(r'```css\s*|\s*```', '', css_content)
    js_content = re.sub(r'```(javascript|js)\s*|\s*```', '', js_content)
    
    return html_content, css_content, js_content


def generate_and_process_code(description, logo_path, business_name, main_color, secondary_color, images_data=None):
    try:
        code_gen = CodeGeneration()
        raw_code = code_gen.generate_code(description, logo_path, business_name, main_color, secondary_color, images_data)
        
        # Clean and split code
        html_content, css_content, js_content = clean_gpt_output(raw_code)
        
        # Create temporary directory for generated files
        temp_dir = os.path.join(os.getcwd(), "generated_website")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save files for preview and download
        with open(os.path.join(temp_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_content)
        with open(os.path.join(temp_dir, "styles.css"), "w", encoding="utf-8") as f:
            f.write(css_content)
        with open(os.path.join(temp_dir, "script.js"), "w", encoding="utf-8") as f:
            f.write(js_content)
        
        # Handle logo for runtime use - convert to base64 for inline embedding
        logo_b64 = None
        if logo_path and os.path.exists(logo_path):
            with open(logo_path, "rb") as logo_file:
                logo_bytes = logo_file.read()
                logo_b64 = base64.b64encode(logo_bytes).decode('utf-8')
                logo_ext = os.path.splitext(logo_path)[1].lstrip('.')
                logo_data_uri = f"data:image/{logo_ext};base64,{logo_b64}"
                # Replace logo path with data URI in HTML
                html_content = html_content.replace(os.path.basename(logo_path), logo_data_uri)
        
        return html_content, css_content, js_content, temp_dir
    
    except Exception as e:
        logging.error(f"An error occurred: {str(e)}")
        return None, None, None, None