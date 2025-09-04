from flask import Flask, request, jsonify, render_template_string, session
import sqlite3
import hashlib
import os
from datetime import timedelta

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-key-change-in-production')
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Portfolio - Professional Network</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: #f3f2ef; min-height: 100vh; color: #000000e6; }
        .navbar { background: #fff; border-bottom: 1px solid #e0e0e0; position: sticky; top: 0; z-index: 100; box-shadow: 0 0 0 1px rgba(0,0,0,.08), 0 2px 4px rgba(0,0,0,.08); }
        .navbar-content { max-width: 1128px; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; padding: 0 24px; height: 52px; }
        .logo { font-size: 24px; font-weight: 700; color: #0a66c2; text-decoration: none; }
        .nav-menu { display: flex; gap: 0; }
        .nav-item { padding: 12px 16px; color: #666; background: none; border: none; cursor: pointer; font-size: 14px; font-weight: 400; transition: color 0.2s; border-radius: 4px; }
        .nav-item:hover { color: #000; background: #f3f2ef; }
        .nav-item.active { color: #0a66c2; font-weight: 600; border-bottom: 2px solid #0a66c2; }
        .container { max-width: 1128px; margin: 24px auto; padding: 0 24px; }
        .card { background: #fff; border-radius: 8px; border: 1px solid #e0e0e0; box-shadow: 0 0 0 1px rgba(0,0,0,.08); overflow: hidden; margin-bottom: 16px; }
        .card-header { padding: 24px 24px 0; border-bottom: 1px solid #e0e0e0; margin-bottom: 24px; display: flex; justify-content: space-between; align-items: center; }
        .card-title { font-size: 20px; font-weight: 600; color: #000; }
        .card-body { padding: 0 24px 24px; }
        .section { display: none; }
        .section.active { display: block; }
        .form-group { margin-bottom: 24px; }
        .form-label { display: block; font-size: 14px; font-weight: 600; color: #000; margin-bottom: 8px; }
        .form-input { width: 100%; padding: 12px 16px; border: 1px solid #ccc; border-radius: 4px; font-size: 16px; background: #fff; transition: border-color 0.2s; }
        .form-input:focus { outline: none; border-color: #0a66c2; box-shadow: 0 0 0 2px rgba(10, 102, 194, 0.2); }
        .btn { padding: 12px 24px; border-radius: 24px; font-size: 16px; font-weight: 600; cursor: pointer; transition: all 0.2s; border: none; }
        .btn-primary { background: #0a66c2; color: #fff; }
        .btn-primary:hover { background: #004182; }
        .btn-secondary { background: #fff; color: #0a66c2; border: 1px solid #0a66c2; }
        .btn-secondary:hover { background: #f3f2ef; }
        .btn-small { padding: 6px 12px; font-size: 14px; }
        .btn-danger { background: #d32f2f; color: #fff; }
        .btn-danger:hover { background: #b71c1c; }
        .item-card { background: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 8px; padding: 20px; margin-bottom: 16px; }
        .item-header { display: flex; justify-content: between; align-items: flex-start; margin-bottom: 12px; }
        .item-title { font-size: 18px; font-weight: 600; color: #000; }
        .item-subtitle { color: #666; font-size: 14px; margin-bottom: 8px; }
        .item-date { color: #666; font-size: 12px; }
        .item-description { color: #333; line-height: 1.5; margin-top: 12px; }
        .tech-tags { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px; }
        .tech-tag { background: #e3f2fd; color: #1976d2; padding: 4px 12px; border-radius: 16px; font-size: 12px; }
        .profile-card { background: #fff; border-radius: 8px; border: 1px solid #e0e0e0; overflow: hidden; }
        .profile-header { height: 120px; background: linear-gradient(135deg, #0a66c2 0%, #004182 100%); position: relative; }
        .profile-avatar { width: 120px; height: 120px; border-radius: 50%; background: #fff; border: 4px solid #fff; position: absolute; bottom: -60px; left: 24px; display: flex; align-items: center; justify-content: center; font-size: 48px; font-weight: 700; color: #0a66c2; }
        .profile-info { padding: 80px 24px 24px; }
        .profile-name { font-size: 24px; font-weight: 700; color: #000; margin-bottom: 4px; }
        .profile-title { font-size: 16px; color: #666; margin-bottom: 16px; }
        .skills-list { display: flex; flex-wrap: wrap; gap: 8px; margin: 16px 0; }
        .skill-tag { background: #f3f2ef; color: #0a66c2; padding: 6px 12px; border-radius: 16px; font-size: 14px; font-weight: 500; border: 1px solid #e0e0e0; }
        .contact-links { display: flex; gap: 16px; margin-top: 16px; }
        .contact-link { color: #0a66c2; text-decoration: none; font-size: 14px; font-weight: 500; padding: 8px 16px; border: 1px solid #0a66c2; border-radius: 24px; transition: all 0.2s; }
        .contact-link:hover { background: #0a66c2; color: #fff; }
        .welcome-section { text-align: center; padding: 80px 24px; }
        .welcome-title { font-size: 32px; font-weight: 700; color: #000; margin-bottom: 16px; }
        .welcome-subtitle { font-size: 18px; color: #666; line-height: 1.5; }
        .auth-tabs { display: flex; margin-bottom: 24px; border-bottom: 1px solid #e0e0e0; }
        .auth-tab { padding: 12px 24px; background: none; border: none; cursor: pointer; font-size: 16px; font-weight: 500; color: #666; border-bottom: 2px solid transparent; }
        .auth-tab.active { color: #0a66c2; border-bottom-color: #0a66c2; }
        .form-row { display: flex; gap: 16px; }
        .form-row .form-group { flex: 1; }
        @media (max-width: 768px) { .navbar-content { padding: 0 16px; } .container { padding: 0 16px; } .form-row { flex-direction: column; } }
    </style>
</head>
<body>
    <nav class="navbar">
        <div class="navbar-content">
            <a href="#" class="logo">Portfolio</a>
            <div class="nav-menu">
                <button onclick="showSection('home')" class="nav-item active" id="homeBtn">Home</button>
                <button onclick="showSection('auth')" class="nav-item" id="authBtn">Sign In</button>
                <button onclick="showSection('profile')" class="nav-item" id="profileBtn" style="display:none">Profile</button>
                <button onclick="showSection('projects')" class="nav-item" id="projectsBtn" style="display:none">Projects</button>
                <button onclick="showSection('experience')" class="nav-item" id="experienceBtn" style="display:none">Experience</button>
                <button onclick="showSection('education')" class="nav-item" id="educationBtn" style="display:none">Education</button>
                <button onclick="logout()" class="nav-item" id="logoutBtn" style="display:none">Sign Out</button>
            </div>
        </div>
    </nav>

    <div class="container">
        <div id="home" class="section active">
            <div class="card">
                <div class="welcome-section">
                    <h1 class="welcome-title">Welcome to Portfolio</h1>
                    <p class="welcome-subtitle">Build your professional presence. Showcase projects, experience, and education.</p>
                </div>
            </div>
        </div>

        <div id="auth" class="section">
            <div class="card" style="max-width: 400px; margin: 0 auto;">
                <div class="card-body">
                    <div class="auth-tabs">
                        <button onclick="toggleAuth('login')" id="loginTab" class="auth-tab active">Sign In</button>
                        <button onclick="toggleAuth('register')" id="registerTab" class="auth-tab">Join Now</button>
                    </div>
                    <form id="authForm">
                        <div class="form-group">
                            <label class="form-label">Username</label>
                            <input type="text" id="username" class="form-input" required>
                        </div>
                        <div class="form-group">
                            <label class="form-label">Password</label>
                            <input type="password" id="password" class="form-input" required>
                        </div>
                        <button type="submit" class="btn btn-primary" id="authSubmit" style="width:100%">Sign In</button>
                    </form>
                </div>
            </div>
        </div>

        <div id="profile" class="section">
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Profile</h2>
                    <button onclick="showEditProfile()" class="btn btn-primary">Edit Profile</button>
                </div>
                <div class="card-body">
                    <div id="profileDisplay"></div>
                    <div id="editProfileForm" style="display:none;">
                        <form id="profileForm">
                            <div class="form-group">
                                <label class="form-label">Full Name *</label>
                                <input type="text" id="name" class="form-input" required>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Professional Title</label>
                                <input type="text" id="title" class="form-input">
                            </div>
                            <div class="form-group">
                                <label class="form-label">About</label>
                                <textarea id="about" class="form-input" rows="4"></textarea>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Skills (comma-separated)</label>
                                <input type="text" id="skills" class="form-input">
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label class="form-label">Email</label>
                                    <input type="email" id="email" class="form-input">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">Phone</label>
                                    <input type="tel" id="phone" class="form-input">
                                </div>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label class="form-label">Location</label>
                                    <input type="text" id="location" class="form-input">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">Website</label>
                                    <input type="url" id="website" class="form-input">
                                </div>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label class="form-label">GitHub</label>
                                    <input type="url" id="github" class="form-input">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">LinkedIn</label>
                                    <input type="url" id="linkedin" class="form-input">
                                </div>
                            </div>
                            <div style="display:flex;gap:10px;">
                                <button type="submit" class="btn btn-primary">Save Changes</button>
                                <button type="button" onclick="hideEditProfile()" class="btn btn-secondary">Cancel</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>

        <div id="projects" class="section">
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Projects</h2>
                    <button onclick="showAddProject()" class="btn btn-primary">Add Project</button>
                </div>
                <div class="card-body">
                    <div id="projectsList"></div>
                    <div id="addProjectForm" style="display:none;">
                        <form id="projectForm">
                            <div class="form-group">
                                <label class="form-label">Project Title *</label>
                                <input type="text" id="projectTitle" class="form-input" required>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Description</label>
                                <textarea id="projectDescription" class="form-input" rows="3"></textarea>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Technologies</label>
                                <input type="text" id="projectTech" class="form-input" placeholder="React, Node.js, MongoDB">
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label class="form-label">Live URL</label>
                                    <input type="url" id="projectUrl" class="form-input">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">GitHub URL</label>
                                    <input type="url" id="projectGithub" class="form-input">
                                </div>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label class="form-label">Start Date</label>
                                    <input type="month" id="projectStart" class="form-input">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">End Date</label>
                                    <input type="month" id="projectEnd" class="form-input">
                                </div>
                            </div>
                            <div style="display:flex;gap:10px;">
                                <button type="submit" class="btn btn-primary">Save Project</button>
                                <button type="button" onclick="hideAddProject()" class="btn btn-secondary">Cancel</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>

        <div id="experience" class="section">
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Work Experience</h2>
                    <button onclick="showAddExperience()" class="btn btn-primary">Add Experience</button>
                </div>
                <div class="card-body">
                    <div id="experienceList"></div>
                    <div id="addExperienceForm" style="display:none;">
                        <form id="experienceForm">
                            <div class="form-row">
                                <div class="form-group">
                                    <label class="form-label">Company *</label>
                                    <input type="text" id="expCompany" class="form-input" required>
                                </div>
                                <div class="form-group">
                                    <label class="form-label">Position *</label>
                                    <input type="text" id="expPosition" class="form-input" required>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Description</label>
                                <textarea id="expDescription" class="form-input" rows="3"></textarea>
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label class="form-label">Start Date</label>
                                    <input type="month" id="expStart" class="form-input">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">End Date</label>
                                    <input type="month" id="expEnd" class="form-input">
                                </div>
                            </div>
                            <div class="form-group">
                                <label><input type="checkbox" id="expCurrent"> Currently working here</label>
                            </div>
                            <div style="display:flex;gap:10px;">
                                <button type="submit" class="btn btn-primary">Save Experience</button>
                                <button type="button" onclick="hideAddExperience()" class="btn btn-secondary">Cancel</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>

        <div id="education" class="section">
            <div class="card">
                <div class="card-header">
                    <h2 class="card-title">Education</h2>
                    <button onclick="showAddEducation()" class="btn btn-primary">Add Education</button>
                </div>
                <div class="card-body">
                    <div id="educationList"></div>
                    <div id="addEducationForm" style="display:none;">
                        <form id="educationForm">
                            <div class="form-row">
                                <div class="form-group">
                                    <label class="form-label">Institution *</label>
                                    <input type="text" id="eduInstitution" class="form-input" required>
                                </div>
                                <div class="form-group">
                                    <label class="form-label">Degree *</label>
                                    <input type="text" id="eduDegree" class="form-input" required>
                                </div>
                            </div>
                            <div class="form-group">
                                <label class="form-label">Field of Study</label>
                                <input type="text" id="eduField" class="form-input">
                            </div>
                            <div class="form-row">
                                <div class="form-group">
                                    <label class="form-label">Start Date</label>
                                    <input type="month" id="eduStart" class="form-input">
                                </div>
                                <div class="form-group">
                                    <label class="form-label">End Date</label>
                                    <input type="month" id="eduEnd" class="form-input">
                                </div>
                            </div>
                            <div class="form-group">
                                <label><input type="checkbox" id="eduCurrent"> Currently studying here</label>
                            </div>
                            <div style="display:flex;gap:10px;">
                                <button type="submit" class="btn btn-primary">Save Education</button>
                                <button type="button" onclick="hideAddEducation()" class="btn btn-secondary">Cancel</button>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let authMode = 'login';
        
        function showSection(sectionId) {
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
            document.getElementById(sectionId).classList.add('active');
            if (document.getElementById(sectionId + 'Btn')) {
                document.getElementById(sectionId + 'Btn').classList.add('active');
            }
            
            if (sectionId === 'profile') loadProfile();
            if (sectionId === 'projects') loadProjects();
            if (sectionId === 'experience') loadExperience();
            if (sectionId === 'education') loadEducation();
        }
        
        function toggleAuth(mode) {
            authMode = mode;
            document.getElementById('loginTab').classList.toggle('active', mode === 'login');
            document.getElementById('registerTab').classList.toggle('active', mode === 'register');
            document.getElementById('authSubmit').textContent = mode === 'login' ? 'Sign In' : 'Join Now';
        }
        
        function updateUI(loggedIn) {
            const navItems = ['authBtn', 'profileBtn', 'projectsBtn', 'experienceBtn', 'educationBtn', 'logoutBtn'];
            navItems.forEach(id => {
                const element = document.getElementById(id);
                if (id === 'authBtn') {
                    element.style.display = loggedIn ? 'none' : 'block';
                } else {
                    element.style.display = loggedIn ? 'block' : 'none';
                }
            });
        }
        
        function showNotification(message, type = 'success') {
            const notification = document.createElement('div');
            const bgColor = type === 'error' ? '#d32f2f' : '#2e7d32';
            notification.style.cssText = `position:fixed;top:20px;right:20px;background:${bgColor};color:white;padding:16px 24px;border-radius:8px;box-shadow:0 4px 20px rgba(0,0,0,0.3);z-index:1000;animation:slideIn 0.3s ease`;
            notification.textContent = message;
            document.body.appendChild(notification);
            setTimeout(() => notification.remove(), 3000);
        }
        
        // Authentication
        document.getElementById('authForm').onsubmit = async (e) => {
            e.preventDefault();
            const data = {
                username: document.getElementById('username').value,
                password: document.getElementById('password').value
            };

            const response = await fetch(`/api/${authMode}`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });

            const result = await response.json();
            if (result.success) {
                updateUI(true);
                showNotification(`${authMode === 'login' ? 'Signed in' : 'Account created'} successfully!`);
                showSection('profile');
                document.getElementById('authForm').reset();
            } else {
                showNotification(result.message, 'error');
            }
        };
        
        // Profile Management
        function showEditProfile() {
            document.getElementById('profileDisplay').style.display = 'none';
            document.getElementById('editProfileForm').style.display = 'block';
            loadProfileForEdit();
        }
        
        function hideEditProfile() {
            document.getElementById('profileDisplay').style.display = 'block';
            document.getElementById('editProfileForm').style.display = 'none';
        }
        
        async function loadProfileForEdit() {
            const response = await fetch('/api/profile');
            const result = await response.json();
            if (result.success && result.profile) {
                const p = result.profile;
                document.getElementById('name').value = p.name || '';
                document.getElementById('title').value = p.title || '';
                document.getElementById('about').value = p.about || '';
                document.getElementById('skills').value = p.skills || '';
                document.getElementById('email').value = p.email || '';
                document.getElementById('phone').value = p.phone || '';
                document.getElementById('location').value = p.location || '';
                document.getElementById('website').value = p.website || '';
                document.getElementById('github').value = p.github || '';
                document.getElementById('linkedin').value = p.linkedin || '';
            }
        }
        
        document.getElementById('profileForm').onsubmit = async (e) => {
            e.preventDefault();
            const data = {
                name: document.getElementById('name').value,
                title: document.getElementById('title').value,
                about: document.getElementById('about').value,
                skills: document.getElementById('skills').value,
                email: document.getElementById('email').value,
                phone: document.getElementById('phone').value,
                location: document.getElementById('location').value,
                website: document.getElementById('website').value,
                github: document.getElementById('github').value,
                linkedin: document.getElementById('linkedin').value
            };

            const response = await fetch('/api/profile', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });

            const result = await response.json();
            if (result.success) {
                showNotification('Profile updated successfully!');
                hideEditProfile();
                loadProfile();
            } else {
                showNotification(result.message, 'error');
            }
        };
        
        async function loadProfile() {
            const response = await fetch('/api/profile');
            const result = await response.json();
            const container = document.getElementById('profileDisplay');
            
            if (!result.success || !result.profile) {
                container.innerHTML = '<p style="text-align:center;padding:40px;">No profile yet. Click "Edit Profile" to create one.</p>';
                return;
            }

            const p = result.profile;
            const initials = p.name.split(' ').map(n => n[0]).join('').toUpperCase();
            container.innerHTML = `
                <div class="profile-card">
                    <div class="profile-header"></div>
                    <div class="profile-avatar">${initials}</div>
                    <div class="profile-info">
                        <h1 class="profile-name">${p.name}</h1>
                        <div class="profile-title">${p.title || 'Professional'}</div>
                        ${p.location ? `<div style="color:#666;margin-bottom:16px;">${p.location}</div>` : ''}
                        ${p.about ? `<div style="margin-bottom:16px;">${p.about}</div>` : ''}
                        ${p.skills ? `<div class="skills-list">${p.skills.split(',').map(s => `<span class="skill-tag">${s.trim()}</span>`).join('')}</div>` : ''}
                        <div class="contact-links">
                            ${p.email ? `<a href="mailto:${p.email}" class="contact-link">Email</a>` : ''}
                            ${p.phone ? `<a href="tel:${p.phone}" class="contact-link">Phone</a>` : ''}
                            ${p.website ? `<a href="${p.website}" target="_blank" class="contact-link">Website</a>` : ''}
                            ${p.github ? `<a href="${p.github}" target="_blank" class="contact-link">GitHub</a>` : ''}
                            ${p.linkedin ? `<a href="${p.linkedin}" target="_blank" class="contact-link">LinkedIn</a>` : ''}
                        </div>
                    </div>
                </div>
            `;
        }
        
        // Projects Management
        function showAddProject() {
            document.getElementById('addProjectForm').style.display = 'block';
        }
        
        function hideAddProject() {
            document.getElementById('addProjectForm').style.display = 'none';
            document.getElementById('projectForm').reset();
        }
        
        document.getElementById('projectForm').onsubmit = async (e) => {
            e.preventDefault();
            const data = {
                title: document.getElementById('projectTitle').value,
                description: document.getElementById('projectDescription').value,
                technologies: document.getElementById('projectTech').value,
                url: document.getElementById('projectUrl').value,
                github_url: document.getElementById('projectGithub').value,
                start_date: document.getElementById('projectStart').value,
                end_date: document.getElementById('projectEnd').value
            };

            const response = await fetch('/api/projects', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });

            const result = await response.json();
            if (result.success) {
                showNotification('Project added successfully!');
                hideAddProject();
                loadProjects();
            } else {
                showNotification(result.message, 'error');
            }
        };
        
        async function loadProjects() {
            const response = await fetch('/api/projects');
            const result = await response.json();
            const container = document.getElementById('projectsList');
            
            if (!result.success || result.projects.length === 0) {
                container.innerHTML = '<p style="text-align:center;padding:40px;">No projects yet. Add your first project!</p>';
                return;
            }

            container.innerHTML = result.projects.map(p => `
                <div class="item-card">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                        <div>
                            <div class="item-title">${p.title}</div>
                            <div class="item-date">${p.start_date || ''} ${p.end_date ? '- ' + p.end_date : ''}</div>
                        </div>
                        <button onclick="deleteProject(${p.id})" class="btn btn-danger btn-small">Delete</button>
                    </div>
                    ${p.description ? `<div class="item-description">${p.description}</div>` : ''}
                    ${p.technologies ? `<div class="tech-tags">${p.technologies.split(',').map(t => `<span class="tech-tag">${t.trim()}</span>`).join('')}</div>` : ''}
                    <div style="margin-top:12px;">
                        ${p.url ? `<a href="${p.url}" target="_blank" class="contact-link" style="margin-right:10px;">Live Demo</a>` : ''}
                        ${p.github_url ? `<a href="${p.github_url}" target="_blank" class="contact-link">GitHub</a>` : ''}
                    </div>
                </div>
            `).join('');
        }
        
        async function deleteProject(id) {
            if (!confirm('Delete this project?')) return;
            
            const response = await fetch('/api/projects', {
                method: 'DELETE',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id})
            });

            const result = await response.json();
            if (result.success) {
                showNotification('Project deleted!');
                loadProjects();
            }
        }
        
        // Experience Management
        function showAddExperience() {
            document.getElementById('addExperienceForm').style.display = 'block';
        }
        
        function hideAddExperience() {
            document.getElementById('addExperienceForm').style.display = 'none';
            document.getElementById('experienceForm').reset();
        }
        
        document.getElementById('experienceForm').onsubmit = async (e) => {
            e.preventDefault();
            const data = {
                company: document.getElementById('expCompany').value,
                position: document.getElementById('expPosition').value,
                description: document.getElementById('expDescription').value,
                start_date: document.getElementById('expStart').value,
                end_date: document.getElementById('expEnd').value,
                current: document.getElementById('expCurrent').checked
            };

            const response = await fetch('/api/experience', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });

            const result = await response.json();
            if (result.success) {
                showNotification('Experience added successfully!');
                hideAddExperience();
                loadExperience();
            } else {
                showNotification(result.message, 'error');
            }
        };
        
        async function loadExperience() {
            const response = await fetch('/api/experience');
            const result = await response.json();
            const container = document.getElementById('experienceList');
            
            if (!result.success || result.experience.length === 0) {
                container.innerHTML = '<p style="text-align:center;padding:40px;">No experience yet. Add your work history!</p>';
                return;
            }

            container.innerHTML = result.experience.map(e => `
                <div class="item-card">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                        <div>
                            <div class="item-title">${e.position}</div>
                            <div class="item-subtitle">${e.company}</div>
                            <div class="item-date">${e.start_date || ''} ${e.current ? '- Present' : (e.end_date ? '- ' + e.end_date : '')}</div>
                        </div>
                        <button onclick="deleteExperience(${e.id})" class="btn btn-danger btn-small">Delete</button>
                    </div>
                    ${e.description ? `<div class="item-description">${e.description}</div>` : ''}
                </div>
            `).join('');
        }
        
        async function deleteExperience(id) {
            if (!confirm('Delete this experience?')) return;
            
            const response = await fetch('/api/experience', {
                method: 'DELETE',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id})
            });

            const result = await response.json();
            if (result.success) {
                showNotification('Experience deleted!');
                loadExperience();
            }
        }
        
        // Education Management
        function showAddEducation() {
            document.getElementById('addEducationForm').style.display = 'block';
        }
        
        function hideAddEducation() {
            document.getElementById('addEducationForm').style.display = 'none';
            document.getElementById('educationForm').reset();
        }
        
        document.getElementById('educationForm').onsubmit = async (e) => {
            e.preventDefault();
            const data = {
                institution: document.getElementById('eduInstitution').value,
                degree: document.getElementById('eduDegree').value,
                field: document.getElementById('eduField').value,
                start_date: document.getElementById('eduStart').value,
                end_date: document.getElementById('eduEnd').value,
                current: document.getElementById('eduCurrent').checked
            };

            const response = await fetch('/api/education', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(data)
            });

            const result = await response.json();
            if (result.success) {
                showNotification('Education added successfully!');
                hideAddEducation();
                loadEducation();
            } else {
                showNotification(result.message, 'error');
            }
        };
        
        async function loadEducation() {
            const response = await fetch('/api/education');
            const result = await response.json();
            const container = document.getElementById('educationList');
            
            if (!result.success || result.education.length === 0) {
                container.innerHTML = '<p style="text-align:center;padding:40px;">No education yet. Add your academic background!</p>';
                return;
            }

            container.innerHTML = result.education.map(e => `
                <div class="item-card">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                        <div>
                            <div class="item-title">${e.degree}${e.field ? ' in ' + e.field : ''}</div>
                            <div class="item-subtitle">${e.institution}</div>
                            <div class="item-date">${e.start_date || ''} ${e.current ? '- Present' : (e.end_date ? '- ' + e.end_date : '')}</div>
                        </div>
                        <button onclick="deleteEducation(${e.id})" class="btn btn-danger btn-small">Delete</button>
                    </div>
                </div>
            `).join('');
        }
        
        async function deleteEducation(id) {
            if (!confirm('Delete this education?')) return;
            
            const response = await fetch('/api/education', {
                method: 'DELETE',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({id})
            });

            const result = await response.json();
            if (result.success) {
                showNotification('Education deleted!');
                loadEducation();
            }
        }
        
        async function logout() {
            await fetch('/api/logout', {method: 'POST'});
            updateUI(false);
            showSection('home');
            showNotification('Signed out successfully!');
        }
        
        // Check if user is already logged in
        fetch('/api/check-auth').then(r => r.json()).then(result => {
            if (result.success) {
                updateUI(true);
            }
        });
        
        // Add slide-in animation
        const style = document.createElement('style');
        style.textContent = '@keyframes slideIn { from { transform: translateX(100%); } to { transform: translateX(0); } }';
        document.head.appendChild(style);
    </script>
</body>
</html>
'''

def get_db_path():
    return os.environ.get('DATABASE_URL', 'portfolio.db')

def init_db():
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    c.execute('''CREATE TABLE IF NOT EXISTS profiles
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  name TEXT NOT NULL,
                  title TEXT,
                  about TEXT,
                  skills TEXT,
                  email TEXT,
                  github TEXT,
                  linkedin TEXT,
                  location TEXT,
                  phone TEXT,
                  website TEXT,
                  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS projects
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  title TEXT NOT NULL,
                  description TEXT,
                  technologies TEXT,
                  url TEXT,
                  github_url TEXT,
                  start_date TEXT,
                  end_date TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS experience
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  company TEXT NOT NULL,
                  position TEXT NOT NULL,
                  description TEXT,
                  start_date TEXT,
                  end_date TEXT,
                  current BOOLEAN DEFAULT 0,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    c.execute('''CREATE TABLE IF NOT EXISTS education
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  institution TEXT NOT NULL,
                  degree TEXT NOT NULL,
                  field TEXT,
                  start_date TEXT,
                  end_date TEXT,
                  current BOOLEAN DEFAULT 0,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (user_id) REFERENCES users (id))''')
    conn.commit()
    conn.close()

def hash_password(password):
    import secrets
    salt = secrets.token_hex(16)
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex() + ':' + salt

def verify_password(password, hashed):
    if ':' not in hashed:
        return hashlib.sha256(password.encode()).hexdigest() == hashed
    hash_part, salt = hashed.split(':')
    return hashlib.pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000).hex() == hash_part

@app.route('/')
def home():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    if not data.get('username') or not data.get('password'):
        return jsonify({'success': False, 'message': 'Username and password required'})
    if len(data['username']) < 3 or len(data['password']) < 6:
        return jsonify({'success': False, 'message': 'Username min 3 chars, password min 6 chars'})
    
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    try:
        c.execute('INSERT INTO users (username, password) VALUES (?, ?)',
                  (data['username'], hash_password(data['password'])))
        conn.commit()
        session['user_id'] = c.lastrowid
        session['username'] = data['username']
        session.permanent = True
        conn.close()
        return jsonify({'success': True})
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'success': False, 'message': 'Username already exists'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    if not data.get('username') or not data.get('password'):
        return jsonify({'success': False, 'message': 'Username and password required'})
    
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    c.execute('SELECT id, username, password FROM users WHERE username = ?', (data['username'],))
    user = c.fetchone()
    conn.close()
    
    if user and verify_password(data['password'], user[2]):
        session['user_id'] = user[0]
        session['username'] = user[1]
        session.permanent = True
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Invalid credentials'})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})

@app.route('/api/check-auth')
def check_auth():
    if 'user_id' in session:
        return jsonify({'success': True, 'username': session['username']})
    return jsonify({'success': False})

@app.route('/api/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    if request.method == 'POST':
        data = request.json
        if not data.get('name'):
            return jsonify({'success': False, 'message': 'Name is required'})
        
        conn = sqlite3.connect(get_db_path())
        c = conn.cursor()
        c.execute('SELECT id FROM profiles WHERE user_id = ?', (session['user_id'],))
        existing = c.fetchone()
        
        if existing:
            c.execute('''UPDATE profiles SET name=?, title=?, about=?, skills=?, email=?, github=?, linkedin=?, location=?, phone=?, website=?, updated_at=CURRENT_TIMESTAMP
                         WHERE user_id=?''',
                      (data['name'], data.get('title', ''), data.get('about', ''), data.get('skills', ''),
                       data.get('email', ''), data.get('github', ''), data.get('linkedin', ''), 
                       data.get('location', ''), data.get('phone', ''), data.get('website', ''), session['user_id']))
        else:
            c.execute('''INSERT INTO profiles (user_id, name, title, about, skills, email, github, linkedin, location, phone, website)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                      (session['user_id'], data['name'], data.get('title', ''), data.get('about', ''), data.get('skills', ''),
                       data.get('email', ''), data.get('github', ''), data.get('linkedin', ''), 
                       data.get('location', ''), data.get('phone', ''), data.get('website', '')))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    else:
        conn = sqlite3.connect(get_db_path())
        c = conn.cursor()
        c.execute('SELECT * FROM profiles WHERE user_id = ?', (session['user_id'],))
        profile = c.fetchone()
        conn.close()
        
        if profile:
            profile_data = {
                'name': profile[2], 'title': profile[3], 'about': profile[4], 'skills': profile[5],
                'email': profile[6], 'github': profile[7], 'linkedin': profile[8],
                'location': profile[9], 'phone': profile[10], 'website': profile[11]
            }
            return jsonify({'success': True, 'profile': profile_data})
        return jsonify({'success': True, 'profile': None})

@app.route('/api/projects', methods=['GET', 'POST', 'DELETE'])
def projects():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        if not data.get('title'):
            return jsonify({'success': False, 'message': 'Title is required'})
        
        c.execute('''INSERT INTO projects (user_id, title, description, technologies, url, github_url, start_date, end_date)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (session['user_id'], data['title'], data.get('description', ''), data.get('technologies', ''),
                   data.get('url', ''), data.get('github_url', ''), data.get('start_date', ''), data.get('end_date', '')))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        project_id = request.json.get('id')
        c.execute('DELETE FROM projects WHERE id = ? AND user_id = ?', (project_id, session['user_id']))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    else:
        c.execute('SELECT * FROM projects WHERE user_id = ? ORDER BY start_date DESC', (session['user_id'],))
        projects = c.fetchall()
        conn.close()
        
        result = []
        for p in projects:
            result.append({
                'id': p[0], 'title': p[2], 'description': p[3], 'technologies': p[4],
                'url': p[5], 'github_url': p[6], 'start_date': p[7], 'end_date': p[8]
            })
        return jsonify({'success': True, 'projects': result})

@app.route('/api/experience', methods=['GET', 'POST', 'DELETE'])
def experience():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        if not data.get('company') or not data.get('position'):
            return jsonify({'success': False, 'message': 'Company and position are required'})
        
        c.execute('''INSERT INTO experience (user_id, company, position, description, start_date, end_date, current)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (session['user_id'], data['company'], data['position'], data.get('description', ''),
                   data.get('start_date', ''), data.get('end_date', ''), data.get('current', False)))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        exp_id = request.json.get('id')
        c.execute('DELETE FROM experience WHERE id = ? AND user_id = ?', (exp_id, session['user_id']))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    else:
        c.execute('SELECT * FROM experience WHERE user_id = ? ORDER BY start_date DESC', (session['user_id'],))
        experiences = c.fetchall()
        conn.close()
        
        result = []
        for e in experiences:
            result.append({
                'id': e[0], 'company': e[2], 'position': e[3], 'description': e[4],
                'start_date': e[5], 'end_date': e[6], 'current': bool(e[7])
            })
        return jsonify({'success': True, 'experience': result})

@app.route('/api/education', methods=['GET', 'POST', 'DELETE'])
def education():
    if 'user_id' not in session:
        return jsonify({'success': False, 'message': 'Not authenticated'})
    
    conn = sqlite3.connect(get_db_path())
    c = conn.cursor()
    
    if request.method == 'POST':
        data = request.json
        if not data.get('institution') or not data.get('degree'):
            return jsonify({'success': False, 'message': 'Institution and degree are required'})
        
        c.execute('''INSERT INTO education (user_id, institution, degree, field, start_date, end_date, current)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  (session['user_id'], data['institution'], data['degree'], data.get('field', ''),
                   data.get('start_date', ''), data.get('end_date', ''), data.get('current', False)))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    elif request.method == 'DELETE':
        edu_id = request.json.get('id')
        c.execute('DELETE FROM education WHERE id = ? AND user_id = ?', (edu_id, session['user_id']))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    
    else:
        c.execute('SELECT * FROM education WHERE user_id = ? ORDER BY start_date DESC', (session['user_id'],))
        educations = c.fetchall()
        conn.close()
        
        result = []
        for e in educations:
            result.append({
                'id': e[0], 'institution': e[2], 'degree': e[3], 'field': e[4],
                'start_date': e[5], 'end_date': e[6], 'current': bool(e[7])
            })
        return jsonify({'success': True, 'education': result})

if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') != 'production'
    
    if debug:
        print(f"Enhanced Portfolio App running at http://127.0.0.1:{port}")
    
    app.run(host='0.0.0.0', port=port, debug=debug)