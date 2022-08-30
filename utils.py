from itertools import count
from typing import Generator, List, Optional

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from settings import Settings


def get_session(
        settings: Settings
) -> requests.Session:
    """Returned new request session with retry strategy."""
    retry_strategy = Retry(
        total=settings.RETRY_COUNT,
        status_forcelist=settings.STATUS_FORCE_LIST,
        allowed_methods=settings.ALLOWED_METHODS
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)

    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def fetch_hh_vacancies(
        session: requests.Session,
        settings: Settings,
        params: dict
) -> Generator:
    """Returned vacancies from all pages hh.ru."""
    for page in count():
        page_response = session.get(
            url="https://api.hh.ru/vacancies",
            params={'page': page, **params},
            timeout=settings.TIMEOUT,
        )
        page_response.raise_for_status()
        page_data = page_response.json()
        if page >= page_data["pages"]:
            break

        yield from page_data["items"]


def fetch_sj_vacancies(
        session: requests.Session,
        settings: Settings,
        headers: dict,
        params: dict
) -> Generator:
    for page in count():
        page_response = session.get(
            url="https://api.superjob.ru/2.0/vacancies",
            headers=headers,
            params={'page': page, **params},
            timeout=settings.TIMEOUT,
        )
        page_response.raise_for_status()
        page_data = page_response.json()
        if not page_data["more"]:
            break

        yield from page_data["objects"]


def predict_rub_salary(
        salary: Optional[dict],
        currency_title: str = "RUR"
) -> Optional[int]:
    """Predicted rub salary from vacancy hh.ru."""
    if not salary or salary["currency"] != currency_title:
        return None

    if salary["from"] and salary["to"]:
        salary = salary["from"] + salary["to"] / 2
    elif salary["from"]:
        salary = salary["from"] * 1.2
    elif salary["to"]:
        salary = salary["to"] * 0.8
    else:
        return None

    return int(salary)  # type: ignore


def get_vacancies_processed(vacancies: List[Optional[int]]) -> List[int]:
    """Returned collection of only specified salaries."""
    specified_salary_vacancies = []
    for specified_salary_vacancy in vacancies:
        if not specified_salary_vacancy:
            continue
        specified_salary_vacancies.append(specified_salary_vacancy)
    return specified_salary_vacancies


def get_average_salary(salaries: List[int]) -> int:
    """Returned average salary."""
    if len(salaries) == 0:
        return 0
    return int(sum(salaries)/len(salaries))
