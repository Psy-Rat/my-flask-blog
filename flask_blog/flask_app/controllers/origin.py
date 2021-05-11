from ..app import app
from flask import redirect, request, abort, render_template, url_for


@app.route('/')
def homepage():
    return render_template("index.html")
