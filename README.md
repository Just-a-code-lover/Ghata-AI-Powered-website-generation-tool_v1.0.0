# GPT-4 Powered Website Generator

This project is a Streamlit-based web application that uses GPT-4 to generate custom websites based on user input. It allows users to describe their desired website, and the app generates HTML, CSS, and JavaScript code accordingly. Additionally, the app can generate a logo using the `FLUX.1-schnell` model via Hugging Face, based on a user-provided description.

## Features

- **Logo upload or AI-generated logo creation**: Users can either upload their own logo or provide a description, and the app will generate a logo using the `FLUX.1-schnell` model from Hugging Face.
- **Website description input**: Users can describe the layout, design, and functionality of their desired website.
- **Customizable color scheme**: Users can select a primary and secondary color to personalize their website's appearance.
- **GPT-4 powered code generation**: The app uses GPT-4 via RapidAPI to generate the website’s HTML, CSS, and JavaScript code.
- **Live preview of generated website**: The generated code is immediately rendered in the app for users to preview.
- **Download options for individual files and complete website as a ZIP**: Users can download the generated HTML, CSS, and JavaScript files individually or as a ZIP archive.

## How It Works

### Logo Generation with Hugging Face's FLUX.1-schnell Model

When users choose to generate a logo, the app sends a request to the `FLUX.1-schnell` model via Hugging Face's API, passing the user-provided description. The model then returns a generated image based on the input description, which can be saved and used as the website's logo.

### GPT-4 API Integration for Code Generation

The app takes the user's website description and sends it to GPT-4 via the RapidAPI interface. GPT-4 generates the entire website's code, including HTML, CSS, and JavaScript, based on the description.

### Code Processing and Separation

To ensure clean and usable code, the app processes the GPT-4 output using regex and BeautifulSoup:

- **Regex**: The generated code is parsed using regex to identify and extract the different sections of the website code (HTML, CSS, JavaScript).
- **BeautifulSoup**: The HTML portion is further processed using BeautifulSoup to ensure proper structure and clean formatting.
- After processing, the HTML, CSS, and JavaScript code is saved into separate files (`index.html`, `styles.css`, `script.js`), making it easier for users to manage the different components of their website.

## Requirements

- Python 3.7+
- Streamlit
- Requests
- BeautifulSoup4
- Pillow
- Other dependencies (see `requirements.txt`)

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/gpt4-website-generator.git
   cd gpt4-website-generator
   ```

2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your environment variables:
   - Create a `.env` file in the project root
   - Add your API keys:
     ```bash
     RAPIDAPI_KEY=your_rapidapi_key_here
     HUGGINGFACE_API_KEY=your_huggingface_api_key_here
     ```

## Usage

1. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. Open your web browser and go to the URL provided by Streamlit (usually `http://localhost:8501`).

3. Follow the steps in the app to generate your website:
   - Upload or generate a logo using the `FLUX.1-schnell` model from Hugging Face.
   - Describe your website and customize its color scheme.
   - Generate the website using GPT-4, and view or download the HTML, CSS, and JavaScript files.
   - Download the website as a ZIP file, which includes the generated logo and the website files.

## Deployment

This app can be deployed on Streamlit Community Cloud. Follow these steps:

1. Push your code to a GitHub repository.
2. Go to [Streamlit Community Cloud](https://streamlit.io/cloud).
3. Connect your GitHub account and select your repository.
4. Deploy the app.
5. Set up your environment variables in the Streamlit Cloud dashboard.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- OpenAI for the GPT-4 API
- Hugging Face for the image generation API
- Streamlit for the web app framework

---