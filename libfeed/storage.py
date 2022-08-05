import json, datetime

from . import utils


class DataStore(object):
    def __init__(self, storepath="data.json"):
        self.storepath = storepath
        self.storedict = {}

    def _isTooOld(self, datestr, threshold=1):
        newdate = datetime.datetime.utcnow()
        olddate = datetime.datetime.strptime(datestr, utils.dfmt)
        difference = (newdate - olddate).days
        if difference >= threshold:
            return True
        else:
            return False

    def initialize(self):
        self.retrieve()

    def retrieve(self):
        with open(self.storepath, "r") as handle:
            self.storedict = json.load(handle)

    def store(self, data={}, replace=False):
        if replace:
            self.storedict = data
        else:
            self.storedict.update(data)
        with open(self.storepath, "w") as handle:
            json.dump(self.storedict, handle)  # indent = 4

    def delete(self, sourceID):
        del self.storedict[sourceID]
        self.store()

    def needUpdate(self):
        found = []
        for sourceID in self.storedict:
            if self._isTooOld(self.storedict[sourceID]["lastUpdated"]):
                found.append(sourceID)
        return found

    def sourceList(self):
        clist = []
        for sourceID in self.storedict:
            temp = {
                "sourceID": sourceID,
                "sourceName": self.storedict[sourceID]["sourceName"],
                "channelIcon": self.storedict[sourceID]["channelIcon"][1],
            }
            clist.append(temp)
        return clist
