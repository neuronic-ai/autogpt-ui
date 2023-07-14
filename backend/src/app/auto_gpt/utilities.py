import ast
from autogpt.logs import logger


def extract_json_from_response(response_content: str) -> dict:
    # Sometimes the response includes the JSON in a code block with ```
    opening_bracket_index = response_content.find("{")
    if opening_bracket_index > 0:
        response_content = response_content[opening_bracket_index:]
    if response_content.startswith("```"):
        response_content = response_content.split("```", 1)[1]
    if response_content.endswith("```"):
        response_content = response_content.rsplit("```", 1)[0]

    # response content comes from OpenAI as a Python `str(content_dict)`, literal_eval reverses this
    try:
        return ast.literal_eval(response_content)
    except BaseException as e:
        logger.error(f"Error parsing JSON response with literal_eval {e}")
        return {}
