from flask import Flask, render_template, request
app = Flask(__name__)


@app.route('/', methods = ['GET', 'POST'])
def main():
    if request.method == 'GET':
        return render_template("main.html")
    
    elif request.method == 'POST':
        print(request.form)
        return request.form
    


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")