import sqlite3
from dataclasses import dataclass
from random_select import Track, SearchCriterion, search_tracks
import os

DATABASE_NAME = "ressource/tracks.sqlite"

class SqlDB:
    def __init__(self):       
        new = not os.path.isfile(DATABASE_NAME)

        self.con = sqlite3.connect(DATABASE_NAME)
        self.cur = self.con.cursor()

        if new:
            self.cur.execute("CREATE TABLE track(spotify_id, title, artist, popularity, year, album, search_id)")
            self.cur.execute("CREATE TABLE search(title, artist, year, album, genre, market, isrc, limmit, offfset)")

    def add_search(self, tracks: list[Track], q: SearchCriterion):
        q_value = "(\"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\"  )" %\
            (str(q.title),str(q.artist),str(q.year),str(q.album),str(q.genre),str(q.market),str(q.isrc),str(q.limit),str(q.offset))
        res = self.cur.execute("INSERT INTO search VALUES " + q_value)
        
        search_id = self.cur.lastrowid

        values = []
        for t in tracks:
            values.append("(\"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", %s)" %\
                (str(t.id),str(t.title),str(t.artist),str(t.popularity),str(t.year),str(t.album),str(search_id)))
        
        res = self.cur.execute("INSERT INTO track VALUES " + str.join(',',values))
            
        self.con.commit()

query = SearchCriterion()
query.year = 1995
tracks, total, next = search_tracks(query)  
db = SqlDB()
db.add_search(tracks, query)