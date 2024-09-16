import streamlit as st
from tasks import generate_and_process_code, ImageGeneration
from PIL import Image
import os
import io
import zipfile
import tempfile

st.set_page_config(page_title="Ghata AI-Powered Website Generation Tool", layout="wide")

# Initialize session state
if 'generated_code' not in st.session_state:
    st.session_state.generated_code = None
if 'save_path' not in st.session_state:
    st.session_state.save_path = None
if 'logo_path' not in st.session_state:
    st.session_state.logo_path = None

# Sidebar for API keys
st.sidebar.title("API Configuration")
RAPIDAPI_KEY = st.sidebar.text_input("Enter your Rapid API key", type="password")
HUGGINGFACE_API_KEY = st.sidebar.text_input("Enter your Hugging Face API key", type="password")

# Main content
st.title("Ghata AI-Powered Website Generation Tool")

# Step 1: Logo
st.header("Step 1: Logo")
logo_choice = st.radio("Choose an option for your logo:", ("Upload Logo", "Generate Logo"))

def save_and_resize_logo(image, filename):
    # Use a temporary directory for Streamlit Cloud
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save original logo
        logo_path = os.path.join(temp_dir, filename)
        image.save(logo_path)
        st.session_state.logo_path = logo_path
        
        # Resize for display
        max_height = 200  # Fixed max height of 200 pixels
        aspect_ratio = image.width / image.height
        new_width = int(max_height * aspect_ratio)
        resized_image = image.resize((new_width, max_height))
        
        return resized_image, logo_path

if logo_choice == "Upload Logo":
    logo = st.file_uploader("Upload your logo (1024x1024 recommended)", type=["png", "jpg", "jpeg"])
    if logo:
        logo_image = Image.open(logo)
        resized_logo, logo_path = save_and_resize_logo(logo_image, "uploaded_logo.png")
        st.image(resized_logo, caption="Uploaded Logo", use_column_width=False)
else:
    logo_description = st.text_input("Describe the logo to generate:", 
                                     placeholder="E.g., 'Logo for an e-commerce website named Shakani'")
    if logo_description and st.button("Generate Logo"):
        with st.spinner("Generating logo..."):
            image_gen = ImageGeneration(HUGGINGFACE_API_KEY)
            generated_image = image_gen.generate_image(logo_description)
            if generated_image:
                resized_image, logo_path = save_and_resize_logo(generated_image, "generated_logo.png")
                st.image(resized_image, caption="Generated Logo", use_column_width=False)
            else:
                st.error("Failed to generate logo.")

# Step 2: Website Description
st.header("Step 2: Website Description")
website_description = st.text_area("Describe your website", 
                                   placeholder="Enter a detailed description of your website, including the type of business, main products or services, and any specific features you want.")

# Step 3: Additional Details
st.header("Step 3: Additional Details")
business_name = st.text_input("Business Name", placeholder="Enter your business name")
main_color = st.color_picker("Choose main color for your website", "#000000")
secondary_color = st.color_picker("Choose secondary color for your website", "#FFFFFF")

if st.button("Generate Website"):
    if website_description and RAPIDAPI_KEY:
        with st.spinner("Generating website..."):
            html_content, css_content, js_content = generate_and_process_code(
                website_description, RAPIDAPI_KEY, st.session_state.logo_path,
                business_name, main_color, secondary_color
            )
            
            if html_content and css_content and js_content:
                st.session_state.generated_code = (html_content, css_content, js_content)
                st.success("Website generated successfully!")
            else:
                st.error("Failed to generate website. Please check the logs for details.")
    else:
        st.error("Please enter a website description and ensure you've provided the Rapid API key.")

# Display generated code if available
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
    
    # Preview generated website
    if st.button("Preview Generated Website"):
        # Create a temporary HTML file with the generated content
        with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as temp_file:
            temp_file.write(f"""
            <html>
            <head>
                <style>{css_content}</style>
            </head>
            <body>
                {html_content}
                <script>{js_content}</script>
            </body>
            </html>
            """)
            temp_file_path = temp_file.name
        
        # Use st.components.v1.html to display the HTML content
        st.components.v1.html(open(temp_file_path, 'r').read(), height=600)
        
        # Clean up the temporary file
        os.unlink(temp_file_path)

    # Add download zip button
    if st.button("Download Website as ZIP"):
        # Create a ZIP file in memory
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            zip_file.writestr("index.html", html_content)
            zip_file.writestr("styles.css", css_content)
            zip_file.writestr("script.js", js_content)
            if st.session_state.logo_path:
                zip_file.write(st.session_state.logo_path, os.path.basename(st.session_state.logo_path))
        
        zip_buffer.seek(0)
        st.download_button(
            label="Download ZIP",
            data=zip_buffer,
            file_name="generated_website.zip",
            mime="application/zip"
        )
    else:
        st.error("No generated website files found.")

# Instructions
st.sidebar.markdown("""
## How to use:
1. Enter your Rapid API and Hugging Face API keys in the sidebar.
2. Choose to upload or generate a logo.
3. Describe your website in detail.
4. Provide additional details like business name and color scheme.
5. Click 'Generate Website' to create your custom website.
6. View, download, or preview your generated website.
7. Use the 'Download Website as ZIP' button to download all files at once.
""")
