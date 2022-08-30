import logging
import logging.config
import time
from typing import Optional

from requests import ConnectionError, HTTPError

from settings import LOGGING_CONFIG, Settings
from utils import (
    get_average_salary,
    get_session,
    get_vacancies_processed,
    predict_rub_salary_hh
)

logger = logging.getLogger(__file__)


def collect_hh_salary_stats() -> Optional[dict]:
    """Returned collection with salary statistics from hh.ru."""
    settings = Settings()
    session = get_session(settings=settings)
    salary_stats = {}
    for lang in settings.PROGRAMING_LANGUAGES:
        params = {
            "specialization": 1.221,
            "area": 1,
            "text": f"Программист {lang}",
        }
        try:
            hh_vacancies = session.get(
                url="https://api.hh.ru/vacancies",
                params=params,  # type: ignore
                timeout=settings.TIMEOUT,
            )
            hh_vacancies.raise_for_status()
            vacancies = hh_vacancies.json()
            predicted_salaries = [
                predict_rub_salary_hh(vacancy["salary"])
                for vacancy in vacancies["items"]
            ]
            vacancies_processed = get_vacancies_processed(
                vacancies=predicted_salaries
            )
            average_salary = get_average_salary(salaries=vacancies_processed)
            salary_stats[lang] = {
                "vacancies_found": vacancies["found"],
                "vacancies_processed": len(vacancies_processed),
                "average_salary": average_salary,
            }

        except HTTPError as err:
            message = f"Что-то пошло не так :( {err}"
            logger.error(msg=message, exc_info=True)

        except ConnectionError as err:
            message = f"Ошибка подключения :( {err}"
            logger.error(msg=message, exc_info=True)
            time.sleep(settings.TIMEOUT)

    return salary_stats


def main() -> None:
    """Main entry for analysis average salaries from hh.ru and superjob.ru."""
    print(collect_hh_salary_stats())


if __name__ == "__main__":
    logging.config.dictConfig(LOGGING_CONFIG)
    main()
