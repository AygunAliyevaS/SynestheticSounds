from flask import Flask
import os

app = Flask(__name__)

@app.route("/")
def home():
    return "giood"

if __name__ == "__main__":
    port = os.environ.get("PORT")
    if port is None:
        print("⚠️  No PORT variable found! Defaulting to 8000")
        port = 8000
    else:
        print(f"✅ PORT variable detected: {port}")
    app.run(host="0.0.0.0", port=int(port), debug=False)


