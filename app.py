import os, copy, datetime
from libfeed import tinyfeed, storage
from flask import (Flask, render_template, url_for, request, redirect, jsonify)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(32)

#Storage facilities
dataobj = storage.DataStore(os.path.join('store', 'data.json'))
dataobj.initialize()

#RSS feed facilities
feedobj = tinyfeed.TinyFeed()

def latestvideos():
    marked = []
    sample = dataobj.needUpdate()
    if sample:
        updated = feedobj.processSources(sample, dataobj.storedict)
        dataobj.store(updated)
    datadict = copy.deepcopy(dataobj.storedict)
    for sourceID in datadict:
        newvideos = feedobj.filterEntries(datadict[sourceID]['entries'], 100)
        if not newvideos: marked.append(sourceID)
        else: datadict[sourceID]['entries'] = newvideos
    for sourceID in marked: del datadict[sourceID]
    return datadict

@app.context_processor
def ctxtprocessor():
    def fancyDate(datestr):
        return feedobj.formatDate(datestr)
    return {'fancyDate': fancyDate}

@app.errorhandler(Exception)
def error_handler(error):
    return jsonify({'success': False,
                    'details': '{}'.format(error),
                    'code': error.code if hasattr(error, 'code') else None
                    })

@app.route('/addfeed', methods = ['POST'])
def addfeed():
    temp = {}
    sourceID = request.args.get('sourceID')
    temp[sourceID] = feedobj.processSource(sourceID)
    dataobj.store(temp)
    return jsonify({'success': True})

@app.route('/remfeed', methods = ['POST'])
def remfeed():
    sourceID = request.args.get('sourceID')
    dataobj.delete(sourceID)
    return jsonify({'success': True})

@app.route('/update', methods = ['POST'])
def updatefeed():
    sourceID = request.args.get('sourceID')
    if sourceID == 'home':
        datadict = feedobj.processSources(dataobj.storedict.keys(), dataobj.storedict)
    else:
        datadict = {sourceID: feedobj.processSource(sourceID, dataobj.storedict)}
    dataobj.store(datadict)
    return jsonify({'success': True})

@app.route('/download', methods = ['POST'])
def downloadfeed():
    sourceID = request.args.get('sourceID')
    if sourceID == 'home':
        datadict = feedobj.processSources(dataobj.storedict.keys())
    else:
        datadict = {sourceID: feedobj.processSource(sourceID)}
    dataobj.store(datadict)
    return jsonify({'success': True})

@app.route('/feed')
def contentfeed():
    sourceID = request.args.get('sourceID')
    feed = copy.deepcopy(dataobj.storedict[sourceID])
    for entry in feed['entries']:
        entry['published'] = feedobj.formatDate(entry['published'])
    return jsonify(feed)

@app.route('/filter')
def filterfeed():
    sourceID = request.args.get('sourceID')
    filterBy = request.args.get('filterBy', type = int)
    feed = copy.deepcopy(dataobj.storedict[sourceID])
    feed['entries'] = feedobj.filterEntries(feed['entries'], filterBy)
    for entry in feed['entries']:
        entry['published'] = feedobj.formatDate(entry['published'])
    return jsonify(feed)

@app.route('/')
def index():
    return render_template('index.html', sources = dataobj.sourceList(), datadict = latestvideos())

if __name__ == '__main__':
    app.run(host = '0.0.0.0', port = 80, debug = False)
