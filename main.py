import streamlit as st
from tasks import generate_and_process_code, ImageGeneration, PexelsImageFetcher
from PIL import Image
import os
import zipfile
import io
import base64
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

st.set_page_config(page_title="AI-Powered Website Generation Tool", layout="wide")

# Initialize session state
if 'generated_code' not in st.session_state:
    st.session_state.generated_code = None
if 'save_path' not in st.session_state:
    st.session_state.save_path = None
if 'logo_path' not in st.session_state:
    st.session_state.logo_path = None
if 'images_data' not in st.session_state:
    st.session_state.images_data = []
if 'website_html' not in st.session_state:
    st.session_state.website_html = None

# Main content
st.title("AI-Powered Website Generation Tool")

# Step 1: Logo
st.header("Step 1: Logo")
logo_choice = st.radio("Choose an option for your logo:", ("Upload Logo", "Generate Logo"))

def save_and_resize_logo(image, filename):
    # Use tempfile module for temporary storage
    import tempfile
    
    # Create temp directory if it doesn't exist yet
    if not hasattr(st.session_state, 'temp_dir'):
        st.session_state.temp_dir = tempfile.mkdtemp()
    
    # Save logo to temp directory
    logo_path = os.path.join(st.session_state.temp_dir, filename)
    image.save(logo_path)
    st.session_state.logo_path = logo_path
    
    # Resize for display
    max_height = 200
    aspect_ratio = image.width / image.height
    new_width = int(max_height * aspect_ratio)
    resized_image = image.resize((new_width, max_height))
    
    return resized_image

if logo_choice == "Upload Logo":
    logo = st.file_uploader("Upload your logo (1024x1024 recommended)", type=["png", "jpg", "jpeg"])
    if logo:
        logo_image = Image.open(logo)
        resized_logo = save_and_resize_logo(logo_image, "uploaded_logo.png")
        st.image(resized_logo, caption="Uploaded Logo", use_column_width=False)
else:
    logo_description = st.text_input("Describe the logo to generate:", 
                                     placeholder="E.g., 'Logo for an e-commerce website named Shakani'")
    if logo_description and st.button("Generate Logo"):
        try:
            with st.spinner("Generating logo..."):
                image_gen = ImageGeneration()
                generated_image = image_gen.generate_image(logo_description)
                if generated_image:
                    resized_image = save_and_resize_logo(generated_image, "generated_logo.png")
                    st.image(resized_image, caption="Generated Logo", use_column_width=False)
                else:
                    st.error("Failed to generate logo.")
        except Exception as e:
            st.error(f"Error generating logo: {str(e)}")

# Step 2: Website Description
st.header("Step 2: Website Description")
website_description = st.text_area("Describe your website", 
                                   placeholder="Enter a detailed description of your website, including the type of business, main products or services, and any specific features you want.")

# Step 3: Images
st.header("Step 3: Website Images")
image_keywords = st.text_input("Enter keywords for images (comma separated):", 
                           placeholder="E.g., 'coffee shop interior, coffee beans, barista'")

if image_keywords and st.button("Fetch Images"):
    keywords_list = [k.strip() for k in image_keywords.split(",")]
    st.session_state.images_data = []
    
    with st.spinner("Fetching images..."):
        for keyword in keywords_list[:3]:  # Limit to 3 keywords for simplicity
            try:
                fetcher = PexelsImageFetcher()
                images = fetcher.fetch_images(keyword, count=2)  # Get 2 images per keyword
                
                if images:
                    st.session_state.images_data.extend(images)
            except Exception as e:
                st.warning(f"Could not fetch images for '{keyword}': {str(e)}")
                
    if st.session_state.images_data:
        st.success(f"Found {len(st.session_state.images_data)} images!")
        
        # Display images in a grid
        cols = st.columns(3)
        for i, img_data in enumerate(st.session_state.images_data):
            with cols[i % 3]:
                st.image(img_data['url'], caption=f"{img_data['alt']} by {img_data['photographer']}", use_column_width=True)
    else:
        st.error("No images found. Try different keywords.")

# Step 4: Additional Details
st.header("Step 4: Additional Details")
business_name = st.text_input("Business Name", placeholder="Enter your business name")
main_color = st.color_picker("Choose main color for your website", "#000000")
secondary_color = st.color_picker("Choose secondary color for your website", "#FFFFFF")

if st.button("Generate Website"):
    if website_description:
        with st.spinner("Generating website..."):
            try:
                html_content, css_content, js_content, save_path = generate_and_process_code(
                    website_description, st.session_state.logo_path,
                    business_name, main_color, secondary_color, st.session_state.images_data
                )
                
                if html_content and css_content and js_content:
                    st.session_state.generated_code = (html_content, css_content, js_content)
                    st.session_state.save_path = save_path
                    
                    # Save complete website for preview
                    st.session_state.website_html = f"""
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>{business_name}</title>
                        <style>
                        {css_content}
                        </style>
                    </head>
                    <body>
                        {html_content}
                        <script>
                        {js_content}
                        </script>
                    </body>
                    </html>
                    """
                    
                    st.success("Website generated successfully!")
                else:
                    st.error("Failed to generate website. Please check the logs for details.")
            except Exception as e:
                st.error(f"Error generating website: {str(e)}")
    else:
        st.error("Please enter a website description.")

# Display generated code and preview if available
if st.session_state.generated_code:
    html_content, css_content, js_content = st.session_state.generated_code
    
    # Tabs for code and preview
    tab1, tab2, tab3, tab4 = st.tabs(["Preview", "HTML", "CSS", "JavaScript"])
    
    with tab1:
        st.subheader("Website Preview")
        
        # Create a temporary HTML file for preview
        preview_html_path = os.path.join(st.session_state.save_path, "preview.html")
        with open(preview_html_path, "w", encoding="utf-8") as f:
            f.write(st.session_state.website_html)
        
        # Display using HTML iframe with data URI to avoid rendering issues
        html_content_b64 = base64.b64encode(st.session_state.website_html.encode()).decode()
        
        iframe_code = f'''
        <iframe 
            src="data:text/html;base64,{html_content_b64}" 
            width="100%" 
            height="600px" 
            frameborder="0" 
            style="border: 1px solid #ddd; border-radius: 8px;">
        </iframe>
        '''
        
        st.components.v1.html(iframe_code, height=620)
        
        # Add a direct link to open in new tab
        if os.path.exists(os.path.join(st.session_state.save_path, "index.html")):
            preview_path = os.path.abspath(os.path.join(st.session_state.save_path, "index.html"))
            st.markdown(f"[Open website in new tab](file:///{preview_path})", unsafe_allow_html=True)
        
    with tab2:
        st.code(html_content, language="html")
        st.download_button("Download HTML", data=html_content, file_name="index.html")
        
    with tab3:
        st.code(css_content, language="css")
        st.download_button("Download CSS", data=css_content, file_name="styles.css")
        
    with tab4:
        st.code(js_content, language="javascript")
        st.download_button("Download JS", data=js_content, file_name="script.js")
    
    # Add download zip button
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

# Instructions
st.sidebar.title("How to use")
st.sidebar.markdown("""
1. Upload or generate a logo for your website
2. Describe your website in detail
3. Add keywords to fetch relevant images
4. Provide business name and color preferences
5. Click 'Generate Website' to create your custom website
6. Preview, download, or export the generated website

**Note**: Make sure you have the following environment variables in your .env file:
- NVIDIA_API_KEY
- PEXELS_API_KEY
""")

# Create a sample .env file if it doesn't exist
if not os.path.exists('.env'):
    st.sidebar.warning("No .env file found. Creating a sample file.")
    with open('.env', 'w') as f:
        f.write("# Add your API keys here\n")
        f.write("NVIDIA_API_KEY=your_nvidia_api_key_here\n")
        f.write("PEXELS_API_KEY=your_pexels_api_key_here\n")
    st.sidebar.info("Sample .env file created. Please add your API keys.")