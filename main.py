import logging
import logging.config
import time

from requests import ConnectionError, HTTPError

from settings import LOGGING_CONFIG, HeadHunterSettings, SuperJobSettings
from utils import (
    fetch_hh_vacancies,
    fetch_sj_vacancies,
    generate_table,
    get_average_salary,
    get_session,
    predict_rub_salary
)

logger = logging.getLogger(__file__)
logging.config.dictConfig(LOGGING_CONFIG)


def collect_hh_salary_stats() -> dict:
    """Returned collection with salary statistics from hh.ru."""
    settings = HeadHunterSettings()
    session = get_session(settings=settings)
    salary_stats = {}
    for lang in settings.PROGRAMING_LANGUAGES:
        params = {
            "specialization": settings.PROFESSIONAL_SPECIALIZATION,
            "area": settings.REGION,
            "text": f"Программист {lang}",
        }
        predicted_salaries = []
        try:
            found_count = 0
            for vacancy in fetch_hh_vacancies(
                session=session,
                settings=settings,
                params=params,
            ):
                logger.debug(msg=f"{vacancy['salary']=}")
                predicted_salary = predict_rub_salary(
                    salary=vacancy["salary"]
                )

                if not predicted_salary:
                    found_count += 1
                    continue

                predicted_salaries.append(predicted_salary)
                found_count += 1
            average_salary = get_average_salary(salaries=predicted_salaries)

            salary_stats[lang] = {
                "vacancies_found": found_count,
                "vacancies_processed": len(predicted_salaries),
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


def collect_sj_salary_stats() -> dict:
    """Returned collection with salary statistics from superjob.ru."""
    settings = SuperJobSettings()
    session = get_session(settings=settings)
    salary_stats = {}
    headers = {
        "X-Api-App-Id": settings.SUPERJOB_API_KEY
    }
    for lang in settings.PROGRAMING_LANGUAGES:
        params = {
            "catalogues": settings.PROFESSIONAL_SPECIALIZATION,
            "town": settings.REGION,
            "keyword": lang,
        }
        predicted_salaries = []
        try:
            found_count = 0
            for vacancy in fetch_sj_vacancies(
                session=session,
                settings=settings,
                headers=headers,
                params=params,
            ):
                logger.debug(msg=f"{vacancy=}")
                predicted_salary = predict_rub_salary(
                    salary={
                        "from": vacancy["payment_from"],
                        "to": vacancy["payment_to"],
                        "currency": vacancy["currency"],
                    },
                    currency_title="rub"
                )

                if not predicted_salary:
                    found_count += 1
                    continue

                predicted_salaries.append(predicted_salary)
                found_count += 1

            average_salary = get_average_salary(salaries=predicted_salaries)
            salary_stats[lang] = {
                "vacancies_found": found_count,
                "vacancies_processed": len(predicted_salaries),
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
    salary_hh_stats = collect_hh_salary_stats()
    salary_sj_stats = collect_sj_salary_stats()
    print(
        generate_table(
            salaries_stats=salary_hh_stats,
            aggregator_title="HeadHunter Moscow"
        )
    )
    print(
        generate_table(
            salaries_stats=salary_sj_stats,
            aggregator_title="SuperJob Moscow"
        )
    )


if __name__ == "__main__":
    main()
