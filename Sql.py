import psycopg2

class Start(self):
    conn = psycopg2.connect(
    "dbname='MusicGenreMigration' user='postgres' host='postgres.d' password='minkovski'")
     self.cur = conn.cursor()


