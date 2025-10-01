from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

@app.route("/")
def serve_index():
    return render_template("index.html")

# Add route for serving GIFs (referenced in the HTML)
@app.route("/gif/<filename>")
def serve_gif(filename):
    return send_from_directory("static", filename)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
