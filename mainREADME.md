### Main Script (Streamlit Setup and UI)

```python
import streamlit as st
from tasks import generate_and_process_code, ImageGeneration
from PIL import Image
import os
import webbrowser
import zipfile
import io
```

- **Imports**: This block imports necessary libraries and modules:
  - **Streamlit (`st`)**: Used to build the user interface.
  - **generate_and_process_code**: Function to generate and clean website code.
  - **ImageGeneration**: Class used for AI-based logo generation.
  - **Other Modules** (`os`, `webbrowser`, `zipfile`, `io`): Handle file operations, such as saving logos, opening websites, and zipping generated files.

---

### Streamlit Page Configuration

```python
st.set_page_config(page_title="Ghata AI-Powered Website Generation Tool", layout="wide")
```

- **Configuration**: Sets up the Streamlit app’s page title and layout. The `layout="wide"` option provides more space, enhancing the app’s visual experience.

---

### Session State Initialization

```python
if 'generated_code' not in st.session_state:
    st.session_state.generated_code = None
if 'save_path' not in st.session_state:
    st.session_state.save_path = None
if 'logo_path' not in st.session_state:
    st.session_state.logo_path = None
```

- **Session State**: Initializes session variables to track generated code and file paths, ensuring continuity across user interactions.

---

### Sidebar (API Key Input)

```python
st.sidebar.title("API Configuration")
RAPIDAPI_KEY = st.sidebar.text_input("Enter your Rapid API key", type="password")
HUGGINGFACE_API_KEY = st.sidebar.text_input("Enter your Hugging Face API key", type="password")
```

- **API Key Input**: Provides fields for users to input their API keys, which are required for accessing the GPT-4 model (via RapidAPI) and FLUX.1-schnell (via Hugging Face).

---

### Main Title and Logo Options

```python
st.title("Ghata AI-Powered Website Generation Tool")
st.header("Step 1: Logo")
logo_choice = st.radio("Choose an option for your logo:", ("Upload Logo", "Generate Logo"))
```

- **Title and Logo Options**: Displays the main title and allows users to choose between uploading a logo or generating one through AI.

---

### Logo Saving and Resizing Function

```python
def save_and_resize_logo(image, filename):
    # Ensure save_path exists
    if st.session_state.save_path is None:
        st.session_state.save_path = os.path.join(os.getcwd(), "generated_website")
        os.makedirs(st.session_state.save_path, exist_ok=True)
    
    # Save original logo
    logo_path = os.path.join(st.session_state.save_path, filename)
    image.save(logo_path)
    st.session_state.logo_path = logo_path
    
    # Resize for display
    max_height = 200
    aspect_ratio = image.width / image.height
    new_width = int(max_height * aspect_ratio)
    resized_image = image.resize((new_width, max_height))
    
    return resized_image
```

- **Logo Processing**: Saves uploaded or generated logos to the `save_path` directory, resizing them to a max height of 200 pixels while preserving aspect ratio.

---

### Logo Upload and Generation

```python
if logo_choice == "Upload Logo":
    logo = st.file_uploader("Upload your logo (1024x1024 recommended)", type=["png", "jpg", "jpeg"])
    if logo:
        logo_image = Image.open(logo)
        resized_logo = save_and_resize_logo(logo_image, "uploaded_logo.png")
        st.image(resized_logo, caption="Uploaded Logo", use_column_width=False)
else:
    logo_description = st.text_input("Describe the logo to generate:", placeholder="E.g., 'Logo for an e-commerce website named Shakani'")
    if logo_description and st.button("Generate Logo"):
        with st.spinner("Generating logo..."):
            image_gen = ImageGeneration(HUGGINGFACE_API_KEY)
            generated_image = image_gen.generate_image(logo_description)
            if generated_image:
                resized_image = save_and_resize_logo(generated_image, "generated_logo.png")
                st.image(resized_image, caption="Generated Logo", use_column_width=False)
            else:
                st.error("Failed to generate logo.")
```

- **Logo Option Handling**: 
  - If the user chooses to upload a logo, it allows them to upload and displays the resized logo.
  - If the user opts to generate a logo, it sends the description to the FLUX.1-schnell model, resizes the output, and displays it.

---

### Website Description and Additional Details

```python
st.header("Step 2: Website Description")
website_description = st.text_area("Describe your website", placeholder="Enter a detailed description of your website...")

st.header("Step 3: Additional Details")
business_name = st.text_input("Business Name", placeholder="Enter your business name")
main_color = st.color_picker("Choose main color for your website", "#000000")
secondary_color = st.color_picker("Choose secondary color for your website", "#FFFFFF")
```

- **Website Details**: Collects user input for website description, business name, and color scheme preferences, which the model uses to customize the website.

---

### Website Generation

```python
if st.button("Generate Website"):
    if website_description and RAPIDAPI_KEY:
        with st.spinner("Generating website..."):
            html_content, css_content, js_content, save_path = generate_and_process_code(
                website_description, RAPIDAPI_KEY, st.session_state.logo_path,
                business_name, main_color, secondary_color
            )
            
            if html_content and css_content and js_content:
                st.session_state.generated_code = (html_content, css_content, js_content)
                st.session_state.save_path = save_path
                st.success("Website generated successfully!")
            else:
                st.error("Failed to generate website. Please check the logs for details.")
    else:
        st.error("Please enter a website description and ensure you've provided the Rapid API key.")
```

- **Generate Website**: On clicking "Generate Website," the description and other inputs are sent to the model. The function `generate_and_process_code` is called, which returns HTML, CSS, and JS code that’s stored in session state for preview and download.

---

### Display and Download Code

```python
if st.session_state.generated_code:
    html_content, css_content, js_content = st.session_state.generated_code
    
    st.header("Generated Code")
    tab1, tab2, tab3 = st.tabs(["HTML", "CSS", "JavaScript"])
    
    with tab1:
        st.code(html_content, language="html")
        st.download_button("Download HTML", data=html_content, file_name="index.html")
        
    with tab2:
        st.code(css_content, language="css")
        st.download_button("Download CSS", data=css_content, file_name="styles.css")
        
    with tab3:
        st.code(js_content, language="javascript")
        st.download_button("Download JS", data=js_content, file_name="script.js")
```

- **Display and Download**: Displays the generated code in tabs, allowing users to view and download each file.

---

### Website Preview and ZIP Download

```python
if st.button("Preview Generated Website"):
    if st.session_state.save_path:
        webbrowser.open('file://' + os.path.realpath(os.path.join(st.session_state.save_path, "index.html")))
        st.success("Website opened in a new tab. If it didn't open automatically, please check your browser settings.")
    else:
        st.error("Unable to preview the website. The files may not have been saved correctly.")

if st.button("Download Website as ZIP"):
    if st.session_state.save_path:
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for root, _, files in os.walk(st.session_state.save_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, st.session_state.save_path)
                    zip_file.write(file_path, arcname)
        zip_buffer.seek(0)
        st.download_button(
            label="Download ZIP",
            data=zip_buffer,
            file_name="generated_website.zip",
            mime="application/zip"
        )
    else:
        st.error("No generated website files found.")
```

- **Preview and ZIP Download**: 
  - **Preview**: Opens the HTML file in the default browser.
  - **ZIP Download**: Packs the generated files into a ZIP for easy download.

---

This covers the entire code, breaking down each feature and its function in the app.
