# import sqlite3
# import streamlit as st
# from langchain.chains import ConversationChain
# from langchain_google_genai import GoogleGenerativeAI
# from langchain.schema import SystemMessage, AIMessage, HumanMessage
# from prompts import system_prompt_assistant  # Your predefined system prompt

# # Set up Google Generative AI API key
# api_key = "AIzaSyAvGc65XG0kQM5uHrCbeCK3K2LO1nzJiaY"

# # Function to initialize the LLM with the system prompt
# def initialize_conversation_chain():
#     llm = GoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=api_key)
#     conversation = ConversationChain(llm=llm)
#     conversation.memory.chat_memory.add_message(SystemMessage(content=system_prompt_assistant))
#     return conversation

# # Initialize SQLite3 database
# conn = sqlite3.connect("chat_history.db")
# cursor = conn.cursor()

# # Create a table for storing messages
# cursor.execute("""
# CREATE TABLE IF NOT EXISTS chat_history (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     user_id TEXT NOT NULL,
#     sender TEXT NOT NULL,
#     message TEXT NOT NULL,
#     timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
# )
# """)
# conn.commit()

# # Function to save a message to the database
# def save_message_to_db(user_id, sender, message):
#     cursor.execute(
#         "INSERT INTO chat_history (user_id, sender, message) VALUES (?, ?, ?)",
#         (user_id, sender, message)
#     )
#     conn.commit()

# # Function to retrieve chat history for a user
# def get_chat_history(user_id):
#     cursor.execute(
#         "SELECT sender, message FROM chat_history WHERE user_id = ? ORDER BY id",
#         (user_id,)
#     )
#     return cursor.fetchall()

# # Function to check if a user exists in the database
# def user_exists(user_id):
#     cursor.execute("SELECT COUNT(*) FROM chat_history WHERE user_id = ?", (user_id,))
#     return cursor.fetchone()[0] > 0

# # Function to clear chat history for a user
# def clear_chat_history(user_id):
#     cursor.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
#     conn.commit()

# # Streamlit App
# st.set_page_config(page_title="LangChain Chatbot", layout="centered")

# # Custom CSS for aligning chat messages
# st.markdown("""
#     <style>
#     .chat-left {
#         text-align: left;
#         background-color: #f1f1f1;
#         border-radius: 10px;
#         padding: 10px;
#         margin: 5px 0;
#         max-width: 60%;
#     }
#     .chat-right {
#         text-align: right;
#         background-color: #007BFF;
#         color: white;
#         border-radius: 10px;
#         padding: 10px;
#         margin: 5px 0;
#         max-width: 60%;
#         margin-left: auto;
#     }
#     </style>
# """, unsafe_allow_html=True)

# # Sidebar for user authentication
# with st.sidebar:
#     st.title("User Panel")
#     user_id = st.text_input("Enter your User ID", placeholder="e.g., 12345")
#     name = st.text_input("Enter your Name", placeholder="e.g., John Doe")

#     if st.button("Authenticate"):
#         if user_id and name:
#             st.session_state["authenticated"] = True
#             st.session_state["user_id"] = user_id
#             st.session_state["name"] = name

#             if user_exists(user_id):
#                 st.success(f"Welcome back, {name}!")

#                 # Initialize conversation and load chat history
#                 conversation = initialize_conversation_chain()
#                 chat_history = get_chat_history(user_id)

#                 for sender, message in chat_history:
#                     if sender == "User":
#                         conversation.memory.chat_memory.add_message(HumanMessage(content=message))
#                     elif sender == "Assistant":
#                         conversation.memory.chat_memory.add_message(AIMessage(content=message))

#                 # Perform analysis and reflection based on chat history
#                 history_as_text = "\n".join(
#                     f"{sender}: {message}" for sender, message in chat_history
#                 )
#                 system_analysis_prompt = (
#                     f"{system_prompt_assistant}\nYou are the assistant trained to help users create SMART goals. "
#                     f"Here is the user's chat history:\n\n{history_as_text}\n\n"
#                     "Analyze their progress, summarize key points, and provide them a friendly reminder about their goals and tasks."
#                 )
#                 reflection = conversation.llm.predict(system_analysis_prompt)

#                 # Auto-send reflection to the user
#                 save_message_to_db(user_id, "Assistant", reflection)
#                 st.session_state["chat_history"] = [{"sender": "Assistant", "message": reflection}]
#                 st.session_state["conversation"] = conversation
#                 st.success("A reflection on your goals and tasks has been sent!")
#             else:
#                 st.success(f"Welcome, {name}! Let's start fresh.")
#                 # Initialize new conversation for the new user
#                 conversation = initialize_conversation_chain()
#                 st.session_state["conversation"] = conversation
#         else:
#             st.error("Please provide both User ID and Name.")

#     # Reset conversation button
#     if st.button("Reset Conversation"):
#         if "user_id" in st.session_state:
#             clear_chat_history(st.session_state["user_id"])
#             conversation = initialize_conversation_chain()
#             st.session_state["conversation"] = conversation
#             st.success("Conversation has been reset.")

# # Chat interface
# if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
#     st.warning("Please authenticate using the sidebar.")
# else:
#     st.title("🤖 SMART Goals with Goalie")
#     st.write("Your AI assistant for SMART goal-setting and refinement. Start chatting below!")

#     # Retrieve and display chat history for the session
#     if "conversation" in st.session_state:
#         conversation = st.session_state["conversation"]
#     else:
#         conversation = initialize_conversation_chain()
#         st.session_state["conversation"] = conversation

#     chat_history = get_chat_history(st.session_state["user_id"])

#     # Display chat history
#     for sender, message in chat_history:
#         if sender == "User":
#             st.markdown(f'<div class="chat-right">{message}</div>', unsafe_allow_html=True)
#         elif sender == "Assistant":
#             st.markdown(f'<div class="chat-left">{message}</div>', unsafe_allow_html=True)

#     # User input section
#     if prompt := st.chat_input("Type your message here..."):
#         # Save user input to the database
#         save_message_to_db(st.session_state["user_id"], "User", prompt)

#         # Display the user message
#         st.markdown(f'<div class="chat-right">{prompt}</div>', unsafe_allow_html=True)

#         # Generate assistant response
#         response = conversation.predict(input=prompt)
#         save_message_to_db(st.session_state["user_id"], "Assistant", response)

#         # Display the assistant message
#         st.markdown(f'<div class="chat-left">{response}</div>', unsafe_allow_html=True)


import sqlite3
import streamlit as st
from langchain.chains import ConversationChain
from langchain_google_genai import GoogleGenerativeAI
from langchain.schema import SystemMessage, AIMessage, HumanMessage
from prompts import system_prompt_assistant
import re

# Set up Google Generative AI API key
api_key = "AIzaSyAvGc65XG0kQM5uHrCbeCK3K2LO1nzJiaY"

# Function to initialize the LLM with the system prompt
def initialize_conversation_chain():
    llm = GoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=api_key)
    conversation = ConversationChain(llm=llm)
    conversation.memory.chat_memory.add_message(SystemMessage(content=system_prompt_assistant))
    return conversation

# Initialize SQLite3 database
conn = sqlite3.connect("goal_planner.db")
cursor = conn.cursor()

# Create tables for chat history and goals/tasks/reflections
cursor.execute("""
CREATE TABLE IF NOT EXISTS chat_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    sender TEXT NOT NULL,
    message TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS goal_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    type TEXT NOT NULL,  -- 'goal', 'task', or 'reflection'
    data TEXT NOT NULL,
    goal_id INTEGER, -- Foreign key for tasks and reflections
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (goal_id) REFERENCES goal_data (id)
)
""")

conn.commit()

# Functions for database operations
def save_message_to_db(user_id, sender, message):
    cursor.execute(
        "INSERT INTO chat_history (user_id, sender, message) VALUES (?, ?, ?)",
        (user_id, sender, message)
    )
    conn.commit()

def get_chat_history(user_id):
    cursor.execute(
        "SELECT sender, message FROM chat_history WHERE user_id = ? ORDER BY id",
        (user_id,)
    )
    return cursor.fetchall()

def user_exists(user_id):
    cursor.execute("SELECT COUNT(*) FROM chat_history WHERE user_id = ?", (user_id,))
    return cursor.fetchone()[0] > 0

def clear_chat_history(user_id):
    cursor.execute("DELETE FROM chat_history WHERE user_id = ?", (user_id,))
    conn.commit()

def save_goal_data(user_id, type, data, goal_id=None):
    cursor.execute("INSERT INTO goal_data (user_id, type, data, goal_id) VALUES (?, ?, ?, ?)", (user_id, type, data, goal_id))
    goal_data_id = cursor.lastrowid
    conn.commit()
    return goal_data_id

# def extract_goals_and_tasks(response, user_id):
#     goals = re.findall(r"\[Goal\](.*?)\[/Goal\]", response, re.DOTALL)
#     tasks = re.findall(r"\[Task\](.*?)\[/Task\]", response, re.DOTALL)

#     goal_ids = []
#     for goal in goals:
#         goal_id = save_goal_data(user_id, "goal", goal.strip())
#         goal_ids.append(goal_id)

#     for task in tasks:
#         if goal_ids:
#             save_goal_data(user_id, "task", task.strip(), goal_ids[-1])

def extract_goals_and_tasks(response, user_id):
    goals = re.findall(r"\[Goal\](.*?)\[/Goal\]", response, re.DOTALL)
    tasks = re.findall(r"\[Task\](.*?)\[/Task\]", response, re.DOTALL)

    goal_ids = []
    for goal in goals:
        goal_text = goal.strip()
        goal_id = save_goal_data(user_id, "goal", goal_text)
        goal_ids.append(goal_id)
        st.success(f"✅ Goal saved: {goal_text}")

    for task in tasks:
        task_text = task.strip()
        if goal_ids:
            save_goal_data(user_id, "task", task_text, goal_ids[-1])
            st.success(f"📌 Task saved under Goal ID {goal_ids[-1]}: {task_text}")

# Streamlit App
st.set_page_config(page_title="LangChain Chatbot", layout="centered")

st.markdown("""
    <style>
    .chat-left { text-align: left; background-color: #f1f1f1; border-radius: 10px; padding: 10px; margin: 5px 0; max-width: 60%; }
    .chat-right { text-align: right; background-color: #007BFF; color: white; border-radius: 10px; padding: 10px; margin: 5px 0; max-width: 60%; margin-left: auto; }
    </style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.title("User Panel")
    user_id = st.text_input("Enter your User ID", placeholder="e.g., 12345")
    name = st.text_input("Enter your Name", placeholder="e.g., John Doe")
    if st.button("Authenticate"):
        if user_id and name:
            st.session_state["authenticated"] = True
            st.session_state["user_id"] = user_id
            st.session_state["name"] = name
            if user_exists(user_id):
                st.success(f"Welcome back, {name}!")
                conversation = initialize_conversation_chain()
                chat_history = get_chat_history(user_id)
                for sender, message in chat_history:
                    if sender == "User":
                        conversation.memory.chat_memory.add_message(HumanMessage(content=message))
                    elif sender == "Assistant":
                        conversation.memory.chat_memory.add_message(AIMessage(content=message))
                history_as_text = "\n".join(f"{sender}: {message}" for sender, message in chat_history)
                system_analysis_prompt = f"{system_prompt_assistant}\nYou are the assistant trained to help users create SMART goals. Here is the user's chat history:\n\n{history_as_text}\n\nAnalyze their progress by asking, summarize key points, and provide them a friendly reminder about their goals and tasks."
                reflection = conversation.llm.predict(system_analysis_prompt)
                save_message_to_db(user_id, "Assistant", reflection)
                st.session_state["chat_history"] = [{"sender": "Assistant", "message": reflection}]
                st.session_state["conversation"] = conversation
                st.success("A reflection on your goals and tasks has been sent!")
                extract_goals_and_tasks(reflection,user_id)
                save_goal_data(user_id, "reflection", reflection)

            else:
                st.success(f"Welcome, {name}! Let's start fresh.")
                conversation = initialize_conversation_chain()
                st.session_state["conversation"] = conversation
        else:
            st.error("Please provide both User ID and Name.")
    if st.button("Reset Conversation"):
        if "user_id" in st.session_state:
            clear_chat_history(st.session_state["user_id"])
            conversation = initialize_conversation_chain()
            st.session_state["conversation"] = conversation
            st.success("Conversation has been reset.")
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    st.warning("Please authenticate using the sidebar.")
else:
    st.title("🤖 SMART Goals with Goalie")
    st.write("Your AI assistant for SMART goal-setting and refinement. Start chatting below!")
    if "conversation" in st.session_state:
        conversation = st.session_state["conversation"]
    else:
        conversation = initialize_conversation_chain()
        st.session_state["conversation"] = conversation
    chat_history = get_chat_history(st.session_state["user_id"])
    for sender, message in chat_history:
        if sender == "User":
            st.markdown(f'<div class="chat-right">{message}</div>', unsafe_allow_html=True)
        elif sender == "Assistant":
            st.markdown(f'<div class="chat-left">{message}</div>', unsafe_allow_html=True)
    if prompt := st.chat_input("Type your message here..."):
        save_message_to_db(st.session_state["user_id"], "User", prompt)
        st.markdown(f'<div class="chat-right">{prompt}</div>', unsafe_allow_html=True)
        response = conversation.predict(input=prompt)
        save_message_to_db(st.session_state["user_id"], "Assistant", response)
        st.markdown(f'<div class="chat-left">{response}</div>', unsafe_allow_html=True)
        extract_goals_and_tasks(response,st.session_state["user_id"])