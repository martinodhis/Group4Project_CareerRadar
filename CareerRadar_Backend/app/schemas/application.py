"""Schemas for updating tracked job applications."""

from marshmallow import fields, validate

from . import StrictSchema


class ApplicationUpdateSchema(StrictSchema):
    status = fields.String(
        validate=validate.OneOf(
            ["SAVED", "APPLIED", "SCREENING", "INTERVIEW", "OFFER", "REJECTED", "ACCEPTED"]
        )
    )
    notes = fields.String(allow_none=True)
    applied_at = fields.DateTime(allow_none=True)
    interview_date = fields.DateTime(allow_none=True)
