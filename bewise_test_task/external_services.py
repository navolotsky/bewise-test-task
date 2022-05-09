import enum
import os
import time
from typing import List, NamedTuple, Optional

import requests
from urllib3.util import Timeout, current_time


class GetQuestionResultStatus(enum.Enum):
    SUCCESS = enum.auto()
    BAD_DATA_RECEIVED = enum.auto()
    CLIENT_ERROR = enum.auto()
    SERVER_ERROR = enum.auto()
    CONNECTION_FAILED = enum.auto()
    TIMED_OUT = enum.auto()
    UNKNOWN_ERROR = enum.auto()


class GetQuestionResult(NamedTuple):
    status: GetQuestionResultStatus
    data: Optional[List] = None
    exception: Optional[requests.RequestException] = None


MIN_NUM_QUESTIONS = 1
MAX_NUM_QUESTIONS = 100  # due to a JService limit
HOST = os.environ.get("JSERVICE_HOST", "jservice.io")
GET_QUESTIONS_URL_PATTERN = f"https://{HOST}/api/random?count={{}}"
TIMEOUT = Timeout(connect=3.05, read=27)


def get_questions(num: int, *,
                  max_tries: int = 5, sleep_for: float = 0.5,
                  max_time: Optional[float] = 5) -> GetQuestionResult:
    if not isinstance(num, int):
        raise TypeError(f"`num` must of the type {int}, not {type(num)}")
    if num < MIN_NUM_QUESTIONS or num > MAX_NUM_QUESTIONS:
        raise ValueError(f"`num` must be an integer in the range of [{MIN_NUM_QUESTIONS}, {MAX_NUM_QUESTIONS}]")

    first_try = True
    tries_left = max_tries

    _timeout = TIMEOUT.clone()
    if max_time is not None and (TIMEOUT.total is None or TIMEOUT.total > max_time):
        _timeout.total = Timeout._validate_timeout(max_time, "total")

    status, data, exception = GetQuestionResultStatus.UNKNOWN_ERROR, None, None

    start_time = current_time()
    while tries_left:
        tries_left -= 1
        if not first_try:
            if max_time is not None and (
                    current_time() - start_time > max_time or
                    current_time() + sleep_for - start_time > max_time):
                break
            time.sleep(sleep_for)
        else:
            first_try = False

        try:
            response = requests.get(GET_QUESTIONS_URL_PATTERN.format(num), timeout=_timeout.clone())
        except requests.ConnectionError as exc:
            status, exception = GetQuestionResultStatus.CONNECTION_FAILED, exc
            continue
        except requests.Timeout as exc:
            status, exception = GetQuestionResultStatus.TIMED_OUT, exc
            continue

        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            exception = exc
            if 400 <= response.status_code < 500:
                status = GetQuestionResultStatus.CLIENT_ERROR
            elif 500 <= response.status_code < 600:
                status = GetQuestionResultStatus.SERVER_ERROR
                continue
            else:
                raise RuntimeError(f"unexpected status code {response.status_code}")
            break
        except requests.RequestException as exc:
            exception = exc
            break

        try:
            data = response.json()
        except requests.JSONDecodeError as exc:
            status, exception = GetQuestionResultStatus.BAD_DATA_RECEIVED, exc
            break
        else:
            status = GetQuestionResultStatus.SUCCESS
            break

    return GetQuestionResult(status, data, exception)
