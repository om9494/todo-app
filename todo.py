import streamlit as st 
import mysql.connector
import pandas as pd
import os

def connect_db():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password=os.getenv("MYSQL_PASSWORD", "Om@123"),
        database="todolistbase",
        auth_plugin="mysql_native_password"
    ) 

def setup_database():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Tasks (
            Task_ID INT AUTO_INCREMENT PRIMARY KEY,
            Task VARCHAR(255) NOT NULL,
            Deadline DATE NOT NULL
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

def execute_query(query, values=None, fetch=False):
    conn = connect_db()
    cursor = conn.cursor(dictionary=True)
    
    try:
        if values:
            cursor.execute(query, values)
        else:
            cursor.execute(query)
        
        if fetch:
            result = cursor.fetchall()
        else:
            conn.commit()
            result = None
    except mysql.connector.Error as err:
        st.error(f"Database error: {err}")
        result = None
    finally:
        cursor.close()
        conn.close()
    
    return result

setup_database()

st.title("📝 To-Do List App")
menu = st.sidebar.selectbox("MENU", ["Add Task", "View Tasks", "Update Task", "Delete Task"])

if menu == "Add Task":
    st.subheader("Add a New Task")
    task = st.text_input("Enter Task", max_chars=255)
    deadline = st.date_input("Enter Deadline")
    submit = st.button("Add Task")

    if submit and task.strip():
        execute_query("INSERT INTO Tasks (Task, Deadline) VALUES (%s, %s)", (task, deadline))
        st.success("Task Added Successfully!")
    elif submit:
        st.warning("Task cannot be empty!")

elif menu == "View Tasks":
    st.subheader("View All Tasks")
    tasks = execute_query("SELECT * FROM Tasks", fetch=True)
    if tasks:
        st.write(pd.DataFrame(tasks))
    else:
        st.info("No tasks found!")

elif menu == "Update Task":
    st.subheader("Update Task")
    tasks = execute_query("SELECT * FROM Tasks", fetch=True)
    
    if tasks:
        st.write(pd.DataFrame(tasks))
        task_id = st.number_input("Enter Task ID", min_value=1, step=1)
        new_task = st.text_input("Enter New Task")
        new_deadline = st.date_input("Enter New Deadline")
        update = st.button("Update Task")
        
        if update and new_task.strip():
            execute_query("UPDATE Tasks SET Task = %s, Deadline = %s WHERE Task_ID = %s", (new_task, new_deadline, task_id))
            st.success("Task Updated Successfully!")
        elif update:
            st.warning("Task description cannot be empty!")
    else:
        st.info("No tasks available to update!")

elif menu == "Delete Task":
    st.subheader("Delete Task")
    tasks = execute_query("SELECT * FROM Tasks", fetch=True)
    
    if tasks:
        st.write(pd.DataFrame(tasks))
        task_id = st.number_input("Enter Task ID to Delete", min_value=1, step=1)
        delete = st.button("Delete Task")
        delete_all = st.button("Delete All Tasks")

        if delete:
            execute_query("DELETE FROM Tasks WHERE Task_ID = %s", (task_id,))
            st.success(f"Task ID {task_id} Deleted Successfully!")
        
        if delete_all and st.checkbox("Are you sure you want to delete all tasks?"):
            execute_query("DELETE FROM Tasks")
            st.success("All Tasks Deleted Successfully!")
    else:
        st.info("No tasks available to delete!")
