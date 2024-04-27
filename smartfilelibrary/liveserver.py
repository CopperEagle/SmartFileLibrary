"""Provides the REST server for the webinterface."""
import os
import sys
import signal
from getpass import getpass
from flask import Flask, request, jsonify

from .databaseinterface import DatabaseInterface
 
app = Flask(__name__)


def get_argument(arg : str):
    """Get argument from the most recent request. 
    Returns empty string if not available.

    Parameter
    ----------
    arg : str
        The argument from the request.
    """
    query = None
    try:
        query = request.args.get(arg)
    except:
        pass
    query = "" if query is None else query
    return query

@app.after_request
def add_header(response):
    """Add CORS header."""
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/status')
def get_status():
    """Send status."""
    return jsonify({"status":"running"})

@app.route('/dbmeta')
def get_dbmeta():
    """Get metadata about the library. So far, it only accepts
    ?key=user to return the username."""
    global db
    if get_argument("key") == "user":
        return jsonify(db.get_username())

@app.route('/turnoff')
def shutdown():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        os.kill(os.getpid(), signal.SIGINT)
    else:
        func()
    return ""


@app.route('/set_fav')
def set_fav():
    """
    Update the favourite status using the web interface.
    Done as GET method for convenience.
    """
    global db
    fav = get_argument("val")
    bid = get_argument("id")
    value = "false"
    if fav == "1":
        value = "true"
    db.execute(
        f"""UPDATE Book
        SET favorite = {value}
        WHERE book_id = {bid};"""
        )
    return ""


@app.route('/query')
def query_db():
    """Query main entry point."""
    global db # need to be explicit with flask
    query = get_argument("kw")
    form = get_argument("form")
    
    if form == "all":
        res = db.execute(
            """SELECT book_id, title, name, favorite 
            FROM Book JOIN Publisher USING(pub_id);"""
            )
    else:
        res = db.execute(
            f"""SELECT book_id, title, name, favorite 
            FROM Book 
            JOIN Publisher USING(pub_id)
            JOIN Form USING(form_id)
            WHERE form_name = '{form}';"""
            )
    ret = []
    for bid, title, pubname, fav in res:
        res = db.execute(
            f"""SELECT topic_name FROM book_topic WHERE book_id = {int(bid)};"""
        )
        tps = [i[0] for i in res]
        tpscheck = [i[0].lower() for i in res]
        if query.lower() not in tpscheck and query != "*":
            continue

        ret.append(
            {
            "id" : bid,
            "title" : title,
            "author" : ("published by " + pubname).title(),
            "keywords" : tps,
            "favourite" : fav
            })

    if ret == []:
        ret = [{"title" : "Could not find any matches.",
            "author" : "",
            "keywords" : [],
            "favourite" : False
            }]
    return jsonify(ret)


def main():
    """Main loop for the server."""
    global db
    if len(sys.argv) != 3:
        print("[Error] liveserver.py expects arguments db_name, user_name")
        quit()
    pw = getpass("Please enter the password for the DB: ")
    db = DatabaseInterface(sys.argv[1], sys.argv[2], pw)
 
    app.run()

