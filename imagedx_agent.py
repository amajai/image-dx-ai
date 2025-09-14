import base64
from PIL import Image
from dotenv import load_dotenv
from datetime import datetime
from typing import Union, List

from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from langchain_tavily import TavilySearch
from langchain.schema import HumanMessage
from utils import get_today_str
load_dotenv()

def encode_image_to_base64(image_path: str) -> str:
    """Encode image file to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def process_images(images: Union[str, List[str]]) -> List[dict]:
    """Process single image or list of images into format suitable for LLM."""
    if isinstance(images, str):
        images = [images]

    processed_images = []
    for image_path in images:
        try:
            # Verify it's an image file
            with Image.open(image_path) as img:
                # Get image format
                img_format = img.format.lower()

            # Encode to base64
            base64_image = encode_image_to_base64(image_path)

            processed_images.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/{img_format};base64,{base64_image}"
                }
            })
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            continue

    return processed_images

prompt = f"""
You are a highly skilled medical imaging expert with extensive knowledge in radiology and diagnostic imaging. Analyze the patient's medical image and structure your response as follows:
Today date: {get_today_str()}

### 1. Image Type & Region
- Specify imaging modality (X-ray/MRI/CT/Ultrasound/etc.)
- Identify the patient's anatomical region and positioning
- Comment on image quality and technical adequacy

### 2. Key Findings
- List primary observations systematically
- Note any abnormalities in the patient's imaging with precise descriptions
- Include measurements and densities where relevant
- Describe location, size, shape, and characteristics
- Rate severity: Normal/Mild/Moderate/Severe

### 3. Diagnostic Assessment
- Provide primary diagnosis with confidence level
- List differential diagnoses in order of likelihood
- Support each diagnosis with observed evidence from the patient's imaging
- Note any critical or urgent findings

### 4. Patient-Friendly Explanation
- Explain the findings in simple, clear language that the patient can understand
- Avoid medical jargon or provide clear definitions
- Include visual analogies if helpful
- Address common patient concerns related to these findings

### 5. Research Context
IMPORTANT: Use the Travily search tool to:
- Find recent medical literature about similar cases
- Search for standard treatment protocols
- Provide a list of relevant medical links of them too
- Research any relevant technological advances
- Include 2-3 key references to support your analysis

Format your response using clear markdown headers and bullet points. Be concise yet thorough.
"""

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

tavily_tool = TavilySearch()

agent = create_react_agent(
    llm,
    [tavily_tool],
    prompt=prompt
)

def analyze_medical_images(images: Union[str, List[str]], question: str = "Analyze this medical image.") -> str:
    """
    Analyze medical images using the agent.
    """
    processed_images = process_images(images)

    if not processed_images:
        return "Error: No valid images were processed."

    message_content = [{"type": "text", "text": question}] + processed_images

    message = HumanMessage(content=message_content)

    result = agent.invoke({"messages": [message]})

    return result["messages"][-1].content

if __name__ == "__main__":
    # Example usage
    # Single image analysis
    result = analyze_medical_images("q.jpg")
    print(result)

    # Multiple images analysis
    # result = analyze_medical_images(["image1.jpg", "image2.jpg"], "Compare these two scans.")
    # print(result)

    pass
