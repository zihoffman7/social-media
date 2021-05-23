from flask import redirect, url_for, render_template, request, session, Blueprint, jsonify, send_from_directory
from subprocess import call
from database import db
from uuid import uuid4
from json import dumps
import os, time, re

main = Blueprint("main", __name__)
db = db()

@main.route("/", methods=["GET"])
def index():
    return redirect(url_for("main.browse"))

@main.route("/register", methods=["GET", "POST"])
def register():
    if not "username" in session:
        if request.method == "POST":
            username = re.sub("[^0-9a-zA-Z_\-.]+", "", request.form["username"].strip())
            if db.check_username(username):
                return render_template("register.html", flash="This username already exists")
            db.create_account(username, request.form["p1"])
            session["username"] = username
            session.permanent = True
            return redirect(url_for("main.profile"))
        return render_template("register.html")
    return redirect(url_for("main.browse"))

@main.route("/check/username", methods=["POST"])
def check_username():
    if len(request.form["username"]) < 4:
        return jsonify(status=False, message="Please increase the length of your username")
    if not re.sub("[^0-9a-zA-Z_\-.]+", "", request.form["username"]) == request.form["username"]:
        return jsonify(status=False, message="Please remove the special characters and spaces")
    if db.check_username(request.form["username"]):
        return jsonify(status=False, message="A user with this name already exists")
    return jsonify(status=True)

@main.route("/check/passwords", methods=["POST"])
def check_passwords():
    if not request.form["p1"] == request.form["p2"]:
        return jsonify(status=False, message="Your passwords do not match")
    if len(request.form["p1"]) < 4:
        return jsonify(status=False, message="Please choose a longer password")
    return jsonify(status=True)

@main.route("/login", methods=["GET", "POST"])
def login():
    if not "username" in session:
        if request.method == "POST":
            username = re.sub("[^0-9a-zA-Z_\-.]+", "", request.form["username"].strip())
            password = request.form["password"]
            if db.check_account_credentials(username, password):
                session["username"] = username
                session.permanent = True
                return redirect(url_for("main.browse"))
            return render_template("login.html", flash="Invalid account credentials")
        return render_template("login.html")
    return redirect(url_for("main.browse"))

@main.route("/logout", methods=["GET"])
def logout():
    if "username" in session:
        session.pop("username", None)
    return redirect(url_for("main.login"))

@main.route("/delete/account", methods=["POST"])
def delete_account():
    if "username" in session:
        if db.check_account_credentials(session["username"], request.form["password"]):
            db.delete_account(session["username"])
            call(["php", "files.php", dumps({"task" : "delete dir","user" : session["username"]})])
            session.pop("username", None)
    return redirect(url_for("main.login"))

@main.route("/profile", methods=["GET"])
def profile():
    if "username" in session:
        posts = db.get_posts(session["username"])
        for i in posts:
            i[2] = str(time.strftime("%a, %b %d, %Y, %I:%M %p", time.localtime(int(i[2].split(".")[0]))))
        return render_template("profile.html", posts=posts, username=session["username"], followers=len(db.followers(session["username"])), following=len(db.following(session["username"])))
    return redirect(url_for("main.login"))

@main.route("/profile/settings", methods=["GET", "POST"])
def settings():
    if "username" in session:
        flash = None
        if request.method == "POST":
            if "p1" in request.form:
                db.update_password(session["username"], request.form["p1"])
                flash = "Password changed successfully"
            if "username" in request.form:
                if db.check_username(request.form["username"]):
                    return render_template("settings.html", flash="This username already exists")
                username = re.sub("[^0-9a-zA-Z_-]+", "", request.form["username"])
                db.update_username(session["username"], username)
                session["username"] = username
                flash = "Username changed successfully"
        return render_template("settings.html", flash=flash, username=session["username"], public=db.is_public(session["username"]))
    return redirect(url_for("main.login"))

@main.route("/people/<user>", methods=["GET"])
def user_profile(user):
    if "username" in session:
        if not db.check_username(user):
            return redirect(url_for("main.profile"))
        if user == session["username"]:
            return redirect(url_for("main.profile"))
        if session["username"] in [i[0] for i in db.followers(user)] or db.is_public(user):
            posts = db.get_posts(user, session["username"])
            for i in posts:
                i[2] = str(time.strftime("%a, %b %d, %Y, %I:%M %p", time.localtime(int(i[2].split(".")[0]))))
            return render_template("user.html", user=user, posts=posts, username=session["username"], followers=len(db.followers(user)), following=len(db.following(user)), public=db.is_public(user), private=False)
        return render_template("user.html", user=user, username=session["username"], followers=len(db.followers(user)), following=len(db.following(user)), private=True, public=db.is_public(user))

    return redirect(url_for("main.login"))

@main.route("/follow/request", methods=["POST"])
def request_follow():
    if not "username" in session:
        return jsonify(status=False)
    if request.form["user"] == session["username"]:
        return jsonify(status=True, message="You can't request to follow yourself")
    if not db.check_username(request.form["user"]):
        return jsonify(status=True, message="A user with this name does not exist")
    if request.form["user"] in [i[0] for i in db.following(session["username"])]:
        return jsonify(status=True, message="You are already following this user")
    if not db.is_requested(session["username"], request.form["user"]):
        if db.check_username(request.form["user"]):
            if db.is_public(request.form["user"]):
                db.add_follower(request.form["user"], session["username"])
                return jsonify(status=True, message="You are now following " + request.form["user"])
            db.request_follow(session["username"], request.form["user"])
            return jsonify(status=True, message="Follow requested")
        return jsonify(status=True)
    return jsonify(status=True, message="You have already requested this user")

@main.route("/follow/accept", methods=["POST"])
def accept_follow():
    if not "username" in session or not db.check_username(request.form["user"]) or not db.is_requested(request.form["user"], session["username"]) or request.form["user"] in db.followers(session["username"]):
        return jsonify(status=False)
    db.add_follower(session["username"], request.form["user"])
    if not request.form["user"] in [i[0] for i in db.following(session["username"])] and not db.is_requested(session["username"], request.form["user"]):
        return jsonify(status=True, show=True)
    return jsonify(status=True, show=False)

@main.route("/follow/deny", methods=["POST"])
def deny_follow():
    if not "username" in session or not db.check_username(request.form["user"]):
        return jsonify(status=False)
    if db.is_requested(request.form["user"], session["username"]):
        db.remove_request(request.form["user"], session["username"])
        return jsonify(status=True)
    return jsonify(status=False)

@main.route("/follow/unrequest", methods=["POST"])
def unrequest():
    if not "username" in session:
        return jsonify(status=False)
    if db.is_requested(session["username"], request.form["user"]):
        db.remove_request(session["username"], request.form["user"])
        return jsonify(status=True, message="Follow unrequested")
    return jsonify(status=False)

@main.route("/follow/unfollow", methods=["POST"])
def unfollow():
    if not "username" in session:
        return jsonify(status=False)
    if request.form["user"] in [i[0] for i in db.following(session["username"])]:
        db.unfollow(session["username"], request.form["user"])
        return jsonify(status=True, message="Successfully unfollowed " + request.form["user"])
    return jsonify(status=False)

@main.route("/status", methods=["POST"])
def change_status():
    if not "username" in session:
        return jsonify(status=False)
    if not db.change_status(session["username"], request.form["public"]):
        return jsonify(status=False)
    return jsonify(status=True, message=request.form["public"])

@main.route("/followers", methods=["GET"])
def followers():
    if not "username" in session:
        return jsonify(status=False)
    return jsonify(status=True, data=db.followers(session["username"]))

@main.route("/following", methods=["GET"])
def following():
    if not "username" in session:
        return jsonify(status=False)
    return jsonify(status=True, data=db.following(session["username"]))

@main.route("/people", methods=["GET"])
def people():
    if "username" in session:
        return render_template("people.html", requests=db.get_requests(session["username"]), myrequests=db.get_my_requests(session["username"]), username=session["username"], followers=len(db.followers(session["username"])), following=len(db.following(session["username"])), people=db.get_users())
    return redirect(url_for("main.login"))

@main.route("/post", methods=["GET", "POST"])
def post():
    if "username" in session:
        if db.count_posts(session["username"]) > 30:
            return render_template("post.html", username=session["username"], allowed=False)
        if request.method == "POST":
            file = request.files["image"]
            if not file.filename.split(".")[1].lower() in ["jpg", "jpeg", "png", "gif"]:
                return render_template("post.html", flash="Invalid file type")
            call(["php", "files.php", dumps({"task" : "create dir","user" : session["username"]})])
            initial_filepath = "uploads/" + session["username"] + "/" + str(uuid4()) + "." + file.filename.split(".")[1].lower()
            file.save(initial_filepath)
            if os.stat(initial_filepath).st_size > 8000000:
                os.remove(os.path.join(initial_filepath))
                return render_template("post.html", flash="File is too large")
            final_filepath = "uploads/" + session["username"] + "/" + str(uuid4()) + ".jpg"
            call(["php", "files.php", dumps({"task" : "compress","initial_path" : initial_filepath,"final_path" : final_filepath})])
            os.remove(os.path.join(initial_filepath))
            db.create_post(session["username"], final_filepath, float(time.time()), re.compile(r"<.*?>").sub("", request.form["title"]), re.compile(r"<.*?>").sub("", request.form["caption"]))
            return redirect(url_for("main.profile"))
        return render_template("post.html", username=session["username"], allowed=True)
    return redirect(url_for("main.login"))

@main.route("/post/delete", methods=["POST"])
def delete_post():
    if "username" in session:
        if db.post_user_from_id(request.form["id"])[0] == session["username"]:
            try:
                os.remove(os.path.join(db.filepath_from_id(request.form["id"])[0]))
            except FileNotFoundError:
                pass
            db.delete_post(request.form["id"])
        return redirect(request.form["url"].split("#")[0])
    return redirect(url_for("main.login"))

@main.route("/comment", methods=["POST"])
def comment():
    if "username" in session:
        comment = re.compile(r"<.*?>").sub("", request.form["comment"])
        if len(comment):
            db.insert_comment(session["username"], comment, request.form["id"], time.time())
    return redirect(request.form["url"].split("#")[0] + "#" + request.form["id"])

@main.route("/comment/edit", methods=["POST"])
def edit_comment():
    if "username" in session:
        comment = re.compile(r"<.*?>").sub("", request.form["comment"])
        if len(comment):
            db.edit_comment(session["username"], comment, request.form["commentid"])
    return redirect(request.form["url"].split("#")[0] + "#" + request.form["id"])

@main.route("/comment/delete", methods=["POST"])
def delete_comment():
    if "username" in session:
        db.delete_comment(session["username"], request.form["commentid"])
    return redirect(request.form["url"].split("#")[0] + "#" + request.form["id"])

@main.route("/like", methods=["POST"])
def like():
    if "username" in session:
        if db.has_liked(session["username"], request.form["id"]):
            db.unlike_post(session["username"], request.form["id"])
            return jsonify(liked=0, likes=db.get_likes(request.form["id"]))
        db.like_post(session["username"], request.form["id"])
        return jsonify(liked=1, likes=db.get_likes(request.form["id"]))
    return redirect(url_for("main.login"))

@main.route("/browse", methods=["GET"])
def browse():
    if "username" in session:
        return render_template("browse.html", posts=db.get_post_content(session["username"]), username=session["username"])
    return redirect(url_for("main.login"))

# @main.route("/liked", methods=["GET"])
# def liked_posts():
#     if "username" in session:
#         return render_template("browse.html", posts=db.get_liked_posts(session["username"]), username=session["username"], fill=True)
#     return redirect(url_for("main.login"))

@main.route("/uploads/<user>/<filename>", methods=["GET"])
def send_file(user, filename):
    if "username" in session:
        return send_from_directory("uploads/" + user, filename)
    return redirect(url_for("main.login"))
