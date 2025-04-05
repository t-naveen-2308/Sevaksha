from sevaksha_app import create_app
from pyngrok import ngrok

app, celery_app = create_app()

if __name__ == "__main__":
    port = 5000

    public_url = ngrok.connect(port, bind_tls=True)
    print(f"✅ Public HTTPS URL: {public_url}")

    app.run(debug=False, port=port)
