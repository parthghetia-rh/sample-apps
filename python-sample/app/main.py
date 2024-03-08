from flask import Flask
import time

app = Flask(__name__)

@app.route('/')
def main():
  return "good morning world and all who inhabit it!"

if __name__ == '__main__':
  port = 8080
  app.run(port=port,host='0.0.0.0') 
