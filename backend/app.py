import os
from dotenv import load_dotenv
from sevaksha_app import create_app
from pyngrok import ngrok

load_dotenv()

ngrok.set_auth_token(os.getenv("NGROK_AUTH_TOKEN"))

app, celery_app = create_app()

if __name__ == "__main__":
    port = 5000

    public_url = ngrok.connect(port, bind_tls=True)
    print(f"✅ Public HTTPS URL: {public_url}")

    app.run(debug=False, port=port)
