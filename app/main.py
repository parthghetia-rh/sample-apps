from flask import Flask
import time

app = Flask(__name__)

@app.route('/')
def main():
  return "People of the world!!!! Welcome Back!! This is 2025!!!"

if __name__ == '__main__':
  port = 8080
  app.run(port=port,host='0.0.0.0') 
