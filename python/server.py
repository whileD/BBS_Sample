from flask import Flask, render_template, request, redirect, url_for, g
import sqlite3

app = Flask(__name__)

DB_NAME = 'threads.db'

# database
def get_db():
    db = getattr(g, '_database', None)
    if db is None: 
        db = g._database = sqlite3.connect(DB_NAME)
    db.row_factory = make_dicts
    return db


@app.teardown_appcontext
def close_connection(exeption):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value) for idx, value in enumerate(row))


# index page
@app.route('/')
def index():
    cur = get_db().cursor()
    rows = cur.execute('select * from threads')
    return render_template('index.html', threads=rows)


# create thread
@app.route('/new_thread', methods=['POST'])
def new_thread():
    db = get_db()
    cur = db.cursor()

    # 同じスレッドがあるなら処理をやめる
    for row in cur.execute('select * from threads'):
        if row['name'] == request.form['new-thread-name']:
            return redirect(url_for('index'))

    cur.execute('insert into threads(name) values(?)', (request.form['new-thread-name'], ))
    new_thread = cur.execute('select * from threads where name=?', 
            (request.form['new-thread-name'], )).fetchone()

    cur.execute('insert into thread_responses values(?, ?, ?, ?)', 
            (new_thread['id'], 1, request.form['new-response'], request.form['new-username']))

    db.commit()
    return redirect(url_for('index'))


@app.route('/thread/<int:thread_id>')
def thread(thread_id):
    cur =  get_db().cursor()
    thread = cur.execute('select * from threads where id=?', (thread_id,)).fetchone()
    responses = cur.execute('select * from thread_responses where thread_id=? order by response_number', (thread_id, ))
    return render_template('thread.html', thread_info=thread, responses=responses)


@app.route('/res/<int:thread_id>', methods=['POST'])
def write_response(thread_id):
    db = get_db()
    cur = db.cursor()
    next_resnum = cur.execute('select response_number from thread_responses where thread_id=? and response_number=(select max(response_number) from thread_responses where thread_id=?)',(thread_id,thread_id )).fetchone()['response_number'] + 1
    cur.execute('insert into thread_responses values(?, ?, ?, ?)', 
            (thread_id, next_resnum, request.form['response-response'], request.form['response-username']))

    db.commit()
    return redirect(url_for('thread', thread_id=thread_id))
    

if __name__ == '__main__':
    app.run(port=8000, debug=True)
