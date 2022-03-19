import re, json, time, utils, datetime, requests

class TinyFeed(object):
    def __init__(self):
        self.url = 'https://www.youtube.com/watch?v={}'
        self.apiurl = 'https://{instance}/api/v1/{source}/{sourceid}'
        #
        self.playlisturl = 'https://www.youtube.com/playlist?list={}'
        self.channelurl = 'https://www.youtube.com/channel/{}/videos'
        #
        self.iconPattern1 = re.compile(r'https://yt3\.ggpht\.com/ytc/[a-zA-Z0-9-_]+=s')
        self.iconPattern2 = re.compile(r'https://yt[0-9]\.ggpht\.com/[a-zA-Z0-9-_]+=s')
        #
        self.vpidPattern1 = re.compile(r'https://i[0-9]*.ytimg.com/an_webp/([a-zA-Z0-9-_]+)')
        self.prevPattern1 = re.compile(r'[\"|\'](https://i[0-9]*.ytimg.com/an_webp/[a-zA-Z0-9-_]+/.*?)[\"|\']')

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
        dateobj = datetime.datetime.fromtimestamp(float(datestr))
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

    def extractIcon(self, url, iconsizes = [28, 50]):
        icons = []
        #
        try: iconurl = self.iconPattern1.search(url).group()
        except AttributeError: return self.extractIcon_(url, iconsizes)
        except: return ['', '']
        #
        for size in iconsizes:
            icons.append(iconurl + str(size))
        return icons

    def extractIcon_(self, content, iconsizes):
        icons = []
        try: iconurl = self.iconPattern2.search(content).group()
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
        if playlist:
            source = 'playlists'
            parameters = {'fields': 'title,authorThumbnails,videos'}
        else:
            source = 'channels'
            parameters = {'fields': 'author,authorThumbnails,latestVideos'}
        #
        url = self.apiurl.format(instance = 'invidious.privacy.gd', source = source, sourceid = sourceID)#rework
        res = requests.get(url, params = parameters, headers = utils.UAFirefox)
        return res

    def parseSource(self, sourceid, playlist):
        if playlist:
            return self.playlisturl.format(sourceid)
        else:
            return self.channelurl.format(sourceid)

    def parseFeed(self, sourceid, dictobj, playlist, previews):
        data = {'entries': []}
        sourceInfo = self.parseSource(sourceid, playlist)
        #
        data['sourceURL'] = sourceInfo
        data['sourceName'] = dictobj.get('author', dictobj.get('title'))
        data['lastUpdated'] = datetime.datetime.utcnow().strftime(utils.dfmt)
        data['channelIcon'] = self.extractIcon(dictobj['authorThumbnails'][0]['url'])
        #
        videos = dictobj.get('latestVideos', dictobj.get('videos'))
        counter = 0
        for entry in videos:
            if counter == 30: break
            stub = {}
            #
            stub['published'] = entry['published']
            stub['title'] = unicode(entry['title'])
            stub['url'] = self.url.format(entry['videoId'])
            stub['duration'] = self.formatTime(entry['lengthSeconds'])
            stub['preview'] = self.extractPreview(entry['videoId'], previews)
            stub['views'] = self.formatViews(entry['viewCount'])
            stub['thumbnail'] = entry['videoThumbnails'][4]['url']#mqdefault
            #
            data['entries'].append(stub)
            counter += 1
        return data

    def processSource(self, sourceID):
        playlist = sourceID.startswith('PL')
        resobj = self.downloadFeed(sourceID, playlist)
        #
        if resobj.status_code == 200:
            previews = playlist and [] or self.extractPreviews(sourceID)
        else:
            raise RuntimeError, 'Unexpected response: {} Source ID: {}'.format(resobj.status_code, sourceID)
        #
        return self.parseFeed(sourceID, json.loads(resobj.content), playlist, previews)

    def processSources(self, sourceIDs):
        masterdict = {}
        for sourceID in sourceIDs:
            masterdict[sourceID] = self.processSource(sourceID)
            time.sleep(0.5) #change instances instead of sleeping?
        return masterdict
