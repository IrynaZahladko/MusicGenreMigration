import urllib.request
import re
import pprint
import psycopg2
import datetime

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
        cur.execute("INSERT INTO dicsong(songname, bandid) VALUES ('%s', '%s')" % (songname, bandid, ))
        conn.commit()
    except:
        conn.rollback()
    cur.execute("SELECT songid FROM dicsong WHERE songname = '%s' AND bandid = '%s'" % (songname, bandid))
    songid = cur.fetchall()
    return songid[0][0]


def insertBandName(bandname):
    try:
        cur.execute("INSERT INTO dicband(bandname) VALUES ('%s')" % (bandname,))
        conn.commit()
    except:
        conn.rollback()
    # print("INSERT INTO dicband(bandname) VALUES ('%s')" % (bandname,))
    #conn.commit()
    cur.execute("SELECT bandid FROM dicband WHERE bandname = '%s'" % (bandname,))
    bandid = cur.fetchall()
    return bandid[0][0]


# --------------------------------------------------------------------18th May-------
def buildBandUrl(bandname):
    return ("http://www.last.fm/music/%s" % (bandname))


def grabBandPage(url, bandid):
    # Debug(url)
    try:
        f = urllib.request.urlopen(url)
        page = f.read().decode('utf-8')
        #googletag.pubads().setTargeting("tag", "punk,punkrock,british,70s,rock,classicrock,classicpunk,alternative,sexpistols,britishpunk");
        line = re.findall('googletag\.pubads\(\)\.setTargeting\("tag", "([^"]+)"\);', page)  #find all tag-words
        if not len(line):
            return
        tags = line[0].split(',')  #я не зрозуміла. перепояснити!!!
        for item in tags:
            genreid = insertGenreName(item)
            insertGenreBandMx(bandid, genreid)
    except:
        Error("can't grab band page %s for bandid=%s" % (url , bandid))


def insertGenreName(genrename):
    try:
        cur.execute("INSERT INTO dicgenre(genrename) VALUES ('%s')" % (genrename,))
        conn.commit()

    except:
        conn.rollback()
    cur.execute("SELECT genreid FROM dicgenre WHERE genrename = '%s'" % (genrename,))
    genreid = cur.fetchall()
    return genreid[0][0]


def insertGenreBandMx(bandid, genreid):
    try:
        cur.execute("INSERT INTO bandgenremx(bandid, genreid) VALUES ('%s', '%s')" % (bandid, genreid, ))
        conn.commit()
    except:
        conn.rollback()
        #------------------------------------------------------------20th May


def insertListening(userid, songid, listeningdate):
    try:
        cur.execute("INSERT INTO listening(userid, songid, listeningdate) VALUES ('%s', '%s', '%s')" % (
        userid, songid, listeningdate,))
        conn.commit()
    except:
        conn.rollback()


def insertUser(url, username):
    f = urllib.request.urlopen(url)
    page = f.read().decode('utf-8')
    searchresult = re.search('<small>since ([\d]{1,2}[\s]+[a-zA-Z]+ [\d]{4,4})</small></span><p class="userActivity">', page)
    regdate = datetime.datetime.strptime(searchresult.group(1), "%d %b %Y")
    try:
        cur.execute("INSERT INTO userlist(username, regdate) VALUES ('%s', '%s')" % (username, regdate, ))
        conn.commit()
    except:
        conn.rollback()
    cur.execute("SELECT userid FROM userlist WHERE username = '%s'" % (username,))
    userid = cur.fetchall()
    return userid[0][0]

    #-------------------------------------------------------21th May

def buildProfilePage(username):
    return ("http://www.last.fm/user/%s" % (username))
    #-------------------------------------------------------------
def grabPage(url, userid):
    f = urllib.request.urlopen(url)
    page = f.read().decode('utf-8')
    # print(page)
    # page = ''
    searchresult = re.search('page=(\d+)[^>]*Next page', page)
    Debug(searchresult)  #go away
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

def buildHistoryUrl(username, page):
    return ("http://www.last.fm/user/%s/tracks?page=%s" % (username, page))

def grabUserPages(username):
    userid = insertUser(buildProfilePage(username),username)  # NEW!!!
    Info('Grabbing Pages for User %s' % username)
    nextpage = 1
    while nextpage != False:
        Info('Grabbing Page %s for User' % nextpage)
        nextpage = grabPage(buildHistoryUrl(username, nextpage), userid)

# <a href="/user/kakabomba/tracks?page=3" class="btn btn--icon-only btn--small btn--white iconright iconright--right" rel="next" title="Next page">Next</a>

#<a href="/music/Downlink/_/Triphekta"     class="recent-tracks-image media-pull-left media-link-hook"> 



grabUserPages('kakabomba')  #THE FIRST STEP



#postges.d/postgres/minkovski
#-de pysaty nazvu db
#- jak dodaty foreignkey
