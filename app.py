from flask import Flask, render_template, request, jsonify

from services.gemini_service import generate_response

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json()
    user_message = data.get("message")

    try:
        ai_response = generate_response(user_message)

        return jsonify({
            "response": ai_response
        })

    except Exception as e:
        print("Gemini error:", e)

        return jsonify({
            "error": "AI service is temporarily unavailable. Please try again."
        }), 503



if __name__ == "__main__":
    app.run(debug=True)