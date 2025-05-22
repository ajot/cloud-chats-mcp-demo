from flask import Flask, render_template, jsonify
import requests

app = Flask(__name__)

DAD_JOKE_API = "https://icanhazdadjoke.com/"

@app.route("/")
def index():
    joke = get_dad_joke()
    return render_template("index.html", joke=joke)

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