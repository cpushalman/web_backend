from flask import Flask, request, redirect
from pymongo import MongoClient
from datetime import datetime

app=Flask(__name__)

client=MongoClient('mongodb://localhost:27017/')
db=client['shortly']
collection=db['urls']

@app.route('/<short>')
def redirect_to(short):
    url=collection.find_one({'shortened_url':short})
    if url:
        collection.update_one({'shortened_url':short},
        {   
            '$inc':{'clicks':1},
            '$push':{'timestamps':datetime.utcnow()}
        })
        return redirect(url['long_url'])
    return "URL not found",404

if __name__=='__main__':
    app.run(debug=True)
