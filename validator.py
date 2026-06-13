from pydantic import ValidationError
from models import ExtractResponse


def validate_output(data):

    errors = data.get("errors", [])


    # required field checks

    if not data.get("issuer"):

        data["issuer"] = ""
        errors.append(
            "issuer missing"
        )


    if not data.get("date"):

        data["date"] = ""
        errors.append(
            "date missing"
        )


    if not data.get("totals"):

        data["totals"] = {}
        errors.append(
            "totals missing"
        )


    if not data.get("reference_ids"):

        data["reference_ids"] = []
        errors.append(
            "reference ids missing"
        )



    data["errors"] = errors



    try:

        return ExtractResponse(
            **data
        )


    except ValidationError as e:

        return ExtractResponse(

            document_type=data.get(
                "document_type",
                "unknown"
            ),

            issuer="",

            date="",

            totals={},

            reference_ids=[],

            confidence=0,

            extraction_method="failed",

            errors=[
                str(e)
            ]
        )