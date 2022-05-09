from .external_services import MAX_NUM_QUESTIONS, MIN_NUM_QUESTIONS


def validate_questions_num(num: int, *, just_return_msg: bool = False) -> str:
    if not isinstance(num, int):
        msg = f"must of the type {int}, not {type(num)}"
        if just_return_msg:
            return msg
        raise TypeError(msg)
    if num < MIN_NUM_QUESTIONS or num > MAX_NUM_QUESTIONS:
        msg = f"must be an integer in the range of [{MIN_NUM_QUESTIONS}, {MAX_NUM_QUESTIONS}]"
        if just_return_msg:
            return msg
        raise ValueError(msg)
    return ""
