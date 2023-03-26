import math
import requests  # Move this line up here, along with the other imports
import os
import sys
from flask import Flask, render_template, send_from_directory, request, redirect, url_for, make_response, session
import subprocess
import datetime
from flaskext.mysql import MySQL
from flask import send_file
from flask import jsonify


app = Flask(__name__)
app.secret_key = 'MottInProgress'

# Configure MySQL connection
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Rugby1234$'
app.config['MYSQL_DATABASE_DB'] = 'matrixDB'

mysql = MySQL()
mysql.init_app(app)


@app.route('/')
def index():
    conn = mysql.connect()
    cur = conn.cursor()
    
    cur.execute("SELECT DISTINCT date FROM testHistory")
    dates = [record[0] for record in cur.fetchall()]

    cur.execute("SELECT * FROM notes")
    notes = cur.fetchall()

    cur.close()
    return render_template('index.html', dates=dates, notes=notes)


@app.route('/search_by_date', methods=['POST', 'GET'])
def search_by_date():
    try:
        if request.method == 'POST':
            selected_date = request.form['date']
            failed_test_cases = request.form.get('failed_test_cases') == '1'
            session['selected_date'] = selected_date
            session['failed_test_cases'] = failed_test_cases
        else:
            selected_date = session.get('selected_date', None)
            failed_test_cases = session.get('failed_test_cases', False)

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        offset = (page - 1) * per_page
        conn = mysql.connect()
        cur = conn.cursor()
        if failed_test_cases:
            query = "SELECT videoTitle, utterance, result, testingNote, date FROM testHistory WHERE date = %s AND LOWER(result) = 'fail'"
        else:
            query = "SELECT videoTitle, utterance, result, testingNote, date FROM testHistory WHERE date = %s"
        cur.execute(query, (selected_date,))
        results = cur.fetchall()
        cur.close()
        cur = conn.cursor()
        total_records = len(results)
        total_pages = math.ceil(total_records / per_page)
        query = query + " LIMIT %s OFFSET %s"
        cur.execute(query, (selected_date, per_page, offset))
        results = cur.fetchall()
        cur.close()
        return render_template('results.html', results=results, total_pages=total_pages, current_page=page, per_page=per_page)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return f"An error occurred: {e}", 500


@app.route('/search', methods=['POST', 'GET'])
def search():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        offset = (page - 1) * per_page
        conn = mysql.connect()
        cur = conn.cursor()

        cur.execute("SELECT COUNT(*) FROM testHistory")
        total_records = cur.fetchone()[0]

        query = f"SELECT videoTitle, utterance, result, testingNote, date FROM testHistory LIMIT {per_page} OFFSET {offset}"
        cur.execute(query)
        results = cur.fetchall()
        cur.close()
        total_pages = math.ceil(total_records / per_page)

        return render_template('results.html', results=results, total_pages=total_pages, current_page=page, per_page=per_page)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return f"An error occurred: {e}", 500


@app.route('/search_by_keyword', methods=['POST', 'GET'])
def search_by_keyword():
    try:
        if request.method == 'POST':
            keyword = request.form['keyword']
            session['keyword'] = keyword
        else:
            keyword = session.get('keyword', None)
            if keyword is None:
                return "No keyword provided.", 400

        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        offset = (page - 1) * per_page
        conn = mysql.connect()
        cur = conn.cursor()
        query = "SELECT COUNT(*) FROM testHistory WHERE LOWER(videoTitle) LIKE %s"
        cur.execute(query, (f'%{keyword.lower()}%',))
        total_records = cur.fetchone()[0]
        query = "SELECT videoTitle, utterance, result, testingNote, date FROM testHistory WHERE LOWER(videoTitle) LIKE %s LIMIT %s OFFSET %s"
        cur.execute(query, (f'%{keyword.lower()}%', per_page, offset))
        results = cur.fetchall()
        cur.close()
        total_pages = math.ceil(total_records / per_page)
        return render_template('results.html', results=results, total_pages=total_pages, current_page=page, per_page=per_page)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return f"An error occurred: {e}", 500


@app.route('/source_file_center')
def source_file_center():
    files = os.listdir('source/PrimeSourceFile')
    sorted_files = sorted(files)
    return render_template('source_file_center.html', files=sorted_files)


@app.route('/download_file/<filename>')
def download_file(filename):
    source_files_path = 'source/PrimeSourceFile'
    return send_from_directory(source_files_path, filename, as_attachment=True)


@app.route('/generate_test_data/<filename>')
def generate_test_data(filename):
    try:
        source_files_path = 'source/PrimeSourceFile'
        return send_from_directory(source_files_path, filename, as_attachment=True)
    except Exception as e:
        return str(e)


@app.route('/generate_delta/<filename>')
def generate_delta(filename):
    try:
        source_files_path = 'source/PrimeSourceFile'
        return send_from_directory(source_files_path, filename, as_attachment=True)
    except Exception as e:
        return str(e)


@app.route('/download_netflix_catalog', methods=['POST'])
def download_netflix_catalog():
    country_code = request.form.get('country_code').upper()
    language = request.form['language'].lower()
    if not country_code:
        return "Country code is required", 400
    if not language:
        return "language code is required", 400

    url = f"http://api.netflix.com/catalog/feeds/{language}_{country_code}.xml?oauth_consumer_key=amazon"
    response = requests.get(url)

    if response.status_code == 200:
        output = make_response(response.content)
        output.headers[
            "Content-Disposition"] = f"attachment; filename=netflix_catalog_{language}_{country_code}.xml"
        output.headers["Content-Type"] = "application/xml"
        return output
    else:
        return "Error downloading file", 500


def run_netflix_top_titles_script(country_code):
    static_folder = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'static')
    script_path = os.path.join(static_folder, 'js', 'netflix.js')
    output_file = os.path.join(os.path.dirname(
        os.path.abspath(__file__)), 'netflix_top_titles.xlsx')

    command = f'node {script_path} {country_code}'
    process = subprocess.Popen(command, shell=True)
    process.wait()

    return output_file


@app.route('/download_netflix_top_titles', methods=['POST'])
def download_netflix_top_titles():
    country_code = request.form.get('country_code')
    if not country_code:
        return 'Country code is required', 400

    try:
        output_file = run_netflix_top_titles_script(country_code)
        return send_file(output_file, as_attachment=True, attachment_filename='netflix_top_titles.xlsx')
    except Exception as e:
        print(e)
        return 'An error occurred while generating the file', 500



@app.route('/notes')
def notes():
    return render_template('notes.html')



@app.route('/save-note', methods=['POST'])
def save_note():
    content = request.form['content']
    timestamp = datetime.datetime.now()
    status = 'unread'

    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("INSERT INTO notes (timestamp, content, status) VALUES (%s, %s, %s)", (timestamp, content, status))
    conn.commit()
    cur.close()

    return redirect(url_for('index'))


@app.route('/mark-as-read/<int:note_id>', methods=['POST'])
def mark_as_read(note_id):
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("UPDATE notes SET status = 'read' WHERE id = %s", (note_id,))
    conn.commit()
    cur.close()
    
    return redirect(url_for('index'))


@app.route('/delete-note/<int:note_id>', methods=['POST'])
def delete_note(note_id):
    conn = mysql.connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM notes WHERE id = %s", (note_id,))
    conn.commit()
    cur.close()

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
