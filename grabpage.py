import urllib.request
import re
import pprint
import psycopg2
import datetime
import traceback

pp = pprint.PrettyPrinter(indent=4)
DEBUG = False

conn = psycopg2.connect(
    "dbname='MusicGenreMigration' user='postgres' host='postgres.d' password='minkovski'")  # connection to db
cur = conn.cursor()

def Debug(s):
    # pp.pprint(s)
    pass

def Error(s):
    pp.pprint(s)
    pass

def Info(s):
    pp.pprint(s)
    pass

def insertSongName(songname, bandid):
    try:
        Sql = "INSERT INTO dicsong (songname, bandid) SELECT '%s', '%s' WHERE NOT EXISTS (SELECT 1 FROM dicsong WHERE songname = '%s' AND bandid = '%s')" % (songname, bandid, songname, bandid)
        print(Sql)
        cur.execute(Sql)
        conn.commit()
        cur.execute("SELECT songid FROM dicsong WHERE songname = '%s' AND bandid = '%s'" % (songname, bandid))
        songid = cur.fetchall()
        return songid[0][0]
    except:
        Error("Can't insert song %s" % songname)

def insertBandName(bandname):
    try:
       Sql = "INSERT INTO dicband(bandname) SELECT '%s' WHERE NOT EXISTS (SELECT 1 FROM dicband WHERE bandname = '%s')" % (bandname, bandname)
       print(Sql)
       cur.execute(Sql)
       conn.commit()
       cur.execute("SELECT bandid FROM dicband WHERE bandname = '%s'" % (bandname,))
       bandid = cur.fetchall()
       return bandid[0][0]
    except:
        Error("Can't insert band %s" % bandname)

def buildBandUrl(bandname):
    return ("http://www.last.fm/music/%s" % (bandname))

def grabBandPage(url, bandid):
    try:
        f = urllib.request.urlopen(url)
        page = f.read().decode('utf-8')
        #googletag.pubads().setTargeting("tag", "punk,punkrock,british,70s,rock,classicrock,classicpunk,alternative,sexpistols,britishpunk");
        line = re.findall('googletag\.pubads\(\)\.setTargeting\("tag", "([^"]+)"\);', page)  #find all tag-words
        if not len(line):
            return  #RETURN WHAT???
        tags = line[0].split(',')
        for item in tags:
            genreid = insertGenreName(item)
            insertGenreBandMx(bandid, genreid)
    except:
        traceback.print_last()
        Error("Can't grab band page %s for bandid=%s" % (url , bandid))

def insertGenreName(genrename):
    try:
        Sql = ("INSERT INTO dicgenre(genrename) SELECT '%s' WHERE NOT EXISTS (SELECT 1 FROM dicgenre WHERE genrename = '%s')" % (genrename, genrename))
        print(Sql)
        cur.execute(Sql)
        conn.commit()
        cur.execute("SELECT genreid FROM dicgenre WHERE genrename = '%s'" % (genrename,))
        genreid = cur.fetchall()
        return genreid[0][0]
    except:
        # traceback.print_last()
        Error("Can't insert genre %s;" % (genrename,))

def insertGenreBandMx(bandid, genreid):
    try:
        Sql = "INSERT INTO bandgenremx(bandid, genreid) SELECT '%s', '%s' WHERE NOT EXISTS (SELECT 1 FROM bandgenremx WHERE bandid = '%s' AND genreid = '%s')" % (bandid, genreid, bandid, genreid)
        print(Sql)
        cur.execute(Sql)
        conn.commit()
    except:
        Error("Can't insert in band-genre-mx")

def insertListening(userid, songid, listeningdate):
    try:
        Sql = ("INSERT INTO listening(userid, songid, listeningdate) SELECT '%s', '%s', '%s' WHERE NOT EXISTS (SELECT 1 FROM listening WHERE userid = '%s' AND songid = '%s' AND listeningdate = '%s')" % (userid, songid, listeningdate, userid, songid, listeningdate))
        print(Sql)
        cur.execute(Sql)
        conn.commit()
    except:
        Error("Can't insert listening item!")

def insertUser(url, username):
    try:
        f = urllib.request.urlopen(url)
        page = f.read().decode('utf-8')
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

def grabPage(url, userid):
    try:
        f = urllib.request.urlopen(url)
        page = f.read().decode('utf-8')
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
            bandid = insertBandName(item[0])  #insert in db-dict
            grabBandPage(buildBandUrl(item[0]), bandid)
            songid = insertSongName(item[1], bandid)  #insert in db-dict
            insertListening(userid, songid, item[2])
        return nextpage
    except:
        Error("Can't grab page %s" % url)

def buildHistoryUrl(username, page):
    return ("http://www.last.fm/user/%s/tracks?page=%s" % (username, page))

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

# <a href="/user/kakabomba/tracks?page=3" class="btn btn--icon-only btn--small btn--white iconright iconright--right" rel="next" title="Next page">Next</a>

#<a href="/music/Downlink/_/Triphekta"     class="recent-tracks-image media-pull-left media-link-hook"> 

grabUserPages('kakabomba')  #THE FIRST STEP



#postges.d/postgres/minkovski

