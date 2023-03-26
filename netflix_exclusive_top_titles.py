from flask import Flask, request, send_file
import subprocess
import os

app = Flask(__name__)

def run_netflix_top_titles_script(country_code):
    static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    script_path = os.path.join(static_folder, 'js', 'netflix.js')
    output_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'netflix_top_titles.xlsx')
    
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
