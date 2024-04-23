from flask import Flask, render_template, request, make_response
from werkzeug import secure_filename
import pandas as pd
from celery import uuid
#import uuid
from celery.result import AsyncResult
import os

from api import task

app = Flask(__name__)
app.secret_key = 'alura'

@app.route('/upload')
def upload_temp():
   return render_template('upload.html')

@app.route('/uploader', methods = ['GET', 'POST'])
def upload_file():
   if request.method == 'POST':
      f = request.files['file']
      result = request.form
      email = result['email']
      tool = result['tool']
      oformat = result['oformat']
      #file = request.files.get('file')
      #df = pd.read_table(file)
      task_id = uuid()
      #task_id = str(uuid.uuid4())
      fls = os.path.join('/formatdb_flask/api/tmp', task_id)
      #f.save(secure_filename(fls))
      f.save(fls)
      #print(task_id)
      df = task.longtask.apply_async(args=[task_id, email, tool, oformat], task_id=task_id)
      #df = task.longtask.delay(task_id)
      #print(df.status)
      #print(df.task_id)
      #df.wait()
      return ('This is your task id: ' + task_id + '\n' +
              'You should receive an email with a download link soon')

@app.route('/download/<task_id>')
def download(task_id):
      fls = os.path.join('/formatdb_flask/api/tmp', task_id+'_FORMATED.txt')
      df = pd.read_csv(fls,  sep='\t')
      os.remove(fls)
      resp = make_response(df.to_csv(sep='\t', index=None))
      resp.headers["Content-Disposition"] = "attachment; filename=formatted.tsv"
      resp.headers["Content-Type"] = "text/tsv"
      return resp

@app.route('/status/<task_id>')
def status(task_id):
    res = AsyncResult(task_id)
    return res.status

if __name__ == '__main__':
    #app.run(debug = True)
    app.run(port=5002, debug = True)
