import streamlit as st
import pandas as pd
import re
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from PyPDF2 import PdfReader
from PIL import Image
from streamlit_navigation_bar import st_navbar #for navigation
from openai import OpenAI
from dotenv import load_dotenv
import os


load_dotenv()
#styling

# #F95CA4
styles = {
    "nav": {
        "background-color": "#00008b"
    },
    "img": {
        "padding-right": "14px",
    },
    "span": {
        "color": "white",
        "padding": "14px",
    },
    "active": {
        "color": "var(--text-color)",
        "background-color": "#EDE8F5",
        "font-weight": "normal",
        "padding": "14px",
    }
}

#open function from previously stored
jd = pd.read_csv("jobs_data.csv")


#function for chat gpt reading skills:--------
client = OpenAI(
    api_key=os.environ.get("OPEN_AI_KEY"),
)

def resume_skill(resume, job_description):
    response = client.chat.completions.create(
                  model="gpt-3.5-turbo-0125",
                  response_format={ "type": "text" },
                  messages=[
                    {"role": "system",
                     "content": "You are a helpful assistant who analyzes resumes and job descriptions data and tells me what I am lacking. You ALWAYS COMPLETE YOUR SENTENCES, given the max number of tokens set at 250. No cutoffs. You also always list your answers and bold where necessary"},
                    {"role": "user", 
                     "content": f"Read and understand this resume:{resume}. Next, based this job description {job_description}, tell me the skills I am lacking. Also, I ask that you list the weakness and bold them. Do not mention that I need to improve in skills that I already have, e.g. If data analysis is in my resume and the job description, let me know that I meet some of the requirments, if not, let me know how I do not "}
                  ],
            temperature = 1
                )
    return response.choices[0].message.content

#function to get text
# Function to extract text from a PDF file-like object
def get_pdf_text(file_obj):
    text = ''
    pdf_text = PdfReader(file_obj)
    for page in pdf_text.pages:
        text = text + page.extract_text()
    return text

# Function to preprocess text
def preprocess_text(text):
    # Lowercasing
    text = text.lower()
    # Remove punctuation
    text = re.sub(r'[^\w\s]', '', text)
    return text

# Function to calculate cosine similarity using TF-IDF vectors
def get_cosine_similarity(text1, text2):
    # Preprocess text
    text1 = preprocess_text(text1)
    text2 = preprocess_text(text2)

    # Create TF-IDF vectorizer
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([text1, text2])

    # Calculate cosine similarity
    similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix)[0][1]
    return similarity

def filter_job_data(user_input_word, data):
    # Assume the column containing job descriptions is named "Description"
    description_column = data["Description"]

    # Filter the DataFrame based on whether the word is present in the descriptions
    filtered_data = data[description_column.str.contains(user_input_word, case=False)]

    # Return the filtered DataFrame
    return filtered_data

def filter_remote_data(data):
    # Assume the column containing job descriptions is named "Description"
    description_column = data["Location"]

    # Filter the DataFrame based on whether the word is present in the descriptions
    filtered_data_remote = data[description_column.str.contains("Remote", case=False)]

    # Return the filtered DataFrame
    return filtered_data_remote

def filter_hybrid_data(data):
    # Assume the column containing job descriptions is named "Description"
    description_column = data["Location"]

    # Filter the DataFrame based on whether the word is present in the descriptions
    filtered_data_hybrid = data[description_column.str.contains("Hybrid", case=False)]

    # Return the filtered DataFrame
    return filtered_data_hybrid

#only display jobs that have a salary posted
def filter_salary_data(data):
    # Assume the column containing job descriptions is named "Description"
    salary_column = data["Salary"]

    # Filter the DataFrame based on whether the word is not present in the descriptions
    filtered_data_salary = data[salary_column != "-99"]

    # Return the filtered DataFrame
    return filtered_data_salary




# Function to load and display image
def display_image(image_path, caption):
    image = Image.open(image_path)
    st.image(image, caption=caption, use_column_width=True)

def main():
    load_dotenv()
    # Set page title and icon
    st.set_page_config(page_title="Job Quest", page_icon=":page_with_curl:")
    #st.title("Job Quest")
    #page = st.sidebar.radio("Select Page:", ["Home", "Jobs", "Skill Gaps"], label_visibility="collapsed")
    page = st_navbar(["Home", "Jobs", "Skill Gaps"], styles = styles)

    #st.sidebar.image("job_quest_logo.png", width=100)
    if page != "Home":
        # Navigation menu in the header
        st.sidebar.header(":blue[Job Explorer]", divider='rainbow')
        # Dropdown menus
        #st.sidebar.title("Dropdown Menus")

        # Dropdown 1
        job_title = st.sidebar.text_input("Enter your Dream job", "")

        # Dropdown 2
        remote_or_not = st.sidebar.selectbox("Remote?", ["Remote", "Hybrid", "All"])

        # Dropdown 3
        salary_or_not = st.sidebar.selectbox("Exclude Jobs Without Salary?", ["Yes", "No"])


    if page == "Home":
      # Display main title and welcoming message
        st.header(":blue[Welcome to JobQuest]", divider='rainbow')
        st.write("Introducing JobQuest, your ultimate companion in the quest for career excellence!")

        # Display main image
        display_image("job_quest_image.jpg", "JobQuest")

        # Add separator
        #st.markdown("---")

        # Explain how Job Quest works
        st.header(":blue[How JobQuest Works]", divider='rainbow')
        st.write("""
        JobQuest is designed to simplify your job search journey. Here's how it works:

        1. **Explore Job Opportunities:** Navigate to the "Jobs" page to discover a wide range of job listings tailored to your preferences.
        2. **Identify Skill Gaps:** Head over to the "Skill Gaps" page to upload your resume and uncover areas for skill improvement based on job matching analysis.
        3. **Make Informed Decisions:** Armed with insights from Job Quest, you'll be equipped to make informed career decisions and take your professional journey to new heights!

        Ready to embark on your career adventure? Navigate to the "Jobs" or "Skill Gaps" page to get started!
        """)

        # Add separator
        st.markdown("---")

        # Provide contact information
        st.header(":blue[Contact Us]", divider='rainbow')
        st.write("Have questions or feedback? Reach out to us at maduabum@umich.edu")

        # Add separator
        st.markdown("---")

        # Add disclaimer
        st.write("**Disclaimer:** Job Quest is a project for educational purposes only. All job listings and data provided are for demonstration purposes and do indeed reflect actual job opportunities.")


        
    if page == "Jobs":
        st.header(":blue[Jobs]", divider='rainbow')
        st.write("""
        Welcome to the Jobs page!

        Here, you can explore job opportunities based on your preferences.
         You can filter jobs by entering your dream job title, selecting
                  whether you prefer remote, hybrid, or all types of jobs,
                  and choose to exclude listings without salary information.

        Once you've entered your criteria, relevant job listings will be displayed below. 
                 You can click on the "Open Link" button to explore each job opportunity further.
        """)

    if page == "Skill Gaps":   
        st.header(":blue[Skill Gaps]", divider='rainbow')
        st.write("Welcome to the Skill Gaps page!")
        st.write("""
                    Understanding your skill gaps is crucial for career growth. Here, you can upload your resume to identify areas for improvement based on the job you've selected. 

                    Once you've uploaded your resume, we'll analyze it against relevant job descriptions and provide insights into where you excel and where you may need to focus on development.

                    Get started by uploading your resume and let's uncover opportunities for skill enhancement!
                    """)
         # Sidebar for uploading PDF (only in the skill Gaps Tab)
        st.sidebar.header(":blue[Upload your resume PDF]", divider='rainbow')
        uploaded_file = st.sidebar.file_uploader("Choose a PDF file")
        process_button = st.sidebar.button(':blue[Process]')
        
        if uploaded_file:
            st.sidebar.success("PDF successfully uploaded!")
            # Perform analysis on the uploaded PDF file
            # Add your analysis code here


    # Main content
    if page != "Home":
        if job_title:
            filter_job = filter_job_data(job_title, jd)
            #all but last row
            filtered_job = filter_job.iloc[:, :-1]
            if remote_or_not == "Remote":
                filter_job = filter_remote_data(filter_job)
                filtered_job = filter_remote_data(filtered_job)
            elif remote_or_not == "Hybrid":
                filter_job = filter_hybrid_data(filter_job)
                filtered_job = filter_hybrid_data(filtered_job)
            if salary_or_not == "Yes":
                filter_job = filter_salary_data(filter_job)
                filtered_job = filter_salary_data(filtered_job)
            #elif salary_or_not == "No":
                #all but last row
             #   filtered_job = filtered_job 
            if len(filtered_job)== 1:
                st.write(f"\n\n**Only one job was found matching your description:**")
            elif len(filtered_job) >1:
                st.write(f"\n\n**{len(filtered_job)} jobs were found matching your description:**")
            else:
                st.write(f"\n\n**No job openings matching your description was posted within the last 2 weeks on Indeed**")
            

            # Configure the Link column
            st.data_editor(
                    filtered_job,
                        column_config={
                        "Link": st.column_config.LinkColumn(
                            label="Visit Link",  # Customize the label as needed
                            help="Click to visit",  # Tooltip for the column header
                            display_text="Open link"  # Text displayed in each cell
                        )
                    },
                    hide_index=True,
                    key = "1" # put key incase you have to display the same value
        )
    
    if page == "Skill Gaps":
        if uploaded_file:
            if process_button and job_title:
                if len(filter_job) == 0:
                    st.write('\n\n**No jobs matching your description are available, so no analysis can be performed. Change selections and try again.**')
                
                else:
                    pdf_text = get_pdf_text(uploaded_file)
                        # Calculate cosine similarity scores and store them in a new column 'Similar'
                    filter_job['Similar'] = filter_job['Description'].apply(lambda x: get_cosine_similarity(pdf_text, x))

                        # Sort the DataFrame by the 'Similar' column in descending order
                    filter_job_sorted = filter_job.sort_values(by='Similar', ascending=False)
                    if len(filter_job_sorted.head()) == 1:
                        st.markdown("**As there was only one job found, the analysis was performed on that job:**")
                    elif len(filter_job_sorted.head()) > 1:
                        st.markdown(f"**Here are the top {len(filter_job_sorted.head())} jobs arranged from most compatable to the least compatable:**")
                    
                    top_5_rel_job = filter_job_sorted.iloc[:,:-2].head()
                
                    st.data_editor(
                        top_5_rel_job,
                            column_config={
                            "Link": st.column_config.LinkColumn(
                                    label="Visit Link",  # Customize the label as needed
                                    help="Click to visit",  # Tooltip for the column header
                                    display_text="Open link"  # Text displayed in each cell
                                )
                            },
                            hide_index=True,
                            key = "2"
                            )
                   
                    for i, jobs in enumerate(filter_job_sorted["Description"].head()):
                        st.write(f"For job {i+1}:")
                        with st.spinner("Processing..."):
                            st.write(resume_skill(pdf_text, jobs))
                            st.write("\n\n")

if __name__ == "__main__":
    main()
