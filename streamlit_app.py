import streamlit as st
import tempfile
import os
from PIL import Image
from imagedx_agent import analyze_medical_images

st.set_page_config(
    page_title="ImageDx AI - Medical Image Analyzer",
    page_icon="🏥",
    layout="wide"
)

def parse_analysis_sections(analysis_text):
    """Parse the analysis text into different sections."""
    sections = {
        "Image Type & Region": "",
        "Key Findings": "",
        "Diagnostic Assessment": "",
        "Patient-Friendly Explanation": "",
        "Research Context": ""
    }

    current_section = None
    lines = analysis_text.split('\n')

    for line in lines:
        if '### 1. Image Type & Region' in line:
            current_section = "Image Type & Region"
        elif '### 2. Key Findings' in line:
            current_section = "Key Findings"
        elif '### 3. Diagnostic Assessment' in line:
            current_section = "Diagnostic Assessment"
        elif '### 4. Patient-Friendly Explanation' in line:
            current_section = "Patient-Friendly Explanation"
        elif '### 5. Research Context' in line:
            current_section = "Research Context"
        elif current_section and line.strip():
            sections[current_section] += line + '\n'

    return sections

def save_uploaded_files(uploaded_files):
    """Save uploaded files to temporary directory and return paths."""
    temp_paths = []
    for uploaded_file in uploaded_files:
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{uploaded_file.name.split(".")[-1]}') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            temp_paths.append(tmp_file.name)
    return temp_paths

def main():
    st.title("🏥 ImageDx AI - Medical Image Analyzer")
    st.markdown("Upload medical images for AI-powered diagnostic analysis")

    with st.sidebar:
        st.header("📤 Upload Images")
        uploaded_files = st.file_uploader(
            "Choose medical image files",
            type=['png', 'jpg', 'jpeg', 'bmp', 'tiff'],
            accept_multiple_files=True,
            help="Upload one or more medical images for analysis"
        )

        additional_question = st.text_area(
            "Additional Question (Optional)",
            placeholder="e.g., What specific abnormalities should I look for?",
            help="Add any specific questions about the images"
        )

        analyze_button = st.button("🔍 Analyze Images", type="primary")

        st.warning(
            "⚠DISCLAIMER: This tool is for educational and informational purposes only. "
            "All analyses should be reviewed by qualified healthcare professionals. "
            "Do not make medical decisions based solely on this analysis."
        )

    if uploaded_files:
        st.subheader("📷 Uploaded Images")
        cols = st.columns(min(len(uploaded_files), 4))

        for idx, uploaded_file in enumerate(uploaded_files):
            with cols[idx % 4]:
                image = Image.open(uploaded_file)
                st.image(image, caption=uploaded_file.name, width=200)

    if analyze_button and uploaded_files:
        with st.spinner("🤖 Analyzing medical images... This may take a few moments."):
            try:
                temp_paths = save_uploaded_files(uploaded_files)

                question = additional_question if additional_question.strip() else "Analyze this medical image."

                if len(temp_paths) == 1:
                    result = analyze_medical_images(temp_paths[0], question)
                else:
                    result = analyze_medical_images(temp_paths, question)

                sections = parse_analysis_sections(result)

                tab1, tab2, tab3, tab4, tab5 = st.tabs([
                    "🔍 Image Type & Region",
                    "📋 Key Findings",
                    "⚕️ Diagnostic Assessment",
                    "👤 Patient Explanation",
                    "📚 Research Context"
                ])

                with tab1:
                    st.markdown("### Image Type & Region")
                    if sections["Image Type & Region"]:
                        st.markdown(sections["Image Type & Region"])
                    else:
                        st.info("No specific image type information found.")

                with tab2:
                    st.markdown("### Key Findings")
                    if sections["Key Findings"]:
                        st.markdown(sections["Key Findings"])
                    else:
                        st.info("No key findings information found.")

                with tab3:
                    st.markdown("### Diagnostic Assessment")
                    if sections["Diagnostic Assessment"]:
                        st.markdown(sections["Diagnostic Assessment"])
                    else:
                        st.info("No diagnostic assessment information found.")

                with tab4:
                    st.markdown("### Patient-Friendly Explanation")
                    if sections["Patient-Friendly Explanation"]:
                        st.markdown(sections["Patient-Friendly Explanation"])
                    else:
                        st.info("No patient explanation found.")

                with tab5:
                    st.markdown("### Research Context")
                    if sections["Research Context"]:
                        st.markdown(sections["Research Context"])
                    else:
                        st.info("No research context found.")

                with st.expander("📄 Full Analysis Report"):
                    st.markdown(result)

                for temp_path in temp_paths:
                    try:
                        os.unlink(temp_path)
                    except:
                        pass

            except Exception as e:
                st.error(f"❌ Error analyzing images: {str(e)}")
                st.info("Please ensure your images are valid medical images and try again.")

    elif analyze_button and not uploaded_files:
        st.warning("⚠️ Please upload at least one image before analyzing.")

    if not uploaded_files:
        st.markdown("""
        ## How to Use
        1. **Upload Images**: Use the sidebar to upload one or more medical images
        2. **Add Questions**: Optionally add specific questions about the images
        3. **Analyze**: Click the analyze button to get AI-powered insights
        4. **Review Results**: View the analysis organized in tabs by section

        ### Supported Formats
        - PNG, JPG, JPEG, BMP, TIFF
        - Multiple images supported for comparative analysis

        ### Analysis Includes
        - Image type and region identification
        - Key medical findings
        - Diagnostic assessment
        - Patient-friendly explanations
        - Research context and references
        """)

if __name__ == "__main__":
    main()