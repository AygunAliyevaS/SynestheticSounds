from flask import Flask, send_from_directory

app = Flask(__name__)

@app.route("/")
def serve_index():
    # Serve index.htm from the same folder as app.py
    return send_from_directory(".", "index.htm")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
