import os
from flask import Flask, render_template, url_for, request
import mysql.connector

app = Flask(__name__)

# todoList = [
#  {'id' : 1, 'description' : 'SS1 Assignment 1', 'status' : 'Done'},
#  {'id' : 2, 'description' : 'SS1 Assignment 2', 'status' : 'Doing'},
#  {'id' : 3, 'description' : 'SS1 Final', 'status' : 'Doing'}
# ]

db_connect = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'YOUR_PASSWORD'
}

def get_db_connect():
    return mysql.connector.connect(**db_connect)

def init_db():
    connecting = get_db_connect()
    cursor = connecting.cursor(dictionary=True)
    cursor.execute("CREATE DATABASE IF NOT EXISTS todoDB")
    cursor.execute("USE todoDB")
    create_table_query = """
        CREATE TABLE IF NOT EXISTS todo (
            id INT AUTO_INCREMENT PRIMARY KEY,
            description VARCHAR(240) NOT NULL,
            status VARCHAR(10) DEFAULT 'Doing'
        )
    """
    cursor.execute(create_table_query)
    connecting.commit()
    cursor.close()
    connecting.close()

init_db()

db_connect['database'] = 'todoDB'

def locate_id(todolist, id):
    arr_id = -1
    for item in todolist:
        arr_id += 1
        matched_id = list(item.values())[0]
        if matched_id == id:
            return arr_id
        else:
            continue

@app.route("/")
def main_page():
    connection = get_db_connect()
    cursor = connection.cursor(dictionary=True)
    cursor.execute('SELECT * FROM todo')
    todoList = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('index.html', todoList=todoList)

@app.route("/", methods=['GET', 'POST'])
def modify_todo():
    req = request.form
    # print(req)
    connection = get_db_connect()
    cursor = connection.cursor(dictionary=True)
    
    try:
        if req.get('newTodo') != None :
            # if len(todoList) > 0:
            #     previous_todo_id = list(todoList[-1].values())[0]
            # else:
            #     previous_todo_id = 0

            # this_todo_id = previous_todo_id + 1
            this_todo_des = req.get('newTodo')

            # new_todo_row = {
            #     'id': this_todo_id,
            #     'description': this_todo_des,
            #     'status': 'Doing',
            # }
            # todoList.append(new_todo_row)
            cursor.execute("INSERT INTO todo (description, status) VALUES (%s, 'Doing')", (this_todo_des,))

        elif req.get('deleteBtn') == 'delete':
            todo_id = req.get('todo_id')
            cursor.execute("DELETE FROM todo WHERE id = %s", (todo_id,))
            
        elif req.get('updateBtn') == 'update':
            todo_id = req.get('todo_id')
            todo_description = req.get('todo_des')
            cursor.execute('UPDATE todo SET description = %s WHERE id = %s', (todo_description, todo_id))

        elif req.get('checkBox') is not None: 
            todo_id = req.get('todo_id')
            if todo_id is not None:
                new_status = req.get('status')
                cursor.execute("UPDATE todo SET status = %s WHERE id = %s", (new_status, todo_id))

        elif req.get('checkBox') is None:
            todo_id = req.get('todo_id') 
            new_status = 'Doing'
            cursor.execute("UPDATE todo SET status = %s WHERE id = %s", (new_status, todo_id))
        
        connection.commit()

    except mysql.connector.Error as err:
        print(err)
        connection.rollback()
    finally:
        cursor.close()
        connection.close()

    return main_page()

if __name__ == '__main__':
    app.run(debug=True)