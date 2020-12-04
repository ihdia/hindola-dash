#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct  1 00:50:04 2020

@author: khadiravana.belagavi
"""
import mysql.connector
import operator
import numpy as np

def getmydb():
    return mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",
    port="2000",
    database="annotation_web"
 )

# Annotators
def getUsers():
    mydb = getmydb()
    mycursor = mydb.cursor()
     
    mycursor.execute('Select distinct username From info;')
    users = []
    for x in mycursor:
        if x[0].lower() not in users:
            users.append(x[0])
    return users

def getRawUsers():
    mydb = getmydb()
    mycursor = mydb.cursor()
     
    mycursor.execute('Select distinct username From info;')
    users = []
    for x in mycursor:
        if x[0] not in users:
            users.append(x[0])
    return users


def get_num_users():
    return len(getUsers())

def user_annot_info(username):
    """
    

    Parameters
    ----------
    username : TYPE
        DESCRIPTION.

    Returns : 
    -------
    annot_info : TYPE
        DESCRIPTION.

    """
    mydb = getmydb()
    mycursor = mydb.cursor()
    status_types = ['annotated','undone','skipped']
    annot_info = {'annotated':0,'served':0}
    
    for status in status_types:
        command = 'Select Count(file) from info Where username= %s  and status = %s;'
        args = (username,status)
         
        mycursor.execute(command,args)
        for x in mycursor:
            if status == 'annotated':

                annot_info[status]= x[0]
                annot_info['served'] += x[0]
            else:
                annot_info['served'] += x[0]
    return annot_info

def all_users_info():
    raw_users = getRawUsers()
    users_info_annotated = {}
    users_info_served = {}
    for user in raw_users:
        info_dict = user_annot_info(user)
        userl = user.lower()
        if userl not in users_info_annotated:
            users_info_annotated[userl] = info_dict['annotated']
        else:
            users_info_annotated[userl] += info_dict['annotated']
        if userl not in users_info_served:
            users_info_served[userl] = info_dict['served']
        else:
            users_info_served[userl] += info_dict['served']
    return users_info_annotated , users_info_served
        
    
def count_ind_collections():
    """
    Returns
    -------
    collection_ind_count : TYPE
        DESCRIPTION.
     Function returns a dictionary with keys as collections and 
     values as their corresponding count in the database (Note: This is 
    not filtering based on whether annotated or not annotated.)
    """
    mydb = getmydb()
    mycursor = mydb.cursor()
     
    command = 'Select count(*),SUBSTRING(file,1,POSITION("-" in file)-1) AS sub from imagelinks GROUP BY sub;'
    collection_ind_count = {}
    mycursor.execute(command)
    result = mycursor.fetchall()
    for x in result:
        collection_ind_count[x[1]] = x[0]
    return collection_ind_count
        
def count_ind_completion():
    """
    

    Returns : number of annotated collections
    -------
    ind_comp_count : TYPE
        DESCRIPTION.

    """
    mydb = getmydb()
    mycursor = mydb.cursor()
    
    command = 'Select count(*),SUBSTRING(Filename,1,POSITION("-" in FILENAME)-1) AS sub from json_v2 GROUP BY sub;'
    ind_comp_count = {}
    mycursor.execute(command)
    result = mycursor.fetchall()
    for x in result:
        ind_comp_count[x[1]] = x[0]
    output = {}
    sorted_x = sorted(ind_comp_count.items(), key=lambda kv: kv[1],reverse=True)
    for key,value in sorted_x:
        output[key] = value
    if len(output) == 0:
        output = count_ind_collections()
        output = {x:0 for x in output}
    collectionS = count_ind_collections().keys()
    for coll in collectionS:
        if coll not in output:
            output[coll]=0
    return output

def detailed_count_collections():
    """
    Returns : Distribution of total collection for each book under each collection
    -------
    detailed_count : Dictionary of dictionaries
        DESCRIPTION.
    """
    detailed_count = {}
    mydb = getmydb()
    mycursor = mydb.cursor()
     
    command = "Select * from imagelinks"
    mycursor.execute(command)
    result = mycursor.fetchall()
    
    for detail in result:
        collection = detail[0].split('-')[0]
        book = detail[1].split('/')[5]
        if collection not in detailed_count:
            detailed_count[collection] = {}
        if book not in detailed_count[collection]:
            detailed_count[collection][book]=0
        detailed_count[collection][book]+=1
    # sorted_x = sorted(detailed_count.items(), key=lambda kv: kv[1])
    sorted_x = sorted(detailed_count.items(), key=operator.itemgetter(0))
    output = {}
    for collection in detailed_count:
        sorted_x = sorted(detailed_count[collection].items(), key=lambda kv: kv[1],reverse=True)
        for key,value in sorted_x:
            if collection not in output:
                output[collection] = {}
            output[collection][key] = value
    return output


def detailed_annot_count():
    """
    Returns : Number of annotated at book level for each collection
    -------
    detailed_annot_count : TYPE
        DESCRIPTION.

    """
    detailed_annot_count = {}
    mydb = getmydb()
    mycursor = mydb.cursor()
     
    command = "Select filename,fileurl from json_v2"
    mycursor.execute(command)
    result = mycursor.fetchall()
    
    for detail in result:
        collection = detail[0].split('-')[0]
        book = detail[1].split('/')[3]
        if collection not in detailed_annot_count:
            detailed_annot_count[collection] = {}
        if book not in detailed_annot_count[collection]:
            detailed_annot_count[collection][book]=0
        detailed_annot_count[collection][book]+=1
    return detailed_annot_count
    
# print(detailed_annot_count())

# book_db_details = detailed_count_collections()
# book_db_annotated = detailed_annot_count()
# annotated = {}
# for collection in book_db_details:
#     annotated[collection] = {}
#     for book in book_db_details[collection]:
#         try:
#             annotated[collection][book] = book_db_annotated[collection][book]
#         except:
#             annotated[collection][book] = 0
# # print(annotated)
# # print(book_db_details)
# book_not_annotated = {}
# for collection in book_db_details:
#     book_not_annotated[collection] = {}
#     for book in book_db_details[collection]:
#         book_not_annotated[collection][book] = book_db_details[collection][book] - annotated[collection][book]
# print(book_not_annotated)
# {'bhoomi':{'bkk'}}
def collection_percentage():
    datailed_db_total = detailed_count_collections()
    detailed_annot_total = detailed_annot_count()
    no_collections_completed = 0
    for collection in detailed_annot_total:
        annotated_books = detailed_annot_total[collection]
        completed = True
        for book in annotated_books:
            if annotated_books[book]!=datailed_db_total[collection][book]:
                completed = False
                break
        if completed:
            no_collections_completed+=1
    total_no_collections = len(datailed_db_total)
    return (no_collections_completed/total_no_collections)*100

def book_percentage():
    datailed_db_total = detailed_count_collections()
    detailed_annot_total = detailed_annot_count()
    no_books_completed = 0
    num_books_total = 0
    for collection in detailed_annot_total:
        annotated_books = detailed_annot_total[collection]
        # completed = True
        for book in annotated_books:
            if annotated_books[book]==datailed_db_total[collection][book]:
                no_books_completed+=1
    for collection in datailed_db_total:
        num_books_total+= len(datailed_db_total[collection])
    return np.ceil((no_books_completed/num_books_total)*100)

def page_percentage():
    datailed_db_total = detailed_count_collections()
    detailed_annot_total = detailed_annot_count()
    no_pages_completed = 0
    num_pages_total = 0
    for collection in detailed_annot_total:
        annotated_books = detailed_annot_total[collection]
        # completed = True
        for book in annotated_books:
            no_pages_completed+=annotated_books[book]
    for collection in datailed_db_total:
        for book in datailed_db_total[collection]:
            num_pages_total+= datailed_db_total[collection][book]
    return np.ceil((no_pages_completed/num_pages_total)*100)

def get_db_stats():
    db_details = detailed_count_collections()
    num_collections = len(db_details)
    num_books = 0
    num_pages = 0
    for collection in db_details:
        num_books+=len(db_details[collection])
        for book in db_details[collection]:
            num_pages+=db_details[collection][book]

    return num_collections , num_books , num_pages
# def get_num_books():

def get_collection_names():
    return list(count_ind_collections().keys())

def get_only_books(collection):
    db_details = detailed_count_collections()
    return db_details[collection]

def get_pages_annotated():
    db_annot_details = detailed_annot_count()
    num_pages = 0
    for collection in db_annot_details:
        for book in db_annot_details[collection]:
            num_pages+=db_annot_details[collection][book]
    return num_pages

# print(len(getUsers()))
def collectionCountAnnot():
    
    datailed_db_total = detailed_count_collections()
    detailed_annot_total = detailed_annot_count()
    no_collections_completed = 0
    for collection in detailed_annot_total:
        annotated_books = detailed_annot_total[collection]
        completed = True
        for book in annotated_books:
            if annotated_books[book]!=datailed_db_total[collection][book]:
                completed = False
                break
        if completed:
            no_collections_completed+=1
    total_no_collections = len(datailed_db_total)
    return no_collections_completed

def bookCountAnnot():
    datailed_db_total = detailed_count_collections()
    detailed_annot_total = detailed_annot_count()
    no_books_completed = 0
    num_books_total = 0
    for collection in detailed_annot_total:
        annotated_books = detailed_annot_total[collection]
        # completed = True
        for book in annotated_books:
            if annotated_books[book]==datailed_db_total[collection][book]:
                no_books_completed+=1
    for collection in datailed_db_total:
        num_books_total+= len(datailed_db_total[collection])
    return no_books_completed

def pagesPercentage():
    datailed_db_total = detailed_count_collections()
    detailed_annot_total = detailed_annot_count()
    no_pages_completed = 0
    num_pages_total = 0
    for collection in detailed_annot_total:
        annotated_books = detailed_annot_total[collection]
        # completed = True
        for book in annotated_books:
            no_pages_completed+=annotated_books[book]
    for collection in datailed_db_total:
        for book in datailed_db_total[collection]:
            num_pages_total+= datailed_db_total[collection][book]
    return no_pages_completed

def users_annot_count():
    mydb = getmydb()
    mycursor = mydb.cursor()

    command = 'select count(*) from info where status = "annotated"'
     
    
    mycursor.execute(command)
    result =  mycursor.fetchone()
    return result

def check_reviewed(url):

    mydb = getmydb()
    mycursor = mydb.cursor()

    final_url = '/'.join(url.split('/')[2:])
    command = "select reviewed from json_v2 where fileurl='{}'".format(final_url)
    
      
    mycursor.execute(command)
    result = mycursor.fetchone()

    return result

def get_document_by_date():
    mydb = getmydb()
    mycursor = mydb.cursor()

    command = 'select localurl from info where status = "annotated" order by date desc '
    
     
    mycursor.execute(command)
    docs = []
    for x in mycursor:
        if x[0].lower() not in docs:
            docs.append(x[0])
    return docs

def accept_image_annotation(fileurl):
    mydb = getmydb()
    mycursor = mydb.cursor()
    fileurl = "/".join(fileurl.split("/")[2:])
     
    command = "UPDATE json_v2 SET reviewed=1 where fileurl = '{}'".format(fileurl)
    # sql = '''UPDATE json_v2 SET reviewed=NULL where fileurl = 'static/imgdata/Bhoomi_data/ANINGYA VYAKHYA/SVUORI/4378/14.jpg''''
    # print(command)
    # args = (fileurl)
        
    mycursor.execute(command)
    mydb.commit()

def reject_image_annotation(fileurl):
    mydb = getmydb()
    mycursor = mydb.cursor()
    fileurl = "/".join(fileurl.split("/")[2:])
     
    command = "UPDATE json_v2 SET reviewed=-1 where fileurl = '{}'".format(fileurl)
    # sql = '''UPDATE json_v2 SET reviewed=NULL where fileurl = 'static/imgdata/Bhoomi_data/ANINGYA VYAKHYA/SVUORI/4378/14.jpg''''
    # print(command)
        
    mycursor.execute(command)
    mydb.commit()

def reviewed_image_annotation(fileurl):
    mydb = getmydb()
    mycursor = mydb.cursor()
    fileurl = "/".join(fileurl.split("/")[2:])
     
    command = "UPDATE json_v2 SET reviewed=0 where fileurl = '{}'".format(fileurl)
    # sql = '''UPDATE json_v2 SET reviewed=NULL where fileurl = 'static/imgdata/Bhoomi_data/ANINGYA VYAKHYA/SVUORI/4378/14.jpg''''
    # print(command)
            
    mycursor.execute(command)
    mydb.commit()    

'''
reviewing system:

NULL - not reviewed
-1 - rejected
0 - reviewed but not approved
1 - accepted
'''
