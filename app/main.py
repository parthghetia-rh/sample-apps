from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
  port = 8080
  app.run(port=port,host='0.0.0.0') 
