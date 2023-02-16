import re, json, time, utils, datetime, requests, xmltodict

class TinyFeed(object):
    def __init__(self):
        self.url = 'https://www.youtube.com/watch?v={}'
        self.feedurl = 'https://www.youtube.com/feeds/videos.xml'
        self.playlisturl = 'https://www.youtube.com/playlist?list={}'
        self.channelurl = 'https://www.youtube.com/channel/{}/videos'
        self.timePattern1 = re.compile(r'\"lengthSeconds\":\"([0-9]+)\"')
        self.timePattern2 = re.compile(r'videoDurationSeconds\\\":\\\"([0-9]+)')
        self.vpidPattern1 = re.compile(r'https://i[0-9]*.ytimg.com/an_webp/([a-zA-Z0-9-_]+)')
        self.prevPattern1 = re.compile(r'[\"|\'](https://i[0-9]*.ytimg.com/an_webp/[a-zA-Z0-9-_]+/.*?)[\"|\']')
        self.iconPattern1 = re.compile(r'\"(https://yt[0-9]\.googleusercontent\.com/[a-zA-Z0-9-_]+=s)[a-z\-0-9]+\",\"width\"')
        self.iconPattern2 = re.compile(r'\"(https://yt[0-9]\.googleusercontent\.com/ytc/[a-zA-Z0-9-_]+=s)[a-z\-0-9]+\",\"width\"')

    def formatDate(self, datestr):
        dateobj = self.parseDate(datestr)
        return utils.formatDate(dateobj)

    def formatTime(self, seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        if h > 0: return '%d:%.2d:%.2d' %(h, m, s)
        else: return '%.2d:%.2d' %(m, s)

    def formatViews(self, views):
        magnitude = 0
        number = float('{:.3g}'.format(int(views)))
        denominations = ['', 'K', 'M', 'B', 'T', 'Q']
        while abs(number) >= 1000:
            magnitude += 1
            number /= 1000.0
        num = '{:f}'.format(number).rstrip('0').rstrip('.')
        stub = denominations[magnitude]
        return num + stub

    def parseDate(self, datestr, tzoffset = 0):
        dateobj = datetime.datetime.strptime(datestr, utils.dfmt)
        return dateobj + datetime.timedelta(minutes = tzoffset)

    def filterEntries(self, entries, hours):
        filtered = []
        seconds = hours * 3600
        filterobj = datetime.datetime.utcnow()
        for entry in entries:
            published = self.parseDate(entry['published'])
            difference = (filterobj - published).total_seconds()
            if difference <= seconds: filtered.append(entry)
        return filtered

    def videoDuration(self, url):
        embedURL = url.replace('watch?v=', 'embed/')
        res = requests.get(embedURL, headers = utils.UAFirefox)
        if res.status_code == 200:
            if 'live.jpg' in res.content: return 'LIVE' #hacky and poorly tested, but seems to work
            try: seconds = self.timePattern2.search(res.content).group(1)
            except AttributeError: return self.videoDuration_(url)
            except: return '00:00'
        else: return '00:00'
        return self.formatTime(int(seconds))

    def videoDuration_(self, url):
        res = requests.get(url, headers = utils.UAFirefox)
        if res.status_code == 200:
            try: seconds = self.timePattern1.search(res.content).group(1)
            except: return '00:00'
        else: return '00:00'
        return self.formatTime(int(seconds))

    def extractIcon(self, url, iconsizes = [28, 50]):
        icons = []
        res = requests.get(url, headers = utils.UAChrome)
        if res.status_code == 200:
            try: iconurl = self.iconPattern1.search(res.content).group(1)
            except AttributeError: return self.extractIcon_(res.content, iconsizes)
            except: return ['', '']
        else: return ['', '']
        for size in iconsizes:
            icons.append(iconurl + str(size))
        return icons

    def extractIcon_(self, content, iconsizes):
        icons = []
        try: iconurl = self.iconPattern2.search(content).group(1)
        except: return ['', '']
        for size in iconsizes:
            icons.append(iconurl + str(size))
        return icons

    def extractPreviews(self, sourceID):
        res = requests.get(self.channelurl.format(sourceID), headers = utils.UAChrome)
        if res.status_code == 200:
            return [x.replace('\u0026', '&') for x in self.prevPattern1.findall(res.content)]
        else: return []

    def extractPreview(self, videoID, previews):
        for preview in previews:
            if self.vpidPattern1.match(preview).group(1) == videoID:
                return preview
        else: return ''

    def downloadFeed(self, sourceID, playlist = False):
        if playlist: parameters = {'playlist_id': sourceID}
        else: parameters = {'channel_id': sourceID}
        res = requests.get(self.feedurl, params = parameters, headers = utils.UAOmea)
        return res

    def feedToDict(self, xmldata, saveTo = ''):
        dictobj = xmltodict.parse(xmldata)
        if saveTo:
            with open(saveTo, 'w') as handle:
                json.dump(dictobj, handle, indent = 4)
        return dictobj

    def parseSourceURL(self, sourceID, playlist = False):
        if playlist:
            return self.playlisturl.format(sourceID)
        else:
            return self.channelurl.format(sourceID)

    def parseFeed(self, dictobj, previews, url):
        data = {'entries': []}
        feed = dictobj['feed']
        #
        data['sourceURL'] = url
        data['sourceName'] = feed['title']
        data['channelIcon'] = self.extractIcon(feed['author']['uri'])
        data['lastUpdated'] = datetime.datetime.utcnow().strftime(utils.dfmt)
        #
        #fix for cases where video source has no videos
        if not feed.get('entry'): return data
        #fix for cases where video source only has one video
        if isinstance(feed['entry'], dict):
            feed['entry'] = [feed['entry']]
        #
        for entry in feed['entry']:
            stub = {}
            mediagroup = entry['media:group']
            mediacommunity = mediagroup['media:community']
            #
            stub['published'] = entry['published']
            stub['title'] = unicode(mediagroup['media:title'])
            stub['url'] = self.url.format(entry['yt:videoId'])
            stub['duration'] = self.videoDuration(stub['url'])
            stub['preview'] = self.extractPreview(entry['yt:videoId'], previews)
            stub['views'] = self.formatViews(mediacommunity['media:statistics']['@views'])
            stub['thumbnail'] = mediagroup['media:thumbnail']['@url'].replace('hqdefault', 'mqdefault')
            #
            data['entries'].append(stub)
        return data

    def parseLite(self, dictobj, index, previews):
        stub = {}
        entry = dictobj['feed']['entry'][index]
        #
        mediagroup = entry['media:group']
        mediacommunity = mediagroup['media:community']
        #
        stub['published'] = entry['published']
        stub['title'] = unicode(mediagroup['media:title'])
        stub['url'] = self.url.format(entry['yt:videoId'])
        stub['duration'] = self.videoDuration(stub['url'])
        stub['preview'] = self.extractPreview(entry['yt:videoId'], previews)
        stub['views'] = self.formatViews(mediacommunity['media:statistics']['@views'])
        stub['thumbnail'] = mediagroup['media:thumbnail']['@url'].replace('hqdefault', 'mqdefault')
        #
        return stub

    def newViewCount(self, dictobj, index):
        entry = dictobj['feed']['entry'][index]
        mediacommunity = entry['media:group']['media:community']
        return self.formatViews(mediacommunity['media:statistics']['@views'])

    def newTitle(self, dictobj, index):
        entry = dictobj['feed']['entry'][index]
        return unicode(entry['media:group']['media:title'])

    def updateFeed(self, oldfeed, newfeed, previews):
        ix = ix2 = 0
        container = []
        oldids, newids = [], []
        #
        #fix for cases where video source has no videos
        if not newfeed['feed'].get('entry'): return None
        #fix for cases where video source only has one video
        if isinstance(newfeed['feed']['entry'], dict):
            newfeed['feed']['entry'] = [newfeed['feed']['entry']]
        #
        for entry in oldfeed['entries']:
            oldids.append(entry['url'][32:])
        for entry in newfeed['feed']['entry']:
            newids.append(entry['yt:videoId'])
        #remove oldest and deleted videos since we last checked
        for x in xrange(len(oldids)):
            if oldids[x] not in newids:
                oldfeed['entries'].pop(x + ix)
                ix -= 1 #avoid IndexErrors
        #find and add any new videos since we last checked + update view counts and video durations if needed
        for x in xrange(len(newids)):
            if newids[x] not in oldids:
                container.append(self.parseLite(newfeed, x, previews))
            else:
                entry = oldfeed['entries'][ix2]
                if entry['duration'] in ['00:00', 'LIVE']:
                    entry['duration'] = self.videoDuration(entry['url'])
                entry['preview'] = self.extractPreview(entry['url'][32:], previews)
                entry['views'] = self.newViewCount(newfeed, x)
                entry['title'] = self.newTitle(newfeed, x)
                ix2 += 1
        oldfeed['entries'] = container + oldfeed['entries']

    def processSource(self, sourceID, oldfeed = None):
        playlist = sourceID.startswith('PL')#crude hack :(
        resobj = self.downloadFeed(sourceID, playlist)
        if resobj.status_code == 200:
            data = self.feedToDict(resobj.content)
            previews = [] if playlist else self.extractPreviews(sourceID)
        else:
            raise RuntimeError, 'Unexpected response: {} Source ID: {}'.format(resobj.status_code, sourceID)
        if oldfeed:
            self.updateFeed(oldfeed[sourceID], data, previews)
            oldfeed[sourceID]['lastUpdated'] = datetime.datetime.utcnow().strftime(utils.dfmt)
            return oldfeed[sourceID]
        url = self.parseSourceURL(sourceID, playlist)
        return self.parseFeed(data, previews, url)

    def processSources(self, sourceIDs, oldfeed = None):
        masterdict = {}
        for sourceID in sourceIDs:
            masterdict[sourceID] = self.processSource(sourceID, oldfeed)
            if not oldfeed: time.sleep(1)
        return masterdict

if __name__ == '__main__':
    c_url = 'UCEDkO7wshcDZ7UZo17rPkzQ'
    p_url = 'PLeyJPHbRnGaZmzkCwy3-8ykUZm_8B9kKM'
    #
    test = TinyFeed()
    res1 = test.downloadFeed(c_url)
    res2 = test.downloadFeed(p_url, True)
    #
    if res1.status_code == 200:
        obj1 = test.feedToDict(res1.content, 'verbose-{}.json'.format(c_url))
        data1 = test.parseFeed(obj1, test.extractPreviews(c_url), test.parseSourceURL(c_url))
        #
        with open('cleaned-{}.json'.format(c_url), 'w') as handle1:
            json.dump(data1, handle1, indent = 4)
    else:
        raise RuntimeError, 'Unexpected response: {}'.format(res1.status_code)
    #
    if res2.status_code == 200:
        obj2 = test.feedToDict(res2.content, 'verbose-{}.json'.format(p_url))
        data2 = test.parseFeed(obj2, [], test.parseSourceURL(p_url, True))
        #
        with open('cleaned-{}.json'.format(p_url), 'w') as handle2:
            json.dump(data2, handle2, indent = 4)
    else:
        raise RuntimeError, 'Unexpected response: {}'.format(res2.status_code)
    #
    print 'Done'
