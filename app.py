from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

@app.route("/")
def serve_index():
    return render_template("index.html")

@app.route("/gif/<filename>")
def serve_gif(filename):
    return send_from_directory("static", filename)

# Health check route (for Azure)
@app.route("/robots933456.txt")
def robots():
    return "User-agent: *\nDisallow:", 200, {"Content-Type": "text/plain"}

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
