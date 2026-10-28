from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from .models import db, User, Project, Task
from . import login_manager

main = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ==================== AUTH ====================

@main.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('landing.html')


@main.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        full_name = request.form.get('full_name', '').strip()
        
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'danger')
            return render_template('register.html')
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('register.html')
        
        # Generate random avatar color
        colors = ['#6366f1', '#8b5cf6', '#ec4899', '#f43f5e', '#f97316', '#eab308', '#22c55e', '#14b8a6', '#06b6d4', '#3b82f6']
        import random
        color = random.choice(colors)
        
        user = User(username=username, email=email, full_name=full_name or username, avatar_color=color)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('register.html')


@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = request.form.get('remember') == 'on'
        
        user = User.query.filter((User.username == username) | (User.email == username)).first()
        
        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.full_name or user.username}!', 'success')
            return redirect(next_page or url_for('main.dashboard'))
        
        flash('Invalid username/email or password.', 'danger')
    
    return render_template('login.html')


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))


# ==================== DASHBOARD ====================

@main.route('/dashboard')
@login_required
def dashboard():
    projects = Project.query.filter_by(user_id=current_user.id).order_by(Project.updated_at.desc()).all()
    recent_tasks = Task.query.join(Project).filter(Project.user_id == current_user.id)\
        .order_by(Task.updated_at.desc()).limit(8).all()
    
    # Stats
    total_projects = len(projects)
    total_tasks = Task.query.join(Project).filter(Project.user_id == current_user.id).count()
    completed_tasks = Task.query.join(Project).filter(
        Project.user_id == current_user.id, Task.status == 'completed'
    ).count()
    pending_tasks = total_tasks - completed_tasks
    
    # Priority breakdown
    high_priority = Task.query.join(Project).filter(
        Project.user_id == current_user.id, Task.priority.in_(['high', 'critical']), Task.status != 'completed'
    ).count()
    
    # Tasks by status for chart
    todo_count = Task.query.join(Project).filter(Project.user_id == current_user.id, Task.status == 'todo').count()
    in_progress_count = Task.query.join(Project).filter(Project.user_id == current_user.id, Task.status == 'in_progress').count()
    
    # Upcoming due tasks
    upcoming = Task.query.join(Project).filter(
        Project.user_id == current_user.id,
        Task.status != 'completed',
        Task.due_date != None,
        Task.due_date <= datetime.utcnow() + timedelta(days=7)
    ).order_by(Task.due_date).limit(5).all()
    
    return render_template('dashboard.html',
                           projects=projects,
                           recent_tasks=recent_tasks,
                           total_projects=total_projects,
                           total_tasks=total_tasks,
                           completed_tasks=completed_tasks,
                           pending_tasks=pending_tasks,
                           high_priority=high_priority,
                           todo_count=todo_count,
                           in_progress_count=in_progress_count,
                           upcoming=upcoming)


# ==================== PROJECTS ====================

@main.route('/projects')
@login_required
def projects():
    status_filter = request.args.get('status', 'all')
    query = Project.query.filter_by(user_id=current_user.id)
    
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    projects_list = query.order_by(Project.updated_at.desc()).all()
    return render_template('projects.html', projects=projects_list, status_filter=status_filter)


@main.route('/projects/create', methods=['GET', 'POST'])
@login_required
def create_project():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        color = request.form.get('color', '#6366f1')
        
        if not name:
            flash('Project name is required.', 'danger')
            return render_template('project_form.html')
        
        project = Project(name=name, description=description, color=color, user_id=current_user.id)
        db.session.add(project)
        db.session.commit()
        
        flash(f'Project "{name}" created successfully!', 'success')
        return redirect(url_for('main.project_detail', project_id=project.id))
    
    return render_template('project_form.html')


@main.route('/projects/<int:project_id>')
@login_required
def project_detail(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.projects'))
    
    status_filter = request.args.get('status', 'all')
    tasks_query = project.tasks
    
    if status_filter != 'all':
        tasks_query = tasks_query.filter_by(status=status_filter)
    
    tasks = tasks_query.order_by(
        db.case(
            (Task.priority == 'critical', 1),
            (Task.priority == 'high', 2),
            (Task.priority == 'medium', 3),
            else_=4
        ),
        Task.due_date.asc().nullslast()
    ).all()
    
    return render_template('project_detail.html', project=project, tasks=tasks, status_filter=status_filter)


@main.route('/projects/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.projects'))
    
    if request.method == 'POST':
        project.name = request.form.get('name', '').strip()
        project.description = request.form.get('description', '').strip()
        project.color = request.form.get('color', '#6366f1')
        project.status = request.form.get('status', 'active')
        project.updated_at = datetime.utcnow()
        
        db.session.commit()
        flash('Project updated successfully!', 'success')
        return redirect(url_for('main.project_detail', project_id=project.id))
    
    return render_template('project_form.html', project=project)


@main.route('/projects/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.projects'))
    
    name = project.name
    db.session.delete(project)
    db.session.commit()
    flash(f'Project "{name}" deleted.', 'info')
    return redirect(url_for('main.projects'))


# ==================== TASKS ====================

@main.route('/tasks/create/<int:project_id>', methods=['GET', 'POST'])
@login_required
def create_task(project_id):
    project = Project.query.get_or_404(project_id)
    if project.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.projects'))
    
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        priority = request.form.get('priority', 'medium')
        status = request.form.get('status', 'todo')
        due_date_str = request.form.get('due_date', '')
        
        if not title:
            flash('Task title is required.', 'danger')
            return render_template('task_form.html', project=project)
        
        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                pass
        
        task = Task(
            title=title,
            description=description,
            priority=priority,
            status=status,
            due_date=due_date,
            project_id=project.id,
            assignee_id=current_user.id
        )
        db.session.add(task)
        project.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash('Task created successfully!', 'success')
        return redirect(url_for('main.project_detail', project_id=project.id))
    
    return render_template('task_form.html', project=project)


@main.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    project = task.project
    if project.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.projects'))
    
    if request.method == 'POST':
        task.title = request.form.get('title', '').strip()
        task.description = request.form.get('description', '').strip()
        task.priority = request.form.get('priority', 'medium')
        old_status = task.status
        task.status = request.form.get('status', 'todo')
        
        due_date_str = request.form.get('due_date', '')
        if due_date_str:
            try:
                task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                pass
        else:
            task.due_date = None
        
        if task.status == 'completed' and old_status != 'completed':
            task.completed_at = datetime.utcnow()
        elif task.status != 'completed':
            task.completed_at = None
        
        task.updated_at = datetime.utcnow()
        project.updated_at = datetime.utcnow()
        db.session.commit()
        
        flash('Task updated successfully!', 'success')
        return redirect(url_for('main.project_detail', project_id=project.id))
    
    return render_template('task_form.html', project=project, task=task)


@main.route('/tasks/<int:task_id>/toggle', methods=['POST'])
@login_required
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.project.user_id != current_user.id:
        return jsonify({'error': 'Access denied'}), 403
    
    if task.status == 'completed':
        task.status = 'todo'
        task.completed_at = None
    else:
        task.status = 'completed'
        task.completed_at = datetime.utcnow()
    
    task.updated_at = datetime.utcnow()
    task.project.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'status': task.status,
        'progress': task.project.progress
    })


@main.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    project = task.project
    if project.user_id != current_user.id:
        flash('Access denied.', 'danger')
        return redirect(url_for('main.projects'))
    
    db.session.delete(task)
    project.updated_at = datetime.utcnow()
    db.session.commit()
    flash('Task deleted.', 'info')
    return redirect(url_for('main.project_detail', project_id=project.id))


# ==================== API (for dynamic JS) ====================

@main.route('/api/stats')
@login_required
def api_stats():
    total_tasks = Task.query.join(Project).filter(Project.user_id == current_user.id).count()
    completed = Task.query.join(Project).filter(Project.user_id == current_user.id, Task.status == 'completed').count()
    todo = Task.query.join(Project).filter(Project.user_id == current_user.id, Task.status == 'todo').count()
    in_progress = Task.query.join(Project).filter(Project.user_id == current_user.id, Task.status == 'in_progress').count()
    
    return jsonify({
        'total': total_tasks,
        'completed': completed,
        'todo': todo,
        'in_progress': in_progress
    })
