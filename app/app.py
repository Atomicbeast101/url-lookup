# Imports
import validators
import psycopg2
import flask
import os
import re

# Attributes
app = flask.Flask(__name__)
WEB_TYPE = 'http'
HOST_CHARS_ALLOWED = re.compile("(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
SQL_GET_URL = '''
    SELECT is_safe 
    FROM paths P
        LEFT JOIN hosts H ON H.id = P.hosts_id
    WHERE
        H.host = %s
        AND P.url = %s;'''
db = None

# Class
class DB():
    def __init__(self):
        self.write_con = self.write_connect()
        self.read_con = self.read_connect()
    
    def write_connect(self):
        try:
            con = psycopg2.connect(
                host=os.environ['DB_WRITE_HOST'],
                port=os.environ['DB_WRITE_PORT'],
                database=os.environ['DB_NAME'],
                user=os.environ['DB_USER'],
                password=os.environ['DB_PASSWORD']
            )
            con.autocommit = False
            print('INFO: Sucessfully connected to write database!', flush=True)
            return con
        except Exception as ex:
            print('ERROR: Unable to connect to write database! Reason: {}'.format(str(ex)), flush=True)
            exit(0)
    
    def read_connect(self):
        try:
            con = psycopg2.connect(
                host=os.environ['DB_READ_HOST'],
                port=os.environ['DB_READ_PORT'],
                database=os.environ['DB_NAME'],
                user=os.environ['DB_USER'],
                password=os.environ['DB_PASSWORD']
            )
            print('INFO: Sucessfully connected to read database!', flush=True)
            return con
        except Exception as ex:
            print('ERROR: Unable to connect to read database! Reason: {}'.format(str(ex)), flush=True)
            exit(0)

    def get_write_cursor(self):
        try:
            cursor = self.write_con.cursor()
            cursor.execute('SELECT 1')
        except Exception as ex:
            self.write_con = self.write_connect()
            cursor = self.write_con.cursor()
        return cursor

    def get_read_cursor(self):
        try:
            cursor = self.read_con.cursor()
            cursor.execute('SELECT 1')
        except Exception as ex:
            self.read_con = self.read_connect()
            cursor = self.read_con.cursor()
        return cursor

# Functions
def get_url(cursor, host, url):
    try:
        cursor.execute(SQL_GET_URL, (host.lower(), url.lower()))
        data = cursor.fetchone()
        if data:
            return 'FOUND', data[0]
        return 'NOT_FOUND', None
    except Exception as ex:
        print('ERROR: Unable to query data from the database! Reason: {}'.format(str(ex)), flush=True)
        return 'ERROR', 'Unable to query data from the database!'

def validate_hostname(host):
    return HOST_CHARS_ALLOWED.match(host)

def validate_host(host):
    if ':' in host:
        host = host.split(':')
        if validate_hostname(host[0]) or validators.domain(host[0]) or validators.ipv4(host[0]) or validators.ipv6(host[0]):
            if host[1].isnumeric():
                if 1 <= int(host[1]) <= 65535:
                    return True, None
                return False, 'Invalid port! Must be numeric and between 1 and 65535.'
        return False, 'Invalid hostname!'
    else:
        if validate_hostname(host) or validators.domain(host) or validators.ipv4(host) or validators.ipv6(host):
            return True, None
        return False, 'Invalid hostname!'

def validate_path(host, path):
    if validators.url('{web_type}://{host}/{path}'.format(web_type=WEB_TYPE, host=host, path=path)):
        return True, None
    return False, 'Invalid path!'

# Flask Calls
@app.route('/', methods=['GET'])
def index():
    return flask.jsonify({
        'success': True
    }), 200

@app.route('/urlinfo/1/<path:host>/<path:path>', methods=['GET'])
def urlinfo_1(host, path):
    # Get DB cursor
    try:
        cursor = db.get_read_cursor()
    except Exception as ex:
        print('ERROR: Unable to connect to database! Reason: {}'.format(str(ex)), flush=True)
        return flask.jsonify({
            'success': False,
            'reason': 'Unable to connect to the database!'
        }), 200

    # Validate host & path fields
    valid, reason = validate_host(host)
    if not valid:
        return flask.jsonify({
            'success': False,
            'reason': reason
        }), 200
    valid, reason = validate_path(host, path)
    if not valid:
        return flask.jsonify({
            'success': False,
            'reason': reason
        })

    # Query DB for details on host/path
    output, data = get_url(cursor, host, path)

    # Return results
    if output == 'FOUND':
        return flask.jsonify({
            'success': True,
            'data': {
                'found': True,
                'is_safe': data
            }
        }), 200
    elif output == 'NOT_FOUND':
        return flask.jsonify({
            'success': True,
            'data': {
                'found': False
            }
        }), 200
    else:
        return flask.jsonify({
            'success': False,
            'reason': data
        }), 200

@app.route('/urladd/1', methods=['POST'])
def urladd_1():
    # Get DB cursor
    try:
        cursor = db.get_write_cursor()
    except Exception as ex:
        print('ERROR: Unable to connect to database! Reason: {}'.format(str(ex)), flush=True)
        return flask.jsonify({
            'success': False,
            'reason': 'Unable to connect to the database!'
        }), 200

    data = flask.request.get_json(force=True)['data']

    # Validate data
    invalid_host = False
    invalid_path = False
    for row in data:
        #print(row, flush=True)
        valid, output = validate_host(row[0])
        if not valid:
            print('Invalid host: {}'.format(row[0]), flush=True)
            invalid_host = True
        valid, output = validate_path(row[0], row[1])
        if not valid:
            print('Invalid path: {}'.format(row[1]), flush=True)
            invalid_path = True
    if invalid_host:
        return flask.jsonify({
            'success': False,
            'reason': 'One of the hostnames is invalid!'
        }), 200
    elif invalid_path:
        return flask.jsonify({
            'success': False,
            'reason': 'One of the paths is invalid!'
        }), 200

    # Import data
    try:
        cursor.execute('SELECT id FROM hosts;')
        hosts = [row[0] for row in cursor.fetchall()]
        for row in data:
            #print(row[0], row[1], flush=True)
            if row[0].lower() not in hosts:
                cursor.execute('INSERT INTO hosts (host) VALUES (%s);', (row[0].lower(), ))
                hosts.append(row[0].lower())
            cursor.execute('INSERT INTO paths (hosts_id, "url", is_safe) VALUES ((SELECT id FROM hosts WHERE host = %s), %s, FALSE);', (row[0].lower(), row[1].lower()))
        db.write_con.commit()

        return flask.jsonify({
            'success': True
        }), 200
    except Exception as ex:
        print('ERROR: Unable to add data to the database! Reason: {}'.format(str(ex)), flush=True)
        return flask.jsonify({
            'success': False,
            'reason': 'Unable to add data to the database!'
        }), 200

# Main
db = DB()
if __name__ == "__main__":
    print('Starting API endpoint...', flush=True)
    app.run(host='0.0.0.0', port=5000)
