import sqlite3


class DBCONTENT(object):

    def __init__(self, user_id):
        self.conn = sqlite3.connect('cache/{user_id}.db'.format(user_id=user_id))
        self.c = self.conn.cursor()
        self.c.execute(
            '''CREATE table IF NOT EXISTS cards (front TEXT UNIQUE, back TEXT, collection TEXT)''')

    def add(self, front, back, collection):
        try:
            self.c.execute(
                "INSERT INTO cards VALUES ('{front}','{back}','{collection}')".format(
                    front=front, back=back, collection=collection))
            self.conn.commit()
        except Exception:
            print('Not unique value to insert')
            pass
        pass

    def find(self, front):
        self.c.execute("SELECT * FROM cards WHERE front='{front}'".format(front=front))
        return self.c.fetchone()

    def get_all(self):
        self.c.execute("SELECT * FROM cards")
        return self.c.fetchall()

    def update(self, front, back, collection):
        try:
            self.c.execute(
                "UPDATE cards SET front = '{front}', back = '{back}', collection = '{collection}'".format(
                    front=front, back=back, collection=collection))
            self.conn.commit()
        except Exception:
            print('Not unique value to insert')
            pass
        pass

    def delete(self, front):
        try:
            self.c.execute("DELETE FROM cards WHERE front='{front}'".format(front=front))
            self.conn.commit()
        except Exception:
            print('ERROR DELETE')
            pass
        pass
# conn.close()


