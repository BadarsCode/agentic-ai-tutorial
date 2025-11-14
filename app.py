# from dotenv import load_dotenv
# import streamlit as st
# import sqlite3
# import os
# import google.generativeai as genai

# # ✅ Load environment variables
# load_dotenv()

# # ✅ Configure Gemini API
# genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# # ✅ Function to generate SQL query using Gemini
# def get_gemini_response(question, prompt):
#     model = genai.GenerativeModel("gemini-2.5-flash")
#     response = model.generate_content([prompt, question])
#     return response.text.strip()

# # ✅ Function to execute SQL query on SQLite database
# def read_sql_query(sql, db):
#     try:
#         conn = sqlite3.connect(db)
#         cur = conn.cursor()
#         cur.execute(sql)
#         rows = cur.fetchall()
#         conn.commit()
#         conn.close()
#         return rows
#     except Exception as e:
#         return [("Error executing query:", str(e))]

# # ✅ Prompt for Gemini model
# prompt = """
# You are an intelligent SQL query generator.
# Your job is to convert natural language text into a valid, safe, and syntactically correct SQL query
# for the following database schema. Return only the SQL query (plain text, no explanation, no markdown).

# --------------------------------------------------
# DATABASE SCHEMA:
# --------------------------------------------------
# Database name: student
# Table name: students

# Columns:
# - name (VARCHAR)
# - email (VARCHAR)
# - number (VARCHAR)
# - address (VARCHAR)
# - class (VARCHAR)

# --------------------------------------------------
# INSTRUCTIONS:
# --------------------------------------------------
# 1. Understand the user request written in plain English.
# 2. Generate ONLY an SQL query (no explanations, no markdown, no extra text).
# 3. The query must be compatible with SQLite syntax.
# 4. Always use the table 'students' from the database 'student'.
# 5. Use column names exactly as given in the schema.
# 6. If a column or intent is unclear, make a reasonable assumption consistent with the schema.
# 7. Use single quotes (' ') for string values.
# 8. If user asks to “show”, “get”, “display”, “fetch”, or “list”, use SELECT.
# 9. If user asks to “add”, “insert”, or “register”, use INSERT INTO.
# 10. If user asks to “update” or “edit”, use UPDATE.
# 11. If user asks to “delete” or “remove”, use DELETE FROM.
# 12. Never perform DROP or TRUNCATE operations unless explicitly requested.
# 13. Always include a WHERE clause when modifying or deleting data unless user explicitly says “delete all”.
# 14. Return ONLY the SQL query — no explanations, no comments, no markdown.

# If the user’s request is unrelated to database operations, respond exactly with:
# "I can only generate SQL queries for the 'students' table in the 'student' database."
# --------------------------------------------------
# Now, based on the user's request below, generate the SQL query only:
# """

# # ✅ Streamlit App Setup
# st.set_page_config(page_title="AI SQL Query Generator")

# st.title("🤖 GEMINI APP: Your AI-Powered SQL Assistant")
# st.markdown("Ask any question in plain English, and I’ll generate and execute the SQL query for you!")

# question = st.text_input("Enter your question:", key='input')

# if st.button("Generate and Run SQL Query"):
#     if question.strip() == "":
#         st.warning("⚠️ Please enter a query.")
#     else:
#         # Generate SQL query using Gemini
#         sql_query = get_gemini_response(question, prompt)
#         st.subheader("🧠 Generated SQL Query:")
#         st.code(sql_query, language="sql")

#         # Execute query on SQLite database
#         result = read_sql_query(sql_query, "student.db")

#         st.subheader("📊 Query Result:")
#         if len(result) == 0:
#             st.info("No records found or query executed successfully.")
#         else:
#             for row in result:
#                 st.write(row)





import os
import sqlite3
from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai

# ============================
#   CREATE TABLE FUNCTION
# ============================
def create_table_in_base_dir(base_dir, db_name, create_query):
    """
    Creates a table in an SQLite database located inside base_dir.
    """
    os.makedirs(base_dir, exist_ok=True)  # ensure directory exists

    # Build DB path
    db_path = os.path.join(base_dir, db_name)

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(create_query)
        conn.commit()
        conn.close()
        return f"Table created successfully in: {db_path}"
    except Exception as e:
        return f"Error creating table: {e}"


# ============================
#   GEMINI SETUP
# ============================
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Generate SQL query with Gemini
def get_gemini_response(question, prompt):
    model = genai.GenerativeModel("gemini-2.5-flash")
    response = model.generate_content([prompt, question])
    return response.text.strip()


# ============================
#   RUN GENERAL SQL QUERIES
# ============================
def run_sql_query(sql, db_path):
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        conn.commit()
        conn.close()
        return rows
    except Exception as e:
        return [("Error executing query:", str(e))]


# ============================
#   PROMPT FOR GEMINI
# ============================
prompt = """You are an intelligent SQL query generator.
Your job is to convert natural language instructions into valid, safe, and syntactically correct SQL queries.
Return ONLY the SQL query (plain text, no explanation, no markdown).

--------------------------------------------------
GENERAL SQL RULES:
--------------------------------------------------
1. Understand the user request written in plain English.
2. Generate ONLY an SQL query — no text, no formatting, no notes.
3. The query must be compatible with SQLite syntax.
4. You are allowed to generate:
   - SELECT
   - INSERT INTO
   - UPDATE
   - DELETE FROM
   - CREATE TABLE (when asked)
5. NEVER generate:
   - DROP TABLE
   - DROP DATABASE
   - TRUNCATE
   - ALTER TABLE (unless explicitly asked)
6. Use single quotes (' ') for string values.
7. Always include a WHERE clause when modifying or deleting rows,
   unless user explicitly says “delete all” or “update all”.
8. When user asks to create a table:
   - Use SQLite-compatible data types (TEXT, INTEGER, REAL).
   - Assume appropriate types if user does not specify.
9. When column names are not given, infer reasonable ones.

--------------------------------------------------
OUTPUT FORMAT:
--------------------------------------------------
Return ONLY the SQL query.
No explanation.
No extra text.
No markdown.
No comments.

--------------------------------------------------
Now generate the SQL query ONLY for the user request below:

"""


# ============================
#   STREAMLIT UI
# ============================
st.set_page_config(page_title="AI SQL Query Generator")
st.title("🤖 GEMINI APP: AI-Powered SQL Assistant")

st.markdown("Ask anything, and I’ll generate & run the SQL query for you!")

user_input = st.text_input("Enter your question:", key="input")


# ============================
#   BUTTON ACTION
# ============================
if st.button("Generate and Run SQL Query"):
    if not user_input.strip():
        st.warning("⚠️ Please enter a valid question.")
    else:
        sql_query = get_gemini_response(user_input, prompt)

        st.subheader("🧠 Generated SQL Query:")
        st.code(sql_query, language="sql")

        # ============================
        #   CHECK IF QUERY IS CREATE
        # ============================
        if sql_query.lower().startswith("create table"):
            st.subheader("🛠 Creating Table...")

            result = create_table_in_base_dir(
                base_dir="database_folder",
                db_name="student.db",
                create_query=sql_query
            )

            st.success(result)

        else:
            # Run normal SQL queries (SELECT, INSERT, etc.)
            st.subheader("📊 Query Result:")
            result = run_sql_query(sql_query, "database_folder/student.db")

            if len(result) == 0:
                st.info("Query executed successfully, no records returned.")
            else:
                for row in result:
                    st.write(row)
