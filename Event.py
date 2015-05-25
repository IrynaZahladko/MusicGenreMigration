
import Grabber
import re
import traceback

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
        Grabber.Get(url)
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
