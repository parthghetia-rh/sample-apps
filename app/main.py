from flask import Flask
import time

app = Flask(__name__)

@app.route('/')
def main():
  return "People of this world!! Welcome Back! This is 2025!!! What's up!!!"

if __name__ == '__main__':
  port = 8080
  app.run(port=port,host='0.0.0.0') 
