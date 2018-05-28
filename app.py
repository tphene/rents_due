from flask import Flask,render_template,request
import os
import boto
import boto.s3
import sys
from boto.s3.key import Key
from boto3.session import Session
app = Flask(__name__)

APP_ROOT = os.path.dirname(os.path.abspath(__file__))

AWS_ACCESS_KEY_ID = 'AKIAIRLADU53Z2ZGFKFQ'
AWS_SECRET_ACCESS_KEY = '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'

# bucket_name = AWS_ACCESS_KEY_ID.lower() + '-dump'

bucket_name = 'test-toshal'
conn = boto.connect_s3(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY)


bucket = conn.get_bucket(bucket_name)
session = Session(aws_access_key_id=AWS_ACCESS_KEY_ID,aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
s3 = session.resource('s3')
bucket1 = s3.Bucket(bucket_name)

content = []
for i in bucket1.objects.all():
	content.append(i.key)

def percent_cb(complete, total):
    sys.stdout.write('.')
    sys.stdout.flush()


@app.route('/')
def index():
	return render_template('upload.html')

@app.route("/upload", methods=['POST'])
def upload():
	target = os.path.join(APP_ROOT, 'images/')
	print(target)

	if not os.path.isdir(target):
		os.mkdir(target)

	print(content)
	#print(bucket_name)
	#print(request.files.getlist("file"))
	for file in request.files.getlist("file"):
		# print(file)
		filename = file.filename
		destination = "/".join([target, filename])
		# print('filename'+filename)
		k = Key(bucket)
		k.key = filename
		if(filename in content):
			print('Change name')
		# file.save(destination)
		k.set_contents_from_filename(destination,cb=percent_cb,num_cb=10)
	return render_template("complete.html")

if(__name__=='__main__'):
	app.run(debug=True)
