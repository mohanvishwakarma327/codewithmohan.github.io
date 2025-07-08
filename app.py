from flask import Flask, render_template, request, redirect, session
import json
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Replace with a secure value in production

PROJECTS_FILE = 'projects.json'
USERS_FILE = 'users.json'


# --- Helpers ---
def load_projects():
    if os.path.exists(PROJECTS_FILE):
        with open(PROJECTS_FILE) as f:
            return json.load(f)
    return []

def save_projects(projects):
    with open(PROJECTS_FILE, 'w') as f:
        json.dump(projects, f, indent=2)


# --- Public Pages ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/projects')
def projects():
    return render_template('project.html', projects=load_projects())


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
    return render_template('admin.html', projects=load_projects())

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


# --- Local Run Support (ignored by gunicorn) ---
if __name__ == '__main__':
    app.run(debug=True)
