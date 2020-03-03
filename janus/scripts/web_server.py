#!/usr/bin/env python3

from flask import Flask, render_template, request


app = Flask(__name__)


@app.route("/<int:id>/streaming.js", methods=["GET"])
def streaming_js(id):
    ip = request.host.split(':')[0]
    return render_template("streaming.js.j2", id=id, ip=ip)


@app.route("/<int:id>", methods=["GET"])
def streaming_html(id):
    return render_template("streaming.html.j2", id=id)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port='80', threaded=True, use_reloader=False)
