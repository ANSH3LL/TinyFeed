import datetime

#Date format string
dfmt = '%Y-%m-%dT%H:%M:%S+00:00'

#User Agents
UAOmea = {'user-agent': 'JetBrains Omea Reader 2.2 (http://www.jetbrains.com/omea/reader/)'}
UAFirefox = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:110.0) Gecko/20100101 Firefox/110.0'}
UAChrome = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36'}

def plural(number):
    return 's' if number > 1 else ''

def formatDate(dateobj):
    hours = minutes = seconds = 0
    years = months = weeks = days = 0
    newdate = datetime.datetime.utcnow()
    delta = newdate - dateobj
    if delta.days > 0:
        days = delta.days
        if days >= 30:
            days = delta.days % 30
            months = delta.days / 30
            if months >= 12:
                months = months % 12
                years = delta.days / 365
    #
    if days >= 7: weeks = days / 7
    #
    if delta.seconds > 0:
        seconds = delta.seconds
        if seconds >= 60:
            seconds = seconds % 60
            minutes = delta.seconds / 60
            if minutes >= 60:
                hours = minutes / 60
                minutes = minutes % 60
    #
    if years > 0:
        return '{0} year{1} ago'.format(years, plural(years))
    elif months > 0:
        return '{0} month{1} ago'.format(months, plural(months))
    elif weeks > 0:
        return '{0} week{1} ago'.format(weeks, plural(weeks))
    elif days > 0:
        return '{0} day{1} ago'.format(days, plural(days))
    elif hours > 0:
        return '{0} hour{1} ago'.format(hours, plural(hours))
    elif minutes > 0:
        return '{0} minute{1} ago'.format(minutes, plural(minutes))
    elif seconds > 0:
        return '{0} second{1} ago'.format(seconds, plural(seconds))
    else: return ''
