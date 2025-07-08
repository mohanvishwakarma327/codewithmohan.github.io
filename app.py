from flask import Flask, render_template, request, redirect, session
import json, os

app = Flask(__name__)
app.secret_key = 'super-secret-key'  # Replace with a strong key in production

PROJECTS_FILE = 'projects.json'
USERS_FILE = 'users.json'


# ---------- Helpers ----------
def load_projects():
    if not os.path.exists(PROJECTS_FILE):
        return []
    with open(PROJECTS_FILE) as f:
        return json.load(f)

def save_projects(projects):
    with open(PROJECTS_FILE, 'w') as f:
        json.dump(projects, f, indent=2)


# ---------- Routes ----------
@app.route('/')
def home():
    return redirect('/projects')

@app.route('/projects')
def show_projects():
    projects = load_projects()
    return render_template('projects.html', projects=projects)

@app.route('/portfolio')
def portfolio():
    projects = load_projects()
    return render_template('project.html', projects=projects)



# ---------- Admin Login ----------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        with open(USERS_FILE) as f:
            users = json.load(f)
        username = request.form['username']
        password = request.form['password']
        if users.get(username) == password:
            session['logged_in'] = True
            return redirect('/admin')
        return "❌ Invalid credentials"
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')


# ---------- Admin Panel ----------
@app.route('/admin')
def admin():
    if not session.get('logged_in'):
        return redirect('/login')
    projects = load_projects()
    return render_template('admin.html', projects=projects)

@app.route('/add', methods=['POST'])
def add_project():
    if not session.get('logged_in'):
        return redirect('/login')
    projects = load_projects()
    new_id = max([p['id'] for p in projects], default=0) + 1
    project = {
        "id": new_id,
        "title": request.form['title'],
        "description": request.form['description'],
        "tags": [tag.strip() for tag in request.form['tags'].split(',') if tag.strip()]
    }
    projects.append(project)
    save_projects(projects)
    return redirect('/admin')

@app.route('/delete/<int:project_id>', methods=['POST'])
def delete_project(project_id):
    if not session.get('logged_in'):
        return redirect('/login')
    projects = load_projects()
    projects = [p for p in projects if p['id'] != project_id]
    save_projects(projects)
    return redirect('/admin')


# ---------- Run App ----------
if __name__ == '__main__':
    app.run(debug=True)
