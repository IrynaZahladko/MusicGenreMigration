
import Grabber
import re
import datetime
import Event

def insertUser(url, username):
    try:
        page = Grabber.Get(url)
        searchresult = re.search('<small>since ([\d]{1,2}[\s]+[a-zA-Z]+ [\d]{4,4})</small></span><p class="userActivity">', page)
        regdate = datetime.datetime.strptime(searchresult.group(1), "%d %b %Y")
        Sql = ("INSERT INTO userlist(username, regdate) SELECT '%s', '%s' WHERE NOT EXISTS (SELECT 1 FROM userlist WHERE username = '%s' AND regdate = '%s')" % (username, regdate, username, regdate,))
        cur.execute(Sql)
        conn.commit()
        cur.execute("SELECT userid FROM userlist WHERE username = '%s'" % (username,))
        userid = cur.fetchall()
        return userid[0][0]
    except:
        Error("I can't insert this user (%s) mazafacka!!!" % username)

def buildProfilePage(username):
    return ("http://www.last.fm/user/%s" % (username))

def grabUserPages(username):
    try:
        userid = insertUser(buildProfilePage(username),username)
        Info('Grabbing Pages for User %s' % username)
        nextpage = 1
        while nextpage != False:
            Info('Grabbing Page %s for User' % nextpage)
            nextpage = grabPage(buildHistoryUrl(username, nextpage), userid)
    except:
        Error("Can't grab PAGES for user %s" % username)

def grabPage(url, userid):
    try:
        page = Grabber.Get(url)
        searchresult = re.search('page=(\d+)[^>]*Next page', page)
        Debug(searchresult)
        if searchresult:
            nextpage = searchresult.group(1)
        else:
            nextpage = False
        line = re.findall(
            '<a href="/music/([^/]+)/_/([^/]+)"\s+class="recent-tracks-image media-pull-left media-link-hook">.*? datetime="([\d\-:TZ]+)"',
            page, re.S)
        Debug(line)
        for item in line:
            bandid = Event.insertBandName(item[0])  #insert in db-dict
            Event.grabBandPage(Event.buildBandUrl(item[0]), bandid)
            songid = Event.insertSongName(item[1], bandid)  #insert in db-dict
            Event.insertListening(userid, songid, item[2])
        return nextpage
    except:
        Error("Can't grab page %s" % url)

def buildHistoryUrl(username, page):
    return ("http://www.last.fm/user/%s/tracks?page=%s" % (username, page))