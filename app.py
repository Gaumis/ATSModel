from dotenv import load_dotenv

load_dotenv()

import streamlit as st
import os
import io
import docx2pdf
import base64
from PIL import Image
import pdf2image
import google.generativeai as genai
from docx2pdf import convert

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

def get_gemini_response(input, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content([input, pdf_content[0], prompt])
    return response.text

import tempfile
from docx2pdf import convert

def input_doc_setup(uploaded_file):
    if uploaded_file is not None:
        try:
            with tempfile.TemporaryFile() as temp_docx, tempfile.NamedTemporaryFile(delete=False) as temp_pdf:
                temp_docx.write(uploaded_file.read())
                temp_docx.seek(0)

                convert(temp_docx.name, temp_pdf.name)

                with open(temp_pdf.name, 'rb') as pdf_file:
                    images = pdf2image.convert_from_bytes(pdf_file.read())

                    first_page = images[0]
                    img_byte_arr = io.BytesIO()
                    first_page.save(img_byte_arr, format='JPEG')
                    img_byte_arr = img_byte_arr.getvalue()

                    doc_parts = [{
                        "mime_type": "image/jpeg",
                        "data": base64.b64encode(img_byte_arr).decode()
                    }]

                    return doc_parts

        except Exception as e:
            print("Error during DOCX conversion:", e)
            raise ValueError("Failed to process DOCX file")

def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        ## Convert the PDF to image
        images=pdf2image.convert_from_bytes(uploaded_file.read())

        first_page=images[0]

        # Convert to bytes
        img_byte_arr = io.BytesIO()
        first_page.save(img_byte_arr, format='JPEG')
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()  # encode to base64
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")
    
def input_file_setup(uploaded_file):
    if uploaded_file is not None:
        if uploaded_file.type == "application/pdf":
            return input_pdf_setup(uploaded_file)  # Handle PDFs as before
        elif uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document" or uploaded_file.name.lower().endswith(".docx"):
            return input_doc_setup(uploaded_file)
        else:
            raise ValueError("Unsupported file type")
    else:
        raise FileNotFoundError("No file uploaded")

## Streamlit App

st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")
input_text=st.text_area("Job Description: ", key="input")
uploaded_file=st.file_uploader("Upload your Resume(PDF).....", type=["pdf","docx"])

if uploaded_file is not None:
    st.write("PDF Uploaded Successfully")

submit1 = st.button("Tell me about the Resume")
submit2 = st.button("How can I improve my skills")
submit3 = st.button("Percentage match")


input_prompt1 = """
 You are an experienced Technical Human Resource Manager with technical experience in the field of 
 web development, Python Full stack development, Python Backend Development, your task is to review the provided resume against the job description. 
  Please share your professional evaluation on whether the candidate's profile aligns with the role. 
 Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are an skilled ATS (Applicant Tracking System) scanner with a deep understanding of Python FullStack Development and ATS functionality, 
your task is to evaluate the resume against the provided job description. give me the percentage of match if the resume matches
the job description. First the output should come as percentage and then keywords missing and last final thoughts.
"""

if submit1:
    if uploaded_file is not None:
        pdf_content=input_file_setup(uploaded_file)
        response=get_gemini_response(input_prompt1,pdf_content,input_text)
        st.subheader("The Repsonse is")
        st.write(response)
    else:
        st.write("Please uplaod the resume")

elif submit3:
    if uploaded_file is not None:
        pdf_content=input_file_setup(uploaded_file)
        response=get_gemini_response(input_prompt3,pdf_content,input_text)
        st.subheader("The Repsonse is")
        st.write(response)
    else:
        st.write("Please uplaod the resume")




