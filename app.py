import json
from flask import Flask, render_template, request, redirect, url_for, flash
from database import JobTrackerDB

app = Flask(__name__)
app.secret_key = 'super_secret_key_for_flash_messages'
db = JobTrackerDB()

# --- DASHBOARD ---
@app.route('/')
def dashboard():
    stats = db.get_dashboard_stats()
    return render_template('dashboard.html', stats=stats)


# --- COMPANIES ---
@app.route('/companies')
def list_companies():
    companies = db.get_all_companies()
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
        if db.add_company(name, industry, website, city, state, notes):
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


# --- JOBS ---
@app.route('/jobs')
def list_jobs():
    jobs = db.get_all_jobs()
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

        if db.add_job(company_id, title, jtype, s_min, s_max, url, d_posted, req_list):
            flash('Job added!', 'success')
        else:
            flash('Error adding job.', 'danger')
        return redirect(url_for('list_jobs'))

    companies = db.get_all_companies()
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
    companies = db.get_all_companies()
    
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
    apps = db.get_all_applications()
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
        
        parsed_int_data = None
        if int_data.strip():
            try:
                parsed_int_data = json.loads(int_data)
            except:
                parsed_int_data = {"notes": int_data}

        if db.add_application(job_id, app_date, status, res_ver, cl_sent, parsed_int_data):
            flash('Application added!', 'success')
        else:
            flash('Error adding application.', 'danger')
        return redirect(url_for('list_applications'))

    jobs = db.get_all_jobs()
    return render_template('application_form.html', jobs=jobs)

@app.route('/applications/<int:id>/edit', methods=['GET', 'POST'])
def edit_application(id):
    if request.method == 'POST':
        job_id = request.form['job_id']
        app_date = request.form['application_date']
        status = request.form['status']
        res_ver = request.form['resume_version']
        cl_sent = 1 if 'cover_letter_sent' in request.form else 0
        int_data = request.form['interview_data']
        
        parsed_int_data = None
        if int_data.strip():
            try:
                parsed_int_data = json.loads(int_data)
            except:
                parsed_int_data = {"notes": int_data}

        if db.update_application(id, job_id, app_date, status, res_ver, cl_sent, parsed_int_data):
            flash('Application updated!', 'success')
        else:
            flash('Error updating application.', 'danger')
        return redirect(url_for('list_applications'))

    app_data = db.get_application(id)
    jobs = db.get_all_jobs()
    return render_template('application_form.html', app=app_data, jobs=jobs)

@app.route('/applications/<int:id>/delete', methods=['POST'])
def delete_application(id):
    if db.delete_application(id):
        flash('Application deleted!', 'warning')
    else:
        flash('Error', 'danger')
    return redirect(url_for('list_applications'))


# --- CONTACTS ---
@app.route('/contacts')
def list_contacts():
    contacts = db.get_all_contacts()
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

        if db.add_contact(company_id, name, title, email, phone, linkedin, notes):
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
                    reqs_lower = [r.strip().lower() for r in reqs]
                    reqs_set = set(reqs_lower)
                    
                    matches = reqs_set.intersection(user_skills_set)
                    missing = reqs_set.difference(user_skills_set)
                    
                    match_percent = int((len(matches) / len(reqs_set)) * 100) if reqs_set else 0
                    
                    match_results.append({
                        'job': job,
                        'percent': match_percent,
                        'total_reqs': len(reqs_set),
                        'match_count': len(matches),
                        'missing': [r.title() for r in missing]
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
