from flask import Flask, render_template, request, jsonify

from services.gemini_service import generate_response

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()

    user_message = data["message"]

    ai_response = generate_response(user_message)

    return jsonify({
        "response": ai_response
    })


if __name__ == "__main__":
    app.run(debug=True)