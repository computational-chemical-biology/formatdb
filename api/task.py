import celery
import os
from api.formatdb import *
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os
import bz2

#app.conf.update(BROKER_URL='redis://localhost:6379/0',
#                CELERY_RESULT_BACKEND='redis://localhost:6379/0')


app = celery.Celery('tasks', backend='redis://redis:6379/0',
                broker='redis://redis:6379/0')

psswd = b''

@app.task
def longtask(inputfile, email, tool):
    fls = os.path.join('/formatdb_flask/api/tmp', inputfile)
    try:
        formated = formatdb(fls, tool)
        server = smtplib.SMTP('smtp.gmail.com', 587)
	#server.starttls()
        server.connect("smtp.gmail.com",587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login("rsilvabioinfo@gmail.com", bz2.decompress(psswd).decode("utf-8"))

        msg = MIMEMultipart()
        msg['From'] = 'rsilvabioinfo@gmail.com'
        msg['To'] = email
        msg['Subject'] = 'Conversion from NAP'

        text = ("Your data is available for download here:\n"+
                "http://seriema.fcfrp.usp.br:5002/download/"+inputfile+"\n"+
                "WARNING: the data will be available for a single download.")
        part1 = MIMEText(text, 'plain')
        msg.attach(part1)
        server.sendmail("rsilvabioinfo@gmail.com", email, msg.as_string())
        server.quit()
    except Exception as exc:
        server = smtplib.SMTP('smtp.gmail.com', 587)
	#server.starttls()
        server.connect("smtp.gmail.com",587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login("rsilvabioinfo@gmail.com", bz2.decompress(psswd).decode("utf-8"))

        msg = MIMEMultipart()
        msg['From'] = 'rsilvabioinfo@gmail.com'
        msg['To'] = email
        msg['Subject'] = 'Conversion from NAP'

        formated = 'FAIL'
        text = ("Your task appear to have failed here is the error:\n"+
              str(exc)+'\n'+
              "If you are unable to understant the error reply this email.")
        part1 = MIMEText(text, 'plain')
        msg.attach(part1)
        server.sendmail("rsilvabioinfo@gmail.com", email, msg.as_string())
        server.quit()
    return formated




