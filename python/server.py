from flask import Flask, render_template, request, redirect, url_for
import os
import csv
import fcntl

app = Flask(__name__)
threadsDir = 'threads/'
fields = ['name', 'res']


def threadLoader(file_name):
    with open(threadsDir + file_name, 'r') as csvfile:
        fcntl.flock(csvfile,fcntl.LOCK_EX)
        reader = csv.DictReader(csvfile, fieldnames=fields)
        return [row for row in reader]


@app.route('/')
def index():
    threads = os.listdir(threadsDir)
    return render_template('index.html', threads=threads)

@app.route('/thread/<string:thread_name>')
def thread(thread_name):
    data = threadLoader(thread_name)
    return render_template('thread.html', 
            title=thread_name, thname=thread_name, data=data)

@app.route('/res/<string:thread_name>', methods=['POST'])
def writeResponse(thread_name):
    with open(threadsDir + thread_name, 'a') as target:
        fcntl.flock(target,fcntl.LOCK_EX)
        addstr = [request.form['name'], request.form['res']]
        target.writelines(','.join(addstr) + '\n')

    return redirect(url_for('thread', thread_name=thread_name))

@app.route('/newThread', methods=['POST'])
def newThread():
    with open(threadsDir + request.form['thread_name'], 'w') as th:
        fcntl.flock(th,fcntl.LOCK_EX)
        target = [request.form['thread_resname'], request.form['thread_res']]
        th.writelines(','.join(target) + '\n')

    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(port=8000, debug=True)
