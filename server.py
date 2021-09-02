""" SERVER INITIALIZATION AND CONFIG """
import os
import json
from utils import Utils
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import default_exceptions
from flask_cors import CORS, cross_origin
from functools import wraps
from waitress import serve
from flask import (
    jsonify,
    request,
    abort,
)
from dotenv import load_dotenv
from os.path import join, dirname
load_dotenv(join(dirname(__file__), ".env"))  # load environment variables into scope


app = Utils.Config().get_app_with_db_configured()



""" API DECORATORS AND CONFIG """
@app.errorhandler(Exception)
def handle_error(e):
    code = 500
    if isinstance(e, HTTPException):
        code = e.code
    return jsonify(error=str(e)), code


for ex in default_exceptions:
    app.register_error_handler(ex, handle_error)


""" allows cross origin communication """
CORS(app, support_credentials=True)



""" Controllers """
from controllers import PostController
PostController = PostController.PostController()


# API authentication route decorator
def require_appkey(view_function):
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        if request.args.get("key") and request.args.get("key") == os.environ["API_KEY"]:
            return view_function(*args, **kwargs)
        else:
            abort(401)

    return decorated_function



""" ROUTES """
@app.route("/api/ping")
@cross_origin(supports_credentials=True)
# @require_appkey       # UNCOMMENT LINE WHEN AUTHENICATED API DESIRED
def basic_ping():

    response = app.response_class(
        response=json.dumps({"success" : True}),
        status=200,
        mimetype="application/json",
    )

    return response


@app.route("/api/posts", methods=["GET"])
@cross_origin(supports_credentials=True)
# @require_appkey       # UNCOMMENT LINE WHEN AUTHENICATED API DESIRED
def process_post():
    

    response, status = PostController.find_relevant_posts(request.args)


    response = json.dumps(response) # convert to json

    response = app.response_class(
        response=response,
        status=status,
        mimetype="application/json",
    )

    return response



""" INSTANTIATE SERVER """
if __name__ == "__main__":
    if "PRODUCTION" in os.environ and os.environ["PRODUCTION"] == "True":
        print("Started production server .... :)")
        serve(app, host="0.0.0.0", port=5000)  # run production server
    else:
        app.run(debug=True)  # run default flask server

