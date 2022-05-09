from typing import Dict

from flask import jsonify, make_response, request

from . import app
from .services import get_and_save_to_db_exactly_given_num_questions, get_last_saved_question
from .validation import validate_questions_num


@app.route('/', methods=["POST"])
def index():
    questions_num_field_name = "questions_num"

    data: Dict = request.get_json(force=True)
    if not isinstance(data, dict):
        return make_response(jsonify(non_field_errors=["payload must be JSON object"]), 400)

    questions_num = data.get(questions_num_field_name)
    if not isinstance(questions_num, int) or questions_num <= 0:
        return make_response(jsonify(field_errors={questions_num_field_name: "positive integer required"}), 400)
    msg = validate_questions_num(questions_num, just_return_msg=True)
    if msg:
        return make_response(jsonify(field_errors={questions_num_field_name: msg}), 400)

    try:
        q = get_last_saved_question()
        return jsonify(last_saved_question=q.to_dict() if q is not None else {})
    finally:
        get_and_save_to_db_exactly_given_num_questions(questions_num)
