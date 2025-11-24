import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os 

# Load .env
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Configure Gemini
genai.configure(api_key=gemini_api_key)

# Load model properly
model = genai.GenerativeModel("gemini-2.5-flash")

# Streamlit UI
st.set_page_config(page_title="SQL Query Generator", page_icon=":guardsman:")
st.title("SQL Query Generator")

col1, col2, col3 = st.columns([1,2,1])
with col2:
    st.image('images.png', width=200)

# Intro Section
st.markdown(
    """
    <div style="text-align: center">
        <h1> SQL QUERY GENERATOR </h1>
        <h3>I can generate SQL queries for you</h2>
        <h4>With explanation as well</h4>
        <p>This tool allows you to generate SQL queries based on plain English.</p>
    </div>
    """,
    unsafe_allow_html=True
)

# Text Input
text_input = st.text_area("Enter your query in plain English")

# Button
submit_button = st.button("Generate SQL Query")

if submit_button and text_input.strip() != "":
    with st.spinner("Generating SQL query..."):

        # 1. Generate SQL Query
        template = """
        Create a SQL query snippet using the below text:

        {text_input}

        I just want a SQL query.
        """
        query_prompt = template.format(text_input=text_input)
        response = model.generate_content(query_prompt)

        sql_query = response.text.strip().lstrip("```sql").rstrip("```")

        # 2. Expected Output
        expected_sql_prompt = f"""
        What would be the expected output of the following SQL query:

        {sql_query}

        Provide a simple sample table output with NO explanation.
        """
        output = model.generate_content(expected_sql_prompt)

        # 3. Explanation
        explanation_prompt = f"""
        Explain this SQL query in the simplest way:

        {sql_query}

        Provide a very simple explanation.
        """
        explanation_response = model.generate_content(explanation_prompt)

    # --- Display Results ---
    with st.container():
        st.success("SQL query generated successfully!")

        st.subheader("SQL Query:")
        st.code(sql_query, language="sql")

        st.subheader("Expected Output:")
        st.markdown(output.text)

        st.subheader("Explanation:")
        st.markdown(explanation_response.text)
