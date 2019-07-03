from bottle import route, request, response, run, template, static_file
import os, uuid 
import redis
import json

import tempfile

import logging

log = logging.getLogger()
log.setLevel('DEBUG')
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
log.addHandler(handler)

from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement

KEYSPACE = "keyspacehw3"
session = None

#Cassandra running carpetshark
def cassandraGetSession(host = '#add your machineupip'):
    global session
    cluster = Cluster([host], port=9054)

    if session is not None:
        return session

    try:
        session = cluster.connect()
        log.info("Cassandra session connected successfully ")
    
        rows = session.execute("SELECT keyspace_name FROM system.schema_keyspaces")
        
        log.info("creating keyspace...")
        session.execute("""
            CREATE KEYSPACE IF NOT EXISTS %s
            WITH replication = { 'class': 'SimpleStrategy', 'replication_factor': '2' }
            """ % KEYSPACE)
        log.info("setting keyspace...")
        session.set_keyspace(KEYSPACE)  

        log.info("creating table...")
        session.execute("""
            CREATE TABLE IF NOT EXISTS FILE_ID_MAP (
                fname text,
                file blob,
                PRIMARY KEY (fname)
            ) WITH caching = { 'keys' : 'NONE', 'rows_per_partition' : '120' };
            """)

    except Exception:
        log.exception("bad things happened")

    return session

def cassandraInsertFile(session, fname, file_binaryObject):

    session.execute("INSERT INTO FILE_ID_MAP (fname, file) VALUES (%s, %s)", (fname,\
            file_binaryObject))
    log.info("Inserted the file %s", fname)

    return

def cassandraRetriveFile(session, fname):

    file_byte_array = session.execute("SELECT file FROM file_id_map WHERE fname='"+str(fname)+"'")
    return file_byte_array

@route('/')
def index():
    return static_file('up.html', root='./')

@route('/cassandrastore1/<fname>', method='POST')
@route('/cassandrastore1/<fname>', method='GET')
def do_download(fname):
    file_byte_array = cassandraRetriveFile(session, fname)
    filedata = file_byte_array[0].file
    print("Coming here")
    print(type(filedata))
    b = bytearray()
    b.extend(filedata)

    temp = tempfile.TemporaryFile().write(filedata)

    #return static_file(temp, as_attachment=True, 
    #                 attachment_filename=fname)

    response.set_header('Content-Disposition', "attachment; filename=" + fname)
    return filedata

@route('/request_url', method='POST')
@route('/request_url', method='GET')
def request_url():
    fname = request.query.fname
    # Get the url of the file from the haystack redis directory
    print fname
    # Running Redis in lemonshark
    r = redis.StrictRedis(host='#addyourmachineupip', port=6389, db=0)
    url = r.get(fname)
    if(url is not None):
        return url
    
    return 'No file'

@route('/upload', method='POST')
@route('/upload', method='GET')
def do_upload():
    global session
    upload = request.files.get('upload')
    if upload is None:
        return 'Please go back and Select a file to upload'
  
    if session is None:
        session = cassandraGetSession()

    upload = request.files.get('upload')
    fname = upload.filename
    name, ext = os.path.splitext(upload.filename)
    
    if ext not in ('.py', '.txt', '.c'):
        return 'Please upload text files so that we can render on the browser while download and complete the demo architecture'

    # Redis will act as Directory here
    # Redis running on lemonshark
    r = redis.StrictRedis(host='#addyourmachineupip', port=6389, db=0)
    
    # Store the filename and create url for the filename
    """Instead of CDN, we store the url of our server itself and also give the machineid
     as cassandrastore1 which will be mapped to the actual store address later and appended 
     with the filename which will be used as the key for cassandra
    """
    # Running NGINX in makoshark
    url = "##urlofcassandra" + upload.filename
    r.set(fname, url)

    # Insert the file into the Cassandra datastore
    res = bytearray(upload.file.read())
    cassandraInsertFile(session, fname, res)

    return 'Please use this filename for downloading the file later.\n File is stored succesfully with the filename: ' + fname


if __name__ == "__main__":
    if session is None:
        session = cassandraGetSession()
    # Running BottleServer angelshark
    run(host='##addbottleserverangelshark', port=8081)
