"""
Dump search to a local db
https://sqliteviewer.app
"""

import sqlite3
from dataclasses import dataclass
from track_search import Track, SearchCriterion, search_tracks
import os
import urllib.parse
import pandas as pd
from requests.utils import requote_uri, unquote

DATABASE_ROOT = "ressource/"

class SqlDB:
    def __init__(self, strategy = "tracks"):  
        self.filename = DATABASE_ROOT +strategy+".sqlite"     
        self.strategy = strategy

        new = not os.path.isfile(self.filename)

        self.con = sqlite3.connect(self.filename)
        self.cur = self.con.cursor()

        if new:
            self.cur.execute("CREATE TABLE track(spotify_id, title, artist, popularity, year, album, search_id)")
            self.cur.execute("CREATE TABLE search(title, artist, year, album, genre, market, isrc, limmit, offfset, strategy, total)")

        # self.cur.execute("ALTER TABLE search ADD total")

    def add_search(self, tracks: list[Track], q: SearchCriterion, total):
        try:
            # Remove special character with url encoding to prevent error in sql query
            val = lambda x : requote_uri(str(x))

            q_value = "(\"%s\", \"%s\", \"%s\", \"%s\",\
                        \"%s\", \"%s\", \"%s\", \"%s\",\
                        \"%s\", \"%s\" , \"%s\" )" %\
                        (val(q.title),val(q.artist),val(q.year),val(q.album),\
                         val(q.genre),val(q.market),val(q.isrc),val(q.limit),\
                        val(q.offset),val(self.strategy),val(total))
            
            res = self.cur.execute("INSERT INTO search VALUES " + q_value)
            
            search_id = self.cur.lastrowid

            values = []
            for t in tracks:
                values.append("(\"%s\", \"%s\", \"%s\", \"%s\", \"%s\", \"%s\", %s)" %\
                    (val(t.id),val(t.title),val(t.artist),val(t.popularity),val(t.year),val(t.album),val(search_id)))
            
            if len(values) > 0:
                res = self.cur.execute("INSERT INTO track VALUES " + str.join(',',values))
                
            self.con.commit()
        except Exception as e:
            print("ERROR: DB insertion error, ", e)

    def get_tracks(self, where=None):
        where = "" if where is None else ("WHERE " + where)
        query = "SELECT * FROM track " + where

        res = self.cur.execute(query)
        res = res.fetchall()
        
        search_id = [] # search_id is mostly meant for product table (join)
        tracks = []
        for row in res:
            row = [unquote(r) for r in row]
            t = Track() 
            t.id = row[0]
            t.title = row[1]
            t.artist = row[2]
            t.popularity = row[3]
            t.year = row[4]
            t.album = row[5]
            tracks.append(t)
            q = row[6]
            search_id.append(q)
            
        return tracks

    def get_tracks_df(self, where=None):
        where = "" if where is None else ("WHERE " + where)
        query = "SELECT * FROM track " + where
        
        df = pd.read_sql_query(query, self.con)
        return df



# query = SearchCriterion()
# query.year = 1995
# tracks, total, next = search_tracks(query)  
# db = SqlDB("test_db")
# db.add_search(tracks, query, total)
