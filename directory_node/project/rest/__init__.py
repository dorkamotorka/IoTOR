from flask import jsonify

def respond(success: bool, message: str, code=200, data=None):
    """Creates a HTTP response that is structured in our given way.

    Example output:
        {
            "success": true,
            "message": "it worked!",
            "data": []
        }

    Parameters:
        success: If the request was successful
        message: A message to the user
        code: HTTP response code
        data: additional data for the response (payload)
    """

    result = dict(
        success=success,
        message=message
    )
    if data is not None:
        result["data"] = data

    return jsonify(result), code
