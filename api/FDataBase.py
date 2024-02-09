import sqlite3
import time
import math


class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getMenu(self):
        sql = '''SELECT * FROM mainmenu'''
        self.__cur.execute(sql)
        res = self.__cur.fetchall()
        if res: return res

    def addPost(self, title, text, author, photo = None):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM posts WHERE title LIKE '{title}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Статья с таким title уже существует")
                return False

            tm = math.floor(time.time())
            if photo:
                self.__cur.execute("INSERT INTO images VALUES(NULL, ?)", (photo,))
                self.__db.commit()

                self.__cur.execute("SELECT id FROM images WHERE path=?", (photo,))
                res = self.__cur.fetchone()
                self.__cur.execute("INSERT INTO posts VALUES(NULL, ?, ?, ?, ?, ?)", (title, text, tm, res[0], author))
                self.__db.commit()

                return True 
               
            self.__cur.execute("INSERT INTO posts VALUES(NULL, ?, ?, ?, NULL, ?)", (title, text, tm, author))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления статьи в БД "+str(e))
            return False

        return True

    def getPost(self, id):
        try:
            self.__cur.execute("""SELECT posts.title AS title, posts.text AS text, posts.time AS time, users.name AS name 
                               FROM posts
                               JOIN users ON users.id = posts.author_id
                               WHERE posts.id = ? LIMIT 1""", (id,))
            res = self.__cur.fetchone()
            if res:
                return res
        except sqlite3.Error as e:
            print("Ошибка получения статьи из БД "+str(e))

        return (False, False, False, False)

    def addUser(self, name, email, hpsw):
        try:
            self.__cur.execute(f"SELECT COUNT() as `count` FROM users WHERE email LIKE '{email}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print("Пользователь с таким email уже существует")
                return False

            tm = math.floor(time.time())
            self.__cur.execute("INSERT INTO users VALUES(NULL, ?, ?, ?, ?)", (name, email, hpsw, tm))
            self.__db.commit()
        except sqlite3.Error as e:
            print("Ошибка добавления пользователя в БД "+str(e))
            return False

        return True

    def getUser(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД "+str(e))

        return False

    def getUserByEmail(self, email):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE email = '{email}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False

            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД "+str(e))

        return False
    def get_all_posts(self):
        self.__cur.execute("""SELECT posts.title AS title, posts.id AS id, posts.time AS time, image.path AS img_path
                              FROM posts 
                              LEFT JOIN images AS image ON image.id = posts.img_id 
                              ORDER BY posts.time DESC
                              """)
        all_posts = self.__cur.fetchall()

        return all_posts
    def get_caroules_posts(self):
        self.__cur.execute("""SELECT posts.title AS title, posts.text AS text, posts.id AS id, posts.time AS time, image.path AS img_path
                            FROM posts 
                            JOIN images AS image ON image.id = posts.img_id 
                            ORDER BY posts.time ASC
                            LIMIT 4""")
        posts = self.__cur.fetchall()

        return posts
    def get_top_posts(self):
        self.__cur.execute("""SELECT title, id
                            FROM posts 
                            WHERE img_id IS NULL
                            ORDER BY posts.time DESC
                            LIMIT 5""")
        posts = self.__cur.fetchall()
        return posts

        
        
        

