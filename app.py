from flask import Flask, render_template, request
from pymysql import connections
import boto3
from config import *

app = Flask(__name__)

# MySQL configurations
# RDS_HOST = 'your_rds_host'
# RDS_PORT = 3306
# RDS_USER = 'your_rds_user'
# RDS_PASSWORD = 'your_rds_password'
# RDS_DB_NAME = 'your_rds_db_name'

# Initialize Boto3 DynamoDB client
dynamodb = boto3.client('dynamodb')

# Initialize RDS database connection
db_conn = connections.Connection(
    host=databasehost,
    port=3306,
    user=duser,
    password=dpass,
    db=s3database
)

def query_employee_data(employee_id):
    try:
        # Connect to the RDS database
        connection = connections.Connection(
            host=databasehost,
            port=3306,
            user=duser,
            password=dpass,
            db=s3database,
            cursorclass=connections.DictCursor
        )

        with connection.cursor() as cursor:
            # Query the employee data using employee ID
            sql = "SELECT * FROM intellipaattable WHERE id = %s"
            cursor.execute(sql, (employee_id,))
            employee_data = cursor.fetchone()

        return employee_data

    except Exception as e:
        # Handle any errors
        print(f"Error: {e}")
        return None

@app.route("/", methods=['GET', 'POST'])
def hello_world():
    if request.method == 'POST':
        name = request.form['name']
        location = request.form['location']
        age = request.form['age']
        technology = request.form['technology']

        # Upload file to S3
        s3 = boto3.resource('s3')
        # s3 = boto3.resource(service_name='s3', region_name='us-east-1', aws_access_key_id=key_id, aws_secret_access_key=access_key)
        file_body = request.files['file_name']
        file_name = file_body.filename
        count_obj = 0
        for i in s3.Bucket(custombucket).objects.all():
            count_obj = count_obj + 1
        file_name = "file-id-" + str(count_obj + 1)

        try:
            s3.Bucket(custombucket).put_object(Key=file_name, Body=file_body)
            print("File uploaded to S3 successfully !")
        except Exception as e:
            return str(e)

        try:
            # Upload data to RDS
            cursor = db_conn.cursor()
            insert_sql = "INSERT INTO intellipaattable VALUES (%s,%s,%s,%s)"
            cursor.execute(insert_sql, (name, location, age, technology))
            db_conn.commit()
            print("Data uploaded to RDS successfully !")
        except Exception as e:
            print(str(e))
            return str(e)

        try:
            # Upload user data to DynamoDB
            dynamodb.put_item(
                TableName=dynamoDB_table,
                Item={
                    'filename': {'S': file_name},
                    'Author': {'S': name}
                },
                ConditionExpression='attribute_not_exists(filename)'
            )
            print("File uploaded to DynamoDB successfully !")
        except Exception as e:
            return str(e)

    return render_template("index.html")

@app.route("/employee", methods=['GET', 'POST'])
def get_employee():
    if request.method == 'POST':
        employee_id = request.form['employee_id']
        employee_data = query_employee_data(employee_id)

        if employee_data:
            return render_template('employee_details.html', employee=employee_data)
        else:
            return render_template('error.html', message="Employee not found")

    return render_template('employee_form.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
