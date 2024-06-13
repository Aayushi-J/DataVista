from flask import Flask, render_template, request, redirect, url_for, session
import pymysql
import logging
from functools import wraps
import time

app = Flask(__name__)
app.secret_key = '7a1e1aba7eae45e1b42f5372efe94ac3'  # Update with your secret key

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s: %(message)s')

# Configure MySQL database connection
db_config = {
    'host': 'datavista.c3m826cwe288.ap-south-1.rds.amazonaws.com',
    'port': 3306,
    'user': 'admin',
    'password': 'AbhiAppu',
    'db': 'DataVista',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection(retries=5, delay=5):
    for attempt in range(retries):
        try:
            connection = pymysql.connect(**db_config)
            logging.info("Database connection established")
            return connection
        except pymysql.MySQLError as e:
            logging.error(f"Database connection error: {e}")
            if attempt < retries - 1:
                time.sleep(delay)
            else:
                return None

def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrap

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        connection = get_db_connection()
        if connection:
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT * FROM UserDetails WHERE Username = %s AND Password = %s", (username, password))
                    user = cursor.fetchone()
                    if user:
                        session['user'] = username
                        user_id = user['UserID']
                        user_redirects = {
                            'SM24001': 'sales_manager',
                            'PM24001': 'product_manager',
                            'STME24001': 'STM_east',
                            'STMW24001': 'STM_west',
                            'STMMW24001': 'STM_midwest',
                            'STMS24001': 'STM_south',
                            'PTM24HEALTH': 'PTM_east',
                            'PTM24FASHION': 'PTM_south',
                            'PTM24HOUSE': 'PTM_midwest',
                            'PTM24OUTING': 'PTM_west'
                        }
                        page_name = user_redirects.get(user_id, 'error')
                        return redirect(url_for(page_name))
                    else:
                        logging.warning("Invalid credentials")
                        return redirect(url_for('error'))
            except pymysql.MySQLError as e:
                logging.error(f"Query execution error: {e}")
                return redirect(url_for('error'))
            finally:
                connection.close()
        else:
            return redirect(url_for('error'))
    return render_template('login.html')

def get_user_details(username):
    connection = get_db_connection()
    if connection:
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT FirstName, RoleID FROM UserDetails WHERE Username = %s", (username,))
                user_details = cursor.fetchone()
                if user_details:
                    cursor.execute("SELECT RoleName FROM UserRole WHERE RoleID = %s", (user_details['RoleID'],))
                    role = cursor.fetchone()
                    if role:
                        return user_details['FirstName'], role['RoleName']
                    else:
                        return user_details['FirstName'], "Unknown"
                else:
                    return "Unknown", "Unknown"
        except pymysql.MySQLError as e:
            logging.error(f"Query execution error: {e}")
            return "Unknown", "Unknown"
        finally:
            connection.close()
    return "Unknown", "Unknown"

@app.route('/sales_manager')
@login_required
def sales_manager():
    username = session['user']
    first_name, role_name = get_user_details(username)
    return render_template('sales_manager.html', first_name=first_name, role_name=role_name)

@app.route('/product_manager')
@login_required
def product_manager():
    username = session['user']
    first_name, role_name = get_user_details(username)
    return render_template('product_manager.html', first_name=first_name, role_name=role_name)

@app.route('/STM_east')
@login_required
def STM_east():
    username = session['user']
    first_name, role_name = get_user_details(username)
    return render_template('STM_east.html', first_name=first_name, role_name=role_name)

@app.route('/STM_west')
@login_required
def STM_west():
    username = session['user']
    first_name, role_name = get_user_details(username)
    return render_template('STM_west.html', first_name=first_name, role_name=role_name)

@app.route('/STM_midwest')
@login_required
def STM_midwest():
    username = session['user']
    first_name, role_name = get_user_details(username)
    return render_template('STM_midwest.html', first_name=first_name, role_name=role_name)

@app.route('/STM_south')
@login_required
def STM_south():
    username = session['user']
    first_name, role_name = get_user_details(username)
    return render_template('STM_south.html', first_name=first_name, role_name=role_name)

@app.route('/PTM_east')
@login_required
def PTM_east():
    username = session['user']
    first_name, role_name = get_user_details(username)
    return render_template('PTM_east.html', first_name=first_name, role_name=role_name)

@app.route('/PTM_south')
@login_required
def PTM_south():
    username = session['user']
    first_name, role_name = get_user_details(username)
    return render_template('PTM_south.html', first_name=first_name, role_name=role_name)

@app.route('/PTM_midwest')
@login_required
def PTM_midwest():
    username = session['user']
    first_name, role_name = get_user_details(username)
    return render_template('PTM_midwest.html', first_name=first_name, role_name=role_name)

@app.route('/PTM_west')
@login_required
def PTM_west():
    username = session['user']
    first_name, role_name = get_user_details(username)
    return render_template('PTM_west.html', first_name=first_name, role_name=role_name)

@app.route('/error')
def error():
    return render_template('error.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
