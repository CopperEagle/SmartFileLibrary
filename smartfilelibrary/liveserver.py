"""Provides the server for the webinterface."""
import sys
from getpass import getpass
from flask import Flask, request

from .databaseinterface import DatabaseInterface
 
app = Flask(__name__)

@app.after_request
def add_header(response):
    """Add CORS header."""
    response.headers['Access-Control-Allow-Origin'] = '*'
    return response

@app.route('/query')
def entry():
    """Query main entry point."""
    global db # need to be explicit with flask
    query = ""
    form = "all"
    try:
        query = request.args.get("kw")
    except:
        pass
    if query is None:
        query = ""

    res = db.execute(
        """SELECT book_id, title, name, favorite FROM Book JOIN Publisher USING(pub_id);"""
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
    return ret

def main():
    """Main loop for the server."""
    global db
    if len(sys.argv) != 3:
        print("[Error] liveserver.py expects arguments db_name, user_name")
        quit()
    pw = getpass("Please enter the password for the DB: ")
    db = DatabaseInterface(sys.argv[1], sys.argv[2], pw)
 
    app.run()

