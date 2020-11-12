
import mysql.connector
import operator
import numpy as np

mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="root",
  port="3306",
  database="hindola"
)

def accept_image_annotation(fileurl):
    mycursor = mydb.cursor()
    command = "UPDATE json_v2 SET reviewed=1 where fileurl = 'static/imgdata/Bhoomi_data/ANINGYA VYAKHYA/SVUORI/4378/14.jpg'"
    # sql = '''UPDATE json_v2 SET reviewed=NULL where fileurl = 'static/imgdata/Bhoomi_data/ANINGYA VYAKHYA/SVUORI/4378/14.jpg''''
    print(command)
    # args = (fileurl)

    mycursor.execute(command)
    mydb.commit()

accept_image_annotation('static/imgdata/Bhoomi_data/ANINGYA VYAKHYA/SVUORI/4378/14.jpg')
