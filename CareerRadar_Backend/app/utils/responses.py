"""Consistent JSON response helpers."""

from flask import jsonify


def success(data=None, message=None, status_code=200, **extra):
    payload = {"success": True}
    if message is not None:
        payload["message"] = message
    if data is not None:
        payload["data"] = data
    payload.update(extra)
    return jsonify(payload), status_code
