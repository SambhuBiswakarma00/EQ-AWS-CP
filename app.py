from flask import Flask
from flask import render_template
from flask import request
import boto3
from pymysql import connections
import urllib.request
from config import *
app = Flask(__name__)
db_conn = connections.Connection(
    host=databasehost,
    port=3306,
    user=duser,
    password=dpass,
    db=s3database

)


@app.route("/", methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        age = request.form['age']
        technology = request.form['technology']
        # s3 = boto3.resource('s3')
        s3 = boto3.resource(service_name='s3',region_name='us-east-1',aws_access_key_id=key_id,aws_secret_access_key=access_key)
        file_body = request.files['file_name']
        file_name = file_body.filename
        count_obj = 0
        for i in s3.Bucket(custombucket).objects.all():
            count_obj = count_obj + 1
        file_name = "file-id-" + str(count_obj + 1)
        # print("inside first for")

        try:
            s3.Bucket(custombucket).put_object(Key=file_name, Body=file_body)
            # print("after obj upload")
            # bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            # # bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)['LocationConstraint']
            # print("after bucket location extraction")
            # s3_location = (bucket_location['LocationConstraint'])
            # print("inside first try")

            # if s3_location is None:
            #     s3_location = ''
            # else:
            #     s3_location = '-' + s3_location

            # object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
            #     s3_location,
            #     custombucket,
            #     file_name)

            try:
                pass
                # cursor = db_conn.cursor()
                # insert_sql = "INSERT INTO intellipaat VALUES (%s, %s)"
                # cursor.execute(insert_sql, (file_name, object_url))
                # db_conn.commit()
                cursor = db_conn.cursor()
                # print("cursor")
                insert_sql = "INSERT INTO intellipaattab VALUES (%s)"
                cursor.execute(insert_sql, (file_name))
                # print("cursor exe")
                db_conn.commit()
                # print("inside second try")

            except Exception as e:
                print(str(e))
                return str(e)

        except Exception as e:
            # print(str(e))
            return str(e)
    print("Uploading to S3 success... ")
    return render_template("index.html")


# @app.route("/check", methods=['GET', 'POST'])
# def hello():
#     try:
#         statuscode = urllib.request.urlopen(kapp).getcode()
#         if statuscode == 200:
#             return "<h1>Cluster is up!</h1>"
#     except Exception as e:
#         return "<h1>Cluster is not up!</h1>"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
