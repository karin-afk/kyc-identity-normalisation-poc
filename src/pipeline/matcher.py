def fields_match(result: dict, expected_normalised: str) -> bool:
    """
    Check if the pipeline result matches the expected normalised value.
    Also accepts any value in allowed_variants.
    """
    actual = result.get("normalised_form", "")
    if actual == expected_normalised:
        return True
    variants = result.get("allowed_variants", [])
    return expected_normalised in [v.upper() for v in variants]
