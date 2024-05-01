from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def countdown():
    return render_template('countdown.html')


if __name__ == '__main__':
    app.run(debug=True)
