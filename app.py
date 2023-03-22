import math
import sys
from flask import Flask, render_template, request
from flaskext.mysql import MySQL

app = Flask(__name__)

# Configure MySQL connection
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Rugby1234$'
app.config['MYSQL_DATABASE_DB'] = 'matrixDB'

mysql = MySQL()
mysql.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

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



if __name__ == '__main__':
    app.run(debug=True)