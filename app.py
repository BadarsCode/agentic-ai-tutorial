from dotenv import load_dotenv
import streamlit as st 
import sqlite3 
import os 
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))


def get_gemini_response(question,prompt):
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content([prompt[0] , question])
    return response.text


# function to retrieve query from the database
def read_sql_query(sql, db):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    cur.execute(sql)
    rows= cur.fetchall()
    conn.commit()
    conn.close()
    for row in rows:
        print(row)
    return rows



prompt = """
You are an intelligent SQL query generator.
Your job is to convert natural language text into a valid, safe, and syntactically correct SQL query
for the following database schema without any other text just provide the SQL Query without any explaination.
don't write any orther textand the query must be in text form and not in code form.

--------------------------------------------------
DATABASE SCHEMA:able name: s
--------------------------------------------------
Database name: student
Ttudents

Columns:
- name (VARCHAR)
- email (VARCHAR)
- number (VARCHAR)
- address (VARCHAR)
- class (VARCHAR)

--------------------------------------------------
INSTRUCTIONS:
--------------------------------------------------
1. Understand the user request written in plain English.
2. Generate ONLY an SQL query (no explanations, no markdown, no extra text).
3. The query must be compatible with MySQL syntax.
4. Always use the table 'students' from the database 'student'.
5. Use column names exactly as given in the schema.
6. If a column or intent is unclear, make a reasonable assumption consistent with the schema.
7. Use single quotes (' ') for string values.
8. If user asks to “show”, “get”, “display”, “fetch”, or “list”, use SELECT.
9. If user asks to “add”, “insert”, or “register”, use INSERT INTO.
10. If user asks to “update” or “edit”, use UPDATE.
11. If user asks to “delete” or “remove”, use DELETE FROM.
12. Never perform DROP or TRUNCATE operations unless explicitly requested.
13. Always include a WHERE clause when modifying or deleting data unless user explicitly says “delete all”.
14. Return ONLY the SQL query — no explanations, no comments, no markdown.

If the user’s request is unrelated to database operations, respond exactly with:
"I can only generate SQL queries for the 'students' table in the 'student' database."
--------------------------------------------------

Now, based on the user's request below, generate the SQL query only don't need any explaination or any text just the sql query for running in your database:
"""


# Streamlit App

# set page configuration with a title 
st.set_page_config(page_title="SQL Query Generator App")

st.markdown(" GEMINI APP:  YOur AI-Powered SQL Assistant")
st.markdown("Ask Any Question: And I will Generate SQL Query for you")


question = st.text_input("Enter your query in plan English:", key='input')

submit = st.button("Generate SQL Query")

if submit:
    response = get_gemini_response(question, prompt)
    print(response)
    response= read_sql_query(response, "student.db")
    st.subheader(" The Response is:")
    for row in response:
        print(row)
        st.subheader("row")
