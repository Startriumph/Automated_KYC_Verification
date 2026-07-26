import streamlit as st
import requests
from PIL import Image

FLASK_API_URL = "http://127.0.0.1:5000"

st.set_page_config(
    page_title="Automated KYC & Verification Platform",
    page_icon="🛡️",
    layout="wide"
)

st.title("🛡️ Automated KYC & Document Verification System")
st.caption("Powered by Gemini Vision Multimodal AI, Flask & SQLite")

tab1, tab2 = st.tabs(["📄 New KYC Scan", "📊 Verified Database Records"])

# --- TAB 1: Document Upload & Verification ---
with tab1:
    st.header("Upload Application Form or ID Card")
    st.write("Supports JPEG, PNG, or scanned PDFs exported as images.")

    uploaded_file = st.file_uploader("Select ID or Form Image", type=["jpg", "jpeg", "png"])

    col1, col2 = st.columns([1, 1])

    if uploaded_file is not None:
        with col1:
            st.subheader("Document Preview")
            image = Image.open(uploaded_file)
            st.image(image, use_container_width=True)

        with col2:
            st.subheader("Automated Processing")
            if st.button("🚀 Process & Extract KYC Data", type="primary"):
                with st.spinner("Extracting OCR text & validating with Gemini Vision..."):
                    try:
                        # Reset file pointer and send to Flask backend
                        uploaded_file.seek(0)
                        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
                        
                        response = requests.post(f"{FLASK_API_URL}/api/verify-kyc", files=files)
                        
                        if response.status_code == 200:
                            result = response.json()
                            extracted = result["extracted_data"]

                            if result["status"] == "PASSED":
                                st.success(f"✅ Record #{result['record_id']} Verified & Saved!")
                            else:
                                st.warning(f"⚠️ Record #{result['record_id']} Flagged! Missing fields: {', '.join(result['missing_fields'])}")

                            # Display formatted attributes
                            st.json(extracted)

                        else:
                            st.error(f"Error {response.status_code}: {response.text}")

                    except requests.exceptions.ConnectionError:
                        st.error("❌ Could not connect to Flask Backend. Ensure `app.py` is running on port 5000.")

# --- TAB 2: SQLite Database View ---
with tab2:
    st.header("Logged KYC Records")
    if st.button("🔄 Refresh Database"):
        st.rerun()

    try:
        res = requests.get(f"{FLASK_API_URL}/api/records")
        if res.status_code == 200:
            data = res.json()
            if data:
                st.dataframe(data, use_container_width=True)
            else:
                st.info("No records found in database yet. Process a document first.")
        else:
            st.error("Failed to load records from backend API.")
    except requests.exceptions.ConnectionError:
        st.error("❌ Could not connect to Flask Backend server.")