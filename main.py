import logging
import logging.config
import time
from typing import Optional

from requests import ConnectionError, HTTPError

from settings import LOGGING_CONFIG, Settings, SuperJobSettings
from utils import (
    fetch_hh_vacancies,
    get_average_salary,
    get_session,
    get_vacancies_processed,
    predict_rub_salary
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
        predicted_salaries = []
        try:
            for vacancy in fetch_hh_vacancies(
                session=session,
                settings=settings,
                params=params,
            ):
                predicted_salaries.append(
                    predict_rub_salary(vacancy["salary"])
                )
                logger.debug(msg=f"{vacancy['salary']=}")
            vacancies_processed = get_vacancies_processed(
                vacancies=predicted_salaries
            )
            average_salary = get_average_salary(salaries=vacancies_processed)
            salary_stats[lang] = {
                "vacancies_found": len(predicted_salaries),
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


def collect_sj_salary_stats() -> Optional[dict]:
    """Returned collection with salary statistics from superjob.ru."""
    settings = SuperJobSettings()
    session = get_session(settings=settings)
    salary_stats = {}
    headers = {
        "X-Api-App-Id": settings.SUPERJOB_API_KEY
    }
    for lang in settings.PROGRAMING_LANGUAGES:
        params = {
            "town": 4,
            "catalogues": 48,
            "keyword": lang,
        }
        try:
            sj_vacancies = session.get(
                url="https://api.superjob.ru/2.0/vacancies",
                params=params,  # type: ignore
                headers=headers,
                timeout=settings.TIMEOUT,
            )
            sj_vacancies.raise_for_status()
            vacancies = sj_vacancies.json()
            predicted_salaries = [
                predict_rub_salary(
                    {
                        "from": vacancy["payment_from"],
                        "to": vacancy["payment_to"],
                        "currency": vacancy["currency"],
                    },
                    currency_title="rub"
                )
                for vacancy in vacancies["objects"]
            ]

            vacancies_processed = get_vacancies_processed(
                vacancies=predicted_salaries
            )
            average_salary = get_average_salary(salaries=vacancies_processed)
            salary_stats[lang] = {
                "vacancies_found": vacancies["total"],
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
    print(collect_sj_salary_stats())


if __name__ == "__main__":
    logging.config.dictConfig(LOGGING_CONFIG)
    main()
