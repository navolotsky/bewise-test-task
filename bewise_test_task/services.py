from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Dict, List, Optional, Union

import sqlalchemy

from . import db
from .external_services import get_questions
from .models import Question


def get_date(date_string: str) -> datetime:
    if date_string.endswith('Z'):
        date_string = date_string[:-1] + '+00:00'
    return datetime.fromisoformat(date_string)


def insert_questions_to_db(questions_data: List[Dict]) -> int:
    """Returns a number of questions failed to insert."""
    questions = [Question(question_id=data["id"], question=data["question"], answer=data["answer"],
                          airdate=get_date(data["airdate"]), created_at=get_date(data["created_at"])
                          ) for data in questions_data]
    num_failed_to_insert = 0

    # TODO: replace if possible with one of "bulk" methods later

    try:
        db.session.bulk_save_objects(questions)
        db.session.commit()
    except sqlalchemy.exc.IntegrityError as exc:
        db.session.rollback()
        if "unique" not in exc.args[0].lower():
            raise
    except Exception as exc:
        db.session.rollback()
        raise RuntimeError("got an unexpected exception") from exc
    else:
        return num_failed_to_insert

    for q in questions:
        try:
            db.session.add(q)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError as exc:
            num_failed_to_insert += 1
            db.session.rollback()
            if "unique" not in exc.args[0].lower():
                raise
        except Exception as exc:
            num_failed_to_insert += 1
            db.session.rollback()
            raise RuntimeError("got an unexpected exception") from exc

    return num_failed_to_insert


def get_last_saved_question() -> Union[Question, None]:
    return Question.query.order_by(Question.pulled_at.desc(), Question.id.desc()).first()


executor = ThreadPoolExecutor()


def _get_and_save_questions(num, max_tries):
    num_left_to_insert = num
    tries_left = max_tries
    while num_left_to_insert and (max_tries is None or tries_left):
        if max_tries is not None:
            tries_left -= 1
        _, questions_data, _ = get_questions(num_left_to_insert)
        if questions_data is None:
            continue
        num_left_to_insert = insert_questions_to_db(questions_data)


def get_and_save_to_db_exactly_given_num_questions(num: int, max_tries: Optional[int] = None) -> None:
    executor.submit(_get_and_save_questions, num, max_tries)
