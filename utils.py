from itertools import count
from typing import Generator, List, Optional

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from terminaltables import AsciiTable

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
        vacancy_page = session.get(
            url="https://api.hh.ru/vacancies",
            params={'page': page, **params},
            timeout=settings.TIMEOUT,
        )
        vacancy_page.raise_for_status()
        vacancies = vacancy_page.json()
        if page >= vacancies["pages"]:
            break

        yield from vacancies["items"]


def fetch_sj_vacancies(
        session: requests.Session,
        settings: Settings,
        headers: dict,
        params: dict
) -> Generator:
    for page in count():
        vacancy_page = session.get(
            url="https://api.superjob.ru/2.0/vacancies",
            headers=headers,
            params={'page': page, **params},
            timeout=settings.TIMEOUT,
        )
        vacancy_page.raise_for_status()
        vacancies = vacancy_page.json()
        if not vacancies["more"]:
            break

        yield from vacancies["objects"]


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


def get_average_salary(salaries: List[int]) -> int:
    """Returned average salary."""
    if len(salaries) == 0:
        return 0
    return int(sum(salaries)/len(salaries))


def generate_table(salaries_stats: dict, aggregator_title: str) -> AsciiTable:
    """Returned salaries statistics in table format."""
    table_content = [
        (
            "Язык программирования",
            "Найдено вакансий",
            "Обработано вакансий",
            "Средняя зарплата"
        ),
    ]
    for lang, salary in salaries_stats.items():
        table_content.append(
            (
                lang,
                salary["vacancies_found"],
                salary["vacancies_processed"],
                salary["average_salary"],
            )
        )
    table_instance = AsciiTable(table_content, aggregator_title)
    for i in range(1, 4):
        table_instance.justify_columns[i] = "right"
    return table_instance.table
