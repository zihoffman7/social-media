from werkzeug.security import check_password_hash, generate_password_hash
import mysql.connector, time, os
from uuid import uuid4

class db:
    def __init__(self):
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password",
            database="media",
            auth_plugin="mysql_native_password",
            charset="utf8mb4"
        )
        self.cursor = self.db.cursor(buffered=True)
        with open("schema.sql") as f:
            self.cursor.execute(f.read(), multi=True)
        self.db.commit()

    def __del__(self):
        self.db.close()

    def create_account(self, username, password):
        self.cursor.execute("INSERT INTO users VALUES (%s, %s, %s)", (username, generate_password_hash(password), 0))
        self.db.commit()

    def check_username(self, username):
        self.cursor.execute("SELECT username FROM users WHERE username = '" + username + "';")
        if self.cursor.fetchone():
            return True
        return False

    def check_account_credentials(self, username, password):
        self.cursor.execute("SELECT password FROM users WHERE username = '" + username + "';")
        p = self.cursor.fetchone()
        if p:
            return check_password_hash(p[0], password)

    def delete_account(self, username):
        self.cursor.execute("SELECT id FROM posts WHERE user = '" + username + "';")
        for id in self.cursor.fetchall():
            self.delete_post(id)
        self.cursor.execute("DELETE FROM users WHERE username = '" + username + "';")
        self.cursor.execute("DELETE FROM follows WHERE follower = '" + username + "' OR following = '" + username + "';")
        self.cursor.execute("DELETE FROM follow_requests WHERE requester = '" + username + "' OR requestee = '" + username + "';")
        self.cursor.execute("DELETE FROM comments WHERE user = '" + username + "';")
        self.cursor.execute("DELETE FROM likes WHERE user = '" + username + "';")
        self.db.commit()

    def update_password(self, username, password):
        self.cursor.execute("UPDATE users SET password = '" + password + "' WHERE username = '" + username + "';")
        self.db.commit()

    def update_username(self, initial, final):
        self.cursor.execute("UPDATE users SET username = '" + final + "' WHERE username = '" + initial + "';")
        self.cursor.execute("UPDATE follow_requests SET requester = '" + final + "' WHERE requester = '" + initial + "';")
        self.cursor.execute("UPDATE follow_requests SET requestee = '" + final + "' WHERE requestee = '" + initial + "';")
        self.cursor.execute("UPDATE follows SET following = '" + final + "' WHERE following = '" + initial + "';")
        self.cursor.execute("UPDATE follows SET follower = '" + final + "' WHERE follower = '" + initial + "';")
        self.cursor.execute("UPDATE likes SET user = '" + final + "' WHERE user = '" + initial + "';")
        self.cursor.execute("UPDATE comments SET user = '" + final + "' WHERE user = '" + initial + "';")
        self.cursor.execute("UPDATE posts SET user = '" + final + "' WHERE user = '" + initial + "';")
        self.db.commit()

    def request_follow(self, requester, requestee):
        self.cursor.execute("INSERT INTO follow_requests VALUES (%s, %s)", (requester, requestee))

    def add_follower(self, following, follower):
        self.cursor.execute("DELETE FROM follow_requests WHERE requester = '" + follower + "' AND requestee = '" + following + "';")
        self.cursor.execute("INSERT INTO follows VALUES (%s, %s)", (follower, following))
        self.db.commit()

    def remove_request(self, follower, following):
        self.cursor.execute("DELETE FROM follow_requests WHERE requester = '" + follower + "' AND requestee = '" + following + "';")
        self.db.commit()

    def is_requested(self, requester, requestee):
        self.cursor.execute("SELECT * FROM follow_requests WHERE requester = '" + requester + "' AND requestee = '" + requestee + "';")
        return self.cursor.fetchone()

    def get_requests(self, username):
        try:
            self.cursor.execute("SELECT requester FROM follow_requests WHERE requestee = '" + username + "';")
            return self.cursor.fetchall()
        except:
            return []

    def get_my_requests(self, username):
        try:
            self.cursor.execute("SELECT requestee FROM follow_requests WHERE requester = '" + username + "';")
            return self.cursor.fetchall()
        except:
            return []

    def unfollow(self, follower, following):
        self.cursor.execute("DELETE FROM follows WHERE follower = '" + follower + "' AND following = '" + following + "';")
        self.db.commit()

    def followers(self, username):
        self.cursor.execute("SELECT follower FROM follows WHERE following = '" + username + "';")
        return list(self.cursor.fetchall())

    def following(self, username):
        self.cursor.execute("SELECT following FROM follows WHERE follower = '" + username + "';")
        return list(self.cursor.fetchall())

    def create_post(self, username, path, time, title, caption):
        self.cursor.execute("INSERT INTO posts VALUES (%s, %s, %s, %s, %s, %s)", (username, path, time, str(uuid4()), title, caption))
        self.db.commit()

    def insert_comment(self, username, comment, id, time):
        self.cursor.execute("INSERT INTO comments VALUES (%s, %s, %s, %s, %s, %s)", (id, username, comment, time, str(uuid4()), 0))
        self.db.commit()

    def edit_comment(self, username, comment, comment_id):
        self.cursor.execute("UPDATE comments SET content = '" + comment + "' WHERE user = '" + username + "' AND commentid = '" + comment_id + "';")
        self.cursor.execute("UPDATE comments SET edited = '1' WHERE user = '" + username + "' AND commentid = '" + comment_id + "';")
        self.db.commit()

    def delete_comment(self, username, comment_id):
        self.cursor.execute("DELETE FROM comments WHERE user = '" + username + "' AND commentid = '" + comment_id + "';")
        self.db.commit()

    def get_posts(self, username, user=None):
        if not user:
            user = username
        self.cursor.execute("SELECT * FROM posts WHERE user = '" + username + "';")
        posts = [list(i) for i in self.cursor.fetchall()]
        posts.sort(key=lambda x: x[2], reverse=True)
        ids = [i[3] for i in posts]
        for id in ids:
            posts[ids.index(id)].append(list(self.get_comments(id)))
            posts[ids.index(id)].append(self.get_likes(id))
            posts[ids.index(id)].append(self.has_liked(user, id))
        return posts

    def get_post_content(self, username):
        posts = []
        self.cursor.execute("SELECT following FROM follows WHERE follower = '" + username + "';")
        for person in [username] + [i[0] for i in self.cursor.fetchall()]:
            posts += self.get_posts(person, username)
        posts.sort(key=lambda x: x[2], reverse=True)
        posts = posts[:70]
        for i in posts:
            i[2] = str(time.strftime("%a, %b %d, %Y, %I:%M %p", time.localtime(int(i[2].split(".")[0]))))
        return posts

    # def get_liked_posts(self, username):
    #     self.cursor.execute("SELECT id FROM likes WHERE user = '" + username + "';")
    #     posts = []
    #     for id in [i[0] for i in self.cursor.fetchall()]:
    #         self.cursor.execute("SELECT * FROM posts WHERE id = '" + id + "';")
    #         post = list(self.cursor.fetchall()[0])
    #         post.append(list(self.get_comments(id)))
    #         post.append(self.get_likes(id))
    #         post.append(1)
    #         posts.append(post)
    #     posts.sort(key=lambda x: x[2], reverse=True)
    #     for i in posts:
    #         i[2] = str(time.strftime("%a, %b %d, %Y, %I:%M %p", time.localtime(int(str(i[2]).split(".")[0]))))
    #     return posts

    def get_comments(self, id):
        self.cursor.execute("SELECT * FROM comments WHERE postid = '" + id + "';")
        comments = [list(i) for i in self.cursor.fetchall()]
        comments.sort(key=lambda x: x[3], reverse=True)
        for i in comments:
            i[3] = str(time.strftime("%a, %b %d, %Y, %I:%M %p", time.localtime(int(i[3].split(".")[0]))))
        return comments

    def post_user_from_id(self, id):
        self.cursor.execute("SELECT user FROM posts WHERE id = '" + id + "';")
        return self.cursor.fetchone()

    def filepath_from_id(self, id):
        self.cursor.execute("SELECT filepath FROM posts WHERE id = '" + id + "';")
        return self.cursor.fetchone()

    def delete_post(self, id):
        self.cursor.execute("DELETE FROM posts WHERE id = '" + id + "';")
        self.cursor.execute("DELETE FROM comments WHERE postid = '" + id + "';")
        self.cursor.execute("DELETE FROM likes WHERE id = '" + id + "';")
        self.db.commit()

    def has_liked(self, user, id):
        self.cursor.execute("SELECT * FROM likes WHERE id = '" + id + "' AND user = '" + user + "';")
        return bool(self.cursor.fetchone())

    def like_post(self, user, id):
        self.cursor.execute("INSERT INTO likes VALUES (%s, %s)", (id, user))
        self.db.commit()

    def unlike_post(self, user, id):
        self.cursor.execute("DELETE FROM likes WHERE user = '" + user + "' AND id = '" + id + "'")
        self.db.commit()

    def get_likes(self, id):
        self.cursor.execute("SELECT user FROM likes WHERE id = '" + id + "';")
        return len(self.cursor.fetchall())

    def is_public(self, user):
        self.cursor.execute("SELECT public FROM users WHERE username = '" + user + "';")
        return {"1" : 1, "0" : 0}[self.cursor.fetchone()[0]]

    def change_status(self, username, status):
        try:
            self.cursor.execute("UPDATE users SET public = '" + {"true" : "1", "false" : "0"}[status] + "' WHERE username = '" + username + "';")
            self.db.commit()
            return True
        except:
            return False

    def get_users(self):
        self.cursor.execute("SELECT username FROM users;")
        return [i[0] for i in self.cursor.fetchall()]

    def count_posts(self, user):
        self.cursor.execute("SELECT * FROM posts WHERE user = '" + user + "';")
        return len(self.cursor.fetchall())
