from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
import requests
from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev')

# MongoDB connection
MONGO_URI = os.environ.get('MONGO_URI_READ_LATER_DB')
print(f"Using MongoDB URI: {MONGO_URI}")
client = MongoClient(MONGO_URI)
db = client['read_later_db']
links_collection = db['links']

DAD_JOKE_API = "https://icanhazdadjoke.com/"

@app.route("/")
def index():
    print("Rendering index.html")
    links = list(links_collection.find())
    print(f"Found {len(links)} links")
    return render_template("links.html", links=links)

@app.route("/link/new", methods=["GET", "POST"])
def new_link():
    if request.method == "POST":
        url = request.form["url"]
        title = request.form["title"]
        description = request.form["description"]
        source = request.form.get("source", "web")
        link = {
            "url": url,
            "title": title,
            "description": description,
            "is_read": False,
            "source": source
        }
        links_collection.insert_one(link)
        flash("Link added successfully!", "success")
        return redirect(url_for("index"))
    return render_template("link_form.html", action="Create", link=None)

@app.route("/link/<id>/edit", methods=["GET", "POST"])
def edit_link(id):
    link = links_collection.find_one({"_id": ObjectId(id)})
    if not link:
        flash("Link not found!", "danger")
        return redirect(url_for("index"))
    if request.method == "POST":
        links_collection.update_one({"_id": ObjectId(id)}, {"$set": {
            "url": request.form["url"],
            "title": request.form["title"],
            "description": request.form["description"],
            "source": request.form.get("source", "web")
        }})
        flash("Link updated!", "success")
        return redirect(url_for("index"))
    return render_template("link_form.html", action="Edit", link=link)

@app.route("/link/<id>/delete", methods=["POST"])
def delete_link(id):
    links_collection.delete_one({"_id": ObjectId(id)})
    flash("Link deleted!", "success")
    return redirect(url_for("index"))

@app.route("/link/<id>/toggle_read", methods=["POST"])
def toggle_read(id):
    link = links_collection.find_one({"_id": ObjectId(id)})
    if link:
        links_collection.update_one({"_id": ObjectId(id)}, {"$set": {"is_read": not link.get("is_read", False)}})
        flash("Read status updated!", "success")
    return redirect(url_for("index"))

# Dad joke endpoint remains for fun
@app.route("/joke")
def joke():
    return jsonify({"joke": get_dad_joke()})

def get_dad_joke():
    headers = {"Accept": "application/json"}
    response = requests.get(DAD_JOKE_API, headers=headers)
    if response.status_code == 200:
        return response.json().get("joke", "No joke found!")
    return "No joke found!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True) 