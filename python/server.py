from flask import Flask, render_template, request, redirect, url_for
import os
import csv
import fcntl

app = Flask(__name__)
THREADS_DIRECTORY = 'threads/'

#csvファイルを読みこんでname,resのkey辞書型リストで返す
def thread_loader(file_name):
    with open(THREADS_DIRECTORY + file_name, 'r') as target:
        fcntl.flock(target, fcntl.LOCK_EX)
        reader = csv.DictReader(target, fieldnames=['name', 'res'])
        return [row for row in reader]


@app.route('/')
def index():
    threads = os.listdir(THREADS_DIRECTORY)
    return render_template('index.html', threads=['a', 'b'])


@app.route('/thread/<string:thread_name>')
def thread(thread_name):
    data = thread_loader(thread_name)
    return render_template('thread.html', title=thread_name, thread_name=thread_name, data=data)


@app.route('/res/<string:thread_name>', methods=['POST'])
def write_response(thread_name):
    with open(THREADS_DIRECTORY + thread_name, 'a') as target:
        fcntl.flock(target, fcntl.LOCK_EX)
        res = [request.form['response-username'], request.form['response-response']]
        target.writelines(','.join(res) + '\n')

    return redirect(url_for('thread', thread_name=thread_name))


@app.route('/newThread', methods=['POST'])
def new_thread():
    with open(THREADS_DIRECTORY + request.form['new-thread-name'], 'w') as target:
        fcntl.flock(target,fcntl.LOCK_EX)
        newdata = [request.form['new-username'], request.form['new-response']]
        target.writelines(','.join(newdata) + '\n')

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(port=8000, debug=True)
