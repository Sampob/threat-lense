from app import create_app_for_flask

app = create_app_for_flask()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)