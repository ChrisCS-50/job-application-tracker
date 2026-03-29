import json
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from database import JobTrackerDB

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_flash_messages'
db = JobTrackerDB()

# --- AUTH SETUP ---
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'warning'

class User(UserMixin):
    def __init__(self, id, username, is_admin=True):
        self.id = id
        self.username = username
        self.is_admin = is_admin

@login_manager.user_loader
def load_user(user_id):
    u = db.get_user_by_id(user_id)
    if u:
        return User(id=u['id'], username=u['username'], is_admin=u['is_admin'])
    return None

@app.before_request
def require_login():
    allowed_routes = ['login', 'register', 'static']
    if request.endpoint not in allowed_routes and not current_user.is_authenticated:
        return redirect(url_for('login', next=request.url))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        u = db.get_user_by_username(username)
        
        if u and check_password_hash(u['password_hash'], password):
            user = User(id=u['id'], username=u['username'], is_admin=u['is_admin'])
            login_user(user)
            flash('Login successful! Welcome to JobTracker Pro.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if db.get_user_by_username(username):
            flash('Username already exists.', 'danger')
        else:
            if db.create_user(username, generate_password_hash(password), is_admin=False):
                flash('Account created successfully! Please log in.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Error creating account.', 'danger')
                
    return render_template('register.html')


@app.route('/admin')
@login_required
def admin_panel():
    if not current_user.is_admin:
        flash('Access completely restricted to Administrators.', 'danger')
        return redirect(url_for('dashboard'))
    
    users = db.get_all_users()
    return render_template('admin.html', users=users, active_page='admin')

@app.route('/admin/toggle/<int:id>', methods=['POST'])
@login_required
def toggle_admin(id):
    if not current_user.is_admin:
        return redirect(url_for('dashboard'))
        
    u = db.get_user_by_id(id)
    if not u:
        flash('User not found.', 'danger')
        return redirect(url_for('admin_panel'))
        
    # Prevent self-demotion
    if id == current_user.id:
        flash('Cannot alter your own Admin permissions securely.', 'warning')
        return redirect(url_for('admin_panel'))
        
    new_status = not u['is_admin']
    if db.update_user_role(id, new_status):
        flash(f"User {u['username']} admin rights updated.", "success")
    else:
        flash("Failed to update user role.", "danger")
        
    return redirect(url_for('admin_panel'))

@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# --- DASHBOARD ---
@app.route('/')
def dashboard():
    view_scope = request.args.get('view', 'all' if current_user.is_admin else 'personal')
    if not current_user.is_admin:
        view_scope = 'personal'
    
    stats = db.get_dashboard_stats(user_id=current_user.id, is_admin=current_user.is_admin, view_scope=view_scope)
    return render_template('dashboard.html', stats=stats, view_scope=view_scope)


# --- COMPANIES ---
@app.route('/companies')
def list_companies():
    view = request.args.get('view')
    uid = current_user.id if (not current_user.is_admin or view == 'personal') else None
    companies = db.get_all_companies(user_id=uid)
    return render_template('companies.html', companies=companies, active_page='companies')

@app.route('/companies/add', methods=['GET', 'POST'])
def add_company():
    if request.method == 'POST':
        name = request.form['name']
        industry = request.form['industry']
        website = request.form['website']
        city = request.form['city']
        state = request.form['state']
        notes = request.form['notes']
        if db.add_company(name, industry, website, city, state, notes, created_by=current_user.id):
            flash('Company added successfully!', 'success')
        else:
            flash('Error adding company.', 'danger')
        return redirect(url_for('list_companies'))
    return render_template('company_form.html')

@app.route('/companies/<int:id>/edit', methods=['GET', 'POST'])
def edit_company(id):
    if request.method == 'POST':
        name = request.form['name']
        industry = request.form['industry']
        website = request.form['website']
        city = request.form['city']
        state = request.form['state']
        notes = request.form['notes']
        if db.update_company(id, name, industry, website, city, state, notes):
            flash('Company updated!', 'success')
        else:
            flash('Error updating company.', 'danger')
        return redirect(url_for('list_companies'))
    
    company = db.get_company(id)
    return render_template('company_form.html', company=company)

@app.route('/companies/<int:id>/delete', methods=['POST'])
def delete_company(id):
    if db.delete_company(id):
        flash('Company deleted!', 'warning')
    else:
        flash('Error deleting company.', 'danger')
    return redirect(url_for('list_companies'))

@app.route('/company/<int:id>')
def company_profile(id):
    profile = db.get_company_profile(id)
    if not profile or not profile.get('company'):
        flash('Company not found.', 'danger')
        return redirect(url_for('list_companies'))
    return render_template('company_profile.html', profile=profile, active_page='companies')

# --- JOBS ---
@app.route('/jobs')
def list_jobs():
    view = request.args.get('view')
    uid = current_user.id if (not current_user.is_admin or view == 'personal') else None
    jobs = db.get_all_jobs(user_id=uid)
    return render_template('jobs.html', jobs=jobs, active_page='jobs')

@app.route('/jobs/add', methods=['GET', 'POST'])
def add_job():
    if request.method == 'POST':
        company_id = request.form['company_id']
        title = request.form['job_title']
        jtype = request.form['job_type']
        s_min = request.form['salary_min'] or None
        s_max = request.form['salary_max'] or None
        url = request.form['job_url']
        d_posted = request.form['date_posted']
        reqs = request.form['requirements']
        
        req_list = [r.strip() for r in reqs.split(',') if r.strip()]

        if db.add_job(company_id, title, jtype, s_min, s_max, url, d_posted, req_list, created_by=current_user.id):
            flash('Job added!', 'success')
        else:
            flash('Error adding job.', 'danger')
        return redirect(url_for('list_jobs'))

    uid = None if current_user.is_admin else current_user.id
    companies = db.get_all_companies(user_id=uid)
    return render_template('job_form.html', companies=companies)

@app.route('/jobs/<int:id>/edit', methods=['GET', 'POST'])
def edit_job(id):
    if request.method == 'POST':
        company_id = request.form['company_id']
        title = request.form['job_title']
        jtype = request.form['job_type']
        s_min = request.form['salary_min'] or None
        s_max = request.form['salary_max'] or None
        url = request.form['job_url']
        d_posted = request.form['date_posted']
        reqs = request.form['requirements']
        
        req_list = [r.strip() for r in reqs.split(',') if r.strip()]

        if db.update_job(id, company_id, title, jtype, s_min, s_max, url, d_posted, req_list):
            flash('Job updated!', 'success')
        else:
            flash('Error updating job.', 'danger')
        return redirect(url_for('list_jobs'))

    job = db.get_job(id)
    uid = None if current_user.is_admin else current_user.id
    companies = db.get_all_companies(user_id=uid)
    
    # helper for form
    if job and job['requirements']:
        try:
            req_parsed = json.loads(job['requirements'])
            job['requirements_str'] = ', '.join(req_parsed) if isinstance(req_parsed, list) else str(job['requirements'])
        except:
            job['requirements_str'] = str(job['requirements'])
    else:
        job['requirements_str'] = ''
        
    return render_template('job_form.html', job=job, companies=companies)

@app.route('/jobs/<int:id>/delete', methods=['POST'])
def delete_job(id):
    if db.delete_job(id):
        flash('Job deleted!', 'warning')
    else:
        flash('Error', 'danger')
    return redirect(url_for('list_jobs'))


# --- APPLICATIONS ---
@app.route('/applications')
def list_applications():
    view = request.args.get('view')
    uid = current_user.id if (not current_user.is_admin or view == 'personal') else None
    apps = db.get_all_applications(user_id=uid)
    
    all_contacts = db.get_all_contacts(user_id=uid)
    contacts_map = {str(c['contact_id']): c for c in all_contacts}
    
    for app_item in apps:
        resolved = []
        if app_item.get('interview_contacts'):
            ids = str(app_item['interview_contacts']).split(',')
            for cid in ids:
                cid_strip = cid.strip()
                if cid_strip in contacts_map:
                    resolved.append(contacts_map[cid_strip])
        app_item['resolved_contacts'] = resolved
        
    return render_template('applications.html', applications=apps, active_page='applications')

@app.route('/applications/add', methods=['GET', 'POST'])
def add_application():
    if request.method == 'POST':
        job_id = request.form['job_id']
        app_date = request.form['application_date']
        status = request.form['status']
        res_ver = request.form['resume_version']
        cl_sent = 1 if 'cover_letter_sent' in request.form else 0
        int_data = request.form['interview_data']
        interview_contacts = ','.join(request.form.getlist('interview_contacts'))
        
        parsed_int_data = None
        if int_data.strip():
            try:
                parsed_int_data = json.loads(int_data)
            except:
                parsed_int_data = {"notes": int_data}

        if db.add_application(job_id, app_date, status, res_ver, cl_sent, parsed_int_data, user_id=current_user.id, interview_contacts=interview_contacts):
            flash('Application added!', 'success')
        else:
            flash('Error adding application.', 'danger')
        return redirect(url_for('list_applications'))

    uid = None if current_user.is_admin else current_user.id
    jobs = db.get_all_jobs(user_id=uid)
    companies = db.get_all_companies(user_id=uid)
    contacts = db.get_all_contacts(user_id=uid)
    return render_template('application_form.html', jobs=jobs, companies=companies, contacts=contacts)

@app.route('/applications/<int:id>/edit', methods=['GET', 'POST'])
def edit_application(id):
    if request.method == 'POST':
        job_id = request.form['job_id']
        app_date = request.form['application_date']
        status = request.form['status']
        res_ver = request.form['resume_version']
        cl_sent = 1 if 'cover_letter_sent' in request.form else 0
        int_data = request.form['interview_data']
        interview_contacts = ','.join(request.form.getlist('interview_contacts'))
        
        parsed_int_data = None
        if int_data.strip():
            try:
                parsed_int_data = json.loads(int_data)
            except:
                parsed_int_data = {"notes": int_data}

        if db.update_application(id, job_id, app_date, status, res_ver, cl_sent, parsed_int_data, interview_contacts=interview_contacts):
            flash('Application updated!', 'success')
        else:
            flash('Error updating application.', 'danger')
        return redirect(url_for('list_applications'))

    app_data = db.get_application(id)
    uid = None if current_user.is_admin else current_user.id
    jobs = db.get_all_jobs(user_id=uid)
    companies = db.get_all_companies(user_id=uid)
    contacts = db.get_all_contacts(user_id=uid)
    return render_template('application_form.html', app=app_data, jobs=jobs, companies=companies, contacts=contacts)

@app.route('/applications/<int:id>/delete', methods=['POST'])
def delete_application(id):
    if db.delete_application(id):
        flash('Application deleted!', 'warning')
    else:
        flash('Error', 'danger')
    return redirect(url_for('list_applications'))


@app.route('/offers')
def list_offers():
    view = request.args.get('view')
    uid = current_user.id if (not current_user.is_admin or view == 'personal') else None
    all_apps = db.get_all_applications(user_id=uid)
    offers = [app for app in all_apps if app['status'] in ('Offer', 'Offer Accepted')]
    
    all_contacts = db.get_all_contacts(user_id=uid)
    contacts_map = {str(c['contact_id']): c for c in all_contacts}
    
    for offer in offers:
        resolved = []
        if offer.get('interview_contacts'):
            ids = offer['interview_contacts'].split(',')
            for cid in ids:
                if cid.strip() in contacts_map:
                    resolved.append(contacts_map[cid.strip()])
        offer['resolved_contacts'] = resolved
        
    return render_template('offers.html', offers=offers, active_page='dashboard')

# --- CONTACTS ---
@app.route('/contacts')
def list_contacts():
    uid = None if current_user.is_admin else current_user.id
    contacts = db.get_all_contacts(user_id=uid)
    return render_template('contacts.html', contacts=contacts, active_page='contacts')

@app.route('/contacts/add', methods=['GET', 'POST'])
def add_contact():
    if request.method == 'POST':
        company_id = request.form['company_id'] or None
        name = request.form['contact_name']
        title = request.form['title']
        email = request.form['email']
        phone = request.form['phone']
        linkedin = request.form['linkedin_url']
        notes = request.form['notes']

        if db.add_contact(company_id, name, title, email, phone, linkedin, notes, created_by=current_user.id):
            flash('Contact added!', 'success')
        else:
            flash('Error adding contact.', 'danger')
        return redirect(url_for('list_contacts'))

    companies = db.get_all_companies()
    return render_template('contact_form.html', companies=companies)

@app.route('/contacts/<int:id>/edit', methods=['GET', 'POST'])
def edit_contact(id):
    if request.method == 'POST':
        company_id = request.form['company_id'] or None
        name = request.form['contact_name']
        title = request.form['title']
        email = request.form['email']
        phone = request.form['phone']
        linkedin = request.form['linkedin_url']
        notes = request.form['notes']

        if db.update_contact(id, company_id, name, title, email, phone, linkedin, notes):
            flash('Contact updated!', 'success')
        else:
            flash('Error updating contact.', 'danger')
        return redirect(url_for('list_contacts'))

    contact = db.get_contact(id)
    companies = db.get_all_companies()
    return render_template('contact_form.html', contact=contact, companies=companies)

@app.route('/contacts/<int:id>/delete', methods=['POST'])
def delete_contact(id):
    if db.delete_contact(id):
        flash('Contact deleted!', 'warning')
    else:
        flash('Error', 'danger')
    return redirect(url_for('list_contacts'))


# --- JOB MATCH ---
@app.route('/job-match', methods=['GET', 'POST'])
def job_match():
    match_results = []
    user_skills_str = ''
    
    if request.method == 'POST':
        user_skills_str = request.form.get('skills', '')
        user_skills = [s.strip().lower() for s in user_skills_str.split(',') if s.strip()]
        user_skills_set = set(user_skills)
        
        if user_skills_set:
            jobs = db.get_all_jobs()
            for job in jobs:
                reqs = []
                if job['requirements']:
                    try:
                        parsed = json.loads(job['requirements'])
                        if isinstance(parsed, list):
                            reqs = parsed
                        else:
                            reqs = [str(job['requirements'])]
                    except:
                        reqs = [str(job['requirements'])]
                
                if reqs:
                    # Standardize all requirements to lower-case strings
                    processed_reqs = []
                    for r in reqs:
                        if isinstance(r, dict):
                            # Extract value from 'skill' key or first value found
                            skill_val = r.get('skill') or next(iter(r.values()), "")
                            processed_reqs.append(str(skill_val).strip().lower())
                        else:
                            processed_reqs.append(str(r).strip().lower())
                    
                    reqs_set = set(processed_reqs)
                    
                    matches = reqs_set.intersection(user_skills_set)
                    missing = reqs_set.difference(user_skills_set)
                    
                    match_percent = int((len(matches) / len(reqs_set)) * 100) if reqs_set else 0
                    
                    match_results.append({
                        'job': job,
                        'percent': match_percent,
                        'total_reqs': len(reqs_set),
                        'match_count': len(matches),
                        'missing': [str(r).title() for r in missing]
                    })
                else:
                    # No requirements, 100% implicitly? Or skip. Skipped for now.
                    pass
                    
            # Sort by match percentage DESC
            match_results.sort(key=lambda x: x['percent'], reverse=True)
            
    return render_template('job_match.html', 
                           results=match_results, 
                           user_skills=user_skills_str,
                           active_page='job-match')

if __name__ == '__main__':
    app.run(debug=True, port=5000)
