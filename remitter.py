from flask import Flask

app = Flask(__name__)

@app.route("/")
def main():
        return "<p>Remitter</p>"

logo = """
                            ||    .     .                   
... ..    ....  .. .. ..   ...  .||.  .||.    ....  ... ..  
 ||' '' .|...||  || || ||   ||   ||    ||   .|...||  ||' '' 
 ||     ||       || || ||   ||   ||    ||   ||       ||     
.||.     '|...' .|| || ||. .||.  '|.'  '|.'  '|...' .||.    
"""

print(logo)
if __name__ == '__main__':
        app.run(host="0.0.0.0", port=8080)

