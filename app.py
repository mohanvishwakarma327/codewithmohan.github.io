from flask import Flask, render_template, request, redirect, session
import json
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'

PROJECTS_FILE = 'projects.json'
USERS_FILE = 'users.json'
MESSAGES_FILE = 'messages.json'

# --- Helpers ---
def load_projects():
    if os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE) as f:
            return json.load(f)
    return []

def save_projects(projects):
    with open(PROJECTS_FILE, 'w') as f:
        json.dump(projects, f, indent=2)

def load_messages():
    if os.path.exists(MESSAGES_FILE):
        with open(MESSAGES_FILE) as f:
            return json.load(f)
    return []

def save_messages(messages):
    with open(MESSAGES_FILE, 'w') as f:
        json.dump(messages, f, indent=2)

# --- Public Pages ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/projects')
def projects():
    return render_template('project.html', projects=load_projects())

@app.route('/contact', methods=['POST'])
def contact():
    if request.form.get('honeypot'):
        return "Spam detected!", 400

    name = request.form.get('name')
    email = request.form.get('email')
    message = request.form.get('message')

    messages = load_messages()
    new_id = max([m['id'] for m in messages], default=0) + 1
    messages.append({"id": new_id, "name": name, "email": email, "message": message})
    save_messages(messages)

    return render_template("thank_you.html", name=name)

# --- Auth ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        with open(USERS_FILE) as f:
            users = json.load(f)
        if users.get(request.form['username']) == request.form['password']:
            session['admin'] = True
            return redirect('/admin')
        return "Invalid credentials"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# --- Admin Panel ---
@app.route('/admin')
def admin():
    if not session.get('admin'):
        return redirect('/login')
    return render_template('admin.html',
                           projects=load_projects(),
                           messages=load_messages())

@app.route('/add', methods=['POST'])
def add():
    if not session.get('admin'):
        return redirect('/login')
    projects = load_projects()
    new_id = max([p['id'] for p in projects], default=0) + 1
    project = {
        "id": new_id,
        "title": request.form['title'],
        "description": request.form['description'],
        "tags": [tag.strip() for tag in request.form['tags'].split(',')],
        "github": request.form.get('github', ''),
        "demo": request.form.get('demo', '')
    }
    projects.append(project)
    save_projects(projects)
    return redirect('/admin')

@app.route('/delete/<int:project_id>', methods=['POST'])
def delete(project_id):
    if not session.get('admin'):
        return redirect('/login')
    projects = [p for p in load_projects() if p['id'] != project_id]
    save_projects(projects)
    return redirect('/admin')

@app.route('/delete_message/<int:msg_id>', methods=['POST'])
def delete_message(msg_id):
    if not session.get('admin'):
        return redirect('/login')
    messages = [m for m in load_messages() if m['id'] != msg_id]
    save_messages(messages)
    return redirect('/admin')

# --- Run ---
if __name__ == '__main__':
    app.run(debug=True)
