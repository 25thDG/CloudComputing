import streamlit as st
from openai import OpenAI
import requests
import re


# OpenAI client setup
LLM = "****"
client = OpenAI(
    base_url=LLM,
    api_key="-"
)

# Function to remove HTML tags because api response contains HTML
def remove_html_tags(text):
    #regular expression matchin anything starting with '<' and ending with '>'
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

@st.cache_data #API Call
def get_data(region, industry):
    jobicy_api = f"https://jobicy.com/api/v2/remote-jobs?count={15}&geo={region}&industry={industry}"
    response = requests.get(jobicy_api)
    if response.status_code == 200:
        return response.json()
    else:
        return None
    
    
def translator(words, LANGUAGE):
    if LANGUAGE == "English":
        return words
    response = ""
    if words:
        completion = client.chat.completions.create(
        model="tgi",
        messages=[
        {"role": "system", "content": f"Translate this:{words}; to this Language{LANGUAGE}; Dont add anything just return the Translated text"},#Always answer in {LANGUAGE}.Your Answer is Always {words} translated to {LANGUAGE}. Do not say that the Text has been translated. Dont add anything else" },
        {"role": "user", "content": f"{""}\nAntwort:"}
        ],
        stream=False,
        max_tokens=1500
    )
        response = completion.choices[0].message.content
    return response
    
    
st.header(':violet[JobHunt]', divider="violet")


col1, col2 = st.columns([9, 19])


# Initialize session state variables
if 'LANGUAGE' not in st.session_state:
    st.session_state.update({
        "LANGUAGE": None,
        "REGION": None,
        "INDUSTRY": None,
        "prev_counter": 0,
        "translated_text": "",
        "counter": 0,
        "messages": []
    })


# Streamlit column for dropdowns
with col1:
    LANGUAGE = st.selectbox(
        "Language", 
        (
            "English", "Spanish", "French", "German", "Portuguese", "Italian", "Dutch", "Turkish", 
            "Indonesian", "Vietnamese", "Polish", "Swedish", "Danish", 
            "Finnish", "Hungarian", "Norwegian", "Thai", "Czech", "Romanian", 
            "Slovak", "Bulgarian", "Croatian", "Serbian", "Ukrainian"
            
        ), label_visibility='collapsed')
        
    REGION = st.selectbox(
        "Region", 
        (
            "EMEA", "APAC", "LATAM", "USA", "Japan", "New Zealand", "Philippines", "Singapore",
            "South Korea", "Thailand", "Vietnam", "Australia", "Europe", "Austria", "Belgium", "Bulgaria",
            "Croatia", "Cyprus", "Czechia", "Denmark", "Estonia", "Finland", "France", "Germany", "Greece", 
            "Hungary", "Ireland", "Italy", "Latvia", "Lithuania", "Netherlands", "Norway", "Poland", 
            "Portugal", "Romania", "Slovakia", "Slovenia", "Spain", "Sweden", "Switzerland", "UK", "Israel", 
            "Türkiye", "United Arab Emirates", "China", "Argentina", "Brazil", "Costa Rica", "Mexico", "Canada"
            
        ), label_visibility='collapsed')
    
    INDUSTRY = st.selectbox(
        "Industry", 
        (
            "Business Development", "Copywriting & Content", "Customer Success", "Technical Support", 
            "Data Science", "Design & Creative", "Web & App Design", "DevOps & SysAdmin", "Engineering", 
            "Finance & Legal", "HR & Recruiting", "Marketing & Sales", "Sales", "SEO", 
            "Social Media Marketing", "Product & Operations", "Programming"
            
        ), label_visibility='collapsed')

# Check if LANGUAGE, REGION, or INDUSTRY changed
language_changed = LANGUAGE != st.session_state.LANGUAGE
region_changed = REGION != st.session_state.REGION
industry_changed = INDUSTRY != st.session_state.INDUSTRY
counter_changed = False
changed = True


# Update session state
st.session_state.LANGUAGE = LANGUAGE
st.session_state.REGION = REGION
st.session_state.INDUSTRY = INDUSTRY

# API call setup
REGION = REGION.replace(" ", "-").lower()
industry_dict = {"Business Development": "business", "Copywriting & Content": "copywriting", "Customer Success": "supporting", "Technical Support": "technical-support", "Data Science" : "data-science", "Design & Creative" : "design-multimedia", "Web & App Design" : "web-app-design", "DevOps & SysAdmin": "admin", "Engineering" : "engineering", "Finance & Legal" : "accounting-finance", "HR & Recruiting" : "hr", "Marketing" : "marketing", "Sales" : "seller", "SEO" : "seo", "Social Media Marketing" : "smm", "Product & Operations" : "management", "Programming" : "dev"}
INDUSTRY = industry_dict[INDUSTRY]
#15 is the max amount of jobs
jobicy_api=f"https://jobicy.com/api/v2/remote-jobs?count={15}&geo={REGION}&industry={INDUSTRY}"

# get API response
response = requests.get(jobicy_api)
if response.status_code == 200:
    data = response.json()
    available_jobs = data.get('jobCount')


def increment_counter():
    st.session_state.counter = (st.session_state.counter + 1) % available_jobs
    

if response.status_code == 200:
    if (region_changed or industry_changed):
        st.session_state.counter = 0
        st.session_state.prev_counter = 0
    with col1:
        increment_button, page_num = st.columns(2)
        with increment_button:
            if st.button(translator("Next Page", LANGUAGE)):
                increment_counter()
                counter_changed = True
            else:
                counter_changed = False
                
        with page_num:
            st.write(f'{translator("Page",LANGUAGE)}: {st.session_state.counter + 1}-{available_jobs}')
        url = data['jobs'][st.session_state.counter]['url']
        #Tried to build the Streamlitbutton from scratch. THis button will get us to the Job Posting
        st.markdown(f'''
                <a href="{url}" target="_blank">
                    <button style="
                        background-color: #131720; 
                        color: white; 
                        border: 1px solid #42444C; 
                        padding: 8px 16px; 
                        font-size: 14px; 
                        cursor: pointer;
                        border-radius: 7px;
                        display: inline-block;
                        transition: background-color 0.3s, border-color 0.3s, color 0.3s;
                    "
                    onmouseover="this.style.backgroundColor='#555';this.style.borderColor='#aaa';"
                    onmouseout="this.style.backgroundColor='#333';this.style.borderColor='#777';">
                        {translator("Go To Job Posting",LANGUAGE)}
                    </button>
                </a>
            ''', unsafe_allow_html=True)

    job_description = remove_html_tags(data['jobs'][st.session_state.counter]['jobDescription']) if available_jobs > 0 else ""
    if job_description and (language_changed or region_changed or industry_changed or counter_changed or counter_changed):
        
        translation = client.chat.completions.create(
            model="tgi",
            messages=[
                {"role": "system", "content": f"Just Translate the Text you get into this = {LANGUAGE}. AND FORMAT IT like a MARKDOWN. dont add anything. DO NOT SAY THAT the text has been translated. Just return the text Translated. ALWAYS END IT with Lines(-) indicating the end"},
                {"role": "user", "content": f"{job_description}\nAntwort:"}
            ],
            stream=True,
            max_tokens=1500
        )

        with col2:            
            output = st.write_stream(m.choices[0].delta.content for m in translation if not m.choices[0].finish_reason)
            st.session_state.translated_text = output
            changed = False
            
        st.session_state.prev_counter = st.session_state.counter
    else:
        changed = True
    
    
    
if  ((not language_changed or  not region_changed or not industry_changed) and (changed)):
    with col2:
        st.write(st.session_state.translated_text)

placeholder = st.empty()

query = st.text_area(translator("How can I help you",LANGUAGE),placeholder=translator("Ask for advice or give him your application",LANGUAGE))
if query:
    completion = client.chat.completions.create(
    model="tgi",
    messages=[
    {"role": "system", "content": f"Always answer in {LANGUAGE}.Answer my Question regarding this text {st.session_state.translated_text}'." },
    {"role": "user", "content": f"{query}\nAntwort:"}
    ],
    stream=True,
    max_tokens=1500
)
    
    placeholder.write_stream(m.choices[0].delta.content for m in completion if not m.choices[0].finish_reason)  

