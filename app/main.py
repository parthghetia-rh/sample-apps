from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def index():
    # Define the text to display
    message = "Good morning all who inhabit it!!!!!!???"
    # Render the template with the message
    return render_template_string('<html><head><title>Beautiful Text</title></head><body><div style="font-size: 3em; text-align: center; margin-top: 20%;">{{ message }}</div></body></html>', message=message)

if __name__ == '__main__':
    app.run(debug=True)