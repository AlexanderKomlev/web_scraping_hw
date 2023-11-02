from tqdm import tqdm
from bs4 import BeautifulSoup

import requests
import fake_headers
import re
import json


def get_html(url):
    headers_gen = fake_headers.Headers(os='win', browser='opera')
    response = requests.get(url, headers=headers_gen.generate())
    return response.text


def scraping(url):
    main_soup = BeautifulSoup(get_html(url), 'lxml')

    vacancies_list_tag = main_soup.find_all('div', class_='vacancy-serp-item-body__main-info')

    vacancies_data = {}
    pattern1 = r'django'
    pattern2 = r'flask'
    pbar = tqdm(vacancies_list_tag, colour='blue')

    for idx, vacancy_tag in enumerate(pbar):
        a_tag = vacancy_tag.find('a', class_='serp-item__title')
        vacancy_link = a_tag['href']

        vacancy_soup = BeautifulSoup(get_html(vacancy_link), 'lxml')
        vacancy_desc = vacancy_soup.find('div', class_='g-user-content').text.lower()

        if len(re.findall(pattern1, vacancy_desc)) >= 1 and len(re.findall(pattern2, vacancy_desc)) >= 1:
            city_tag = vacancy_tag.find_all('div', class_='bloko-text')[1]
            company_name = vacancy_tag.find('a', class_='bloko-link bloko-link_kind-tertiary')
            vacancy_name = vacancy_tag.find('a', class_='serp-item__title')
            vacancy_salary = vacancy_tag.find('span', class_='bloko-header-section-2')

            if vacancy_name not in vacancies_data.keys():
                key = vacancy_name.text
                vacancies_data.update({key: None})
            else:
                key = f'{vacancy_name.text}({idx})'
                vacancies_data.update({key: None})

            company_name_fix = company_name.text.replace('\xa0', ' ')
            city = city_tag.text.split(',')[0]

            vacancies_data[key] = {
                'company_name': company_name_fix,
                'city': city,
                'link': vacancy_link
            }

            if vacancy_salary:
                vacancy_salary_fix = vacancy_salary.text.replace('\u202F', ' ')
                vacancies_data[key].update({'salary': vacancy_salary_fix})
            else:
                vacancies_data[key].update({'salary': 'з/п не указана'})

    return vacancies_data


# Поиск вакансий с ЗП в долларах(USD)
def scraping2(url):
    main_soup = BeautifulSoup(get_html(url), 'lxml')

    vacancies_list_tag = main_soup.find_all('div', class_='vacancy-serp-item-body__main-info')

    vacancies_data = {}
    pattern1 = r'django'
    pattern2 = r'flask'
    pbar = tqdm(vacancies_list_tag)

    for idx, vacancy_tag in enumerate(pbar):
        a_tag = vacancy_tag.find('a', class_='serp-item__title')
        vacancy_link = a_tag['href']

        vacancy_soup = BeautifulSoup(get_html(vacancy_link), 'lxml')
        vacancy_desc = vacancy_soup.find('div', class_='g-user-content').text.lower()
        vacancy_salary = vacancy_tag.find('span', class_='bloko-header-section-2')

        if vacancy_salary and vacancy_salary.text.split(' ')[-1] == '$':
            if len(re.findall(pattern1, vacancy_desc)) >= 1 and len(re.findall(pattern2, vacancy_desc)) >= 1:
                city_tag = vacancy_tag.find_all('div', class_='bloko-text')[1]
                company_name = vacancy_tag.find('a', class_='bloko-link bloko-link_kind-tertiary')
                vacancy_name = vacancy_tag.find('a', class_='serp-item__title')

                if vacancy_name not in vacancies_data.keys():
                    key = vacancy_name.text
                    vacancies_data.update({key: None})
                else:
                    key = f'{vacancy_name.text}({idx})'
                    vacancies_data.update({key: None})

                company_name_fix = company_name.text.replace('\xa0', ' ')
                city = city_tag.text.split(',')[0]

                vacancies_data[key] = {
                    'company_name': company_name_fix,
                    'city': city,
                    'link': vacancy_link
                }

                if vacancy_salary:
                    vacancy_salary_fix = vacancy_salary.text.replace('\u202F', ' ')
                    vacancies_data[key].update({'salary': vacancy_salary_fix})
                else:
                    vacancies_data[key].update({'salary': 'з/п не указана'})

    return vacancies_data


def write_file(data):
    with open("data.json", "w", encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    URL = "https://spb.hh.ru/search/vacancy?area=1&area=2&search_field=name&search_field=company_name&search_field=description&enable_snippets=false&excluded_text=&text=python"

    write_file(scraping(URL))
