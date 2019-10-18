# -*- coding: utf-8 -*-

import json
from typing import List

import bs4
import requests

from CambridgeLMS.objects import Lesson, Tab, Unit
from CambridgeLMS.urls import URLS
from CambridgeLMS.utils import get_random_code

API_KEY = '3_IetkykgAbd85mRZSn7vlq2bO_SoniDE4BZToGJTdLsoXtdEfintM85o3cVKnQ_Vv'
API_KEY_TWO = '3_SeTeHe4Ovfob_OvhCewySB2QLSdzMIurs0VmsJXG8zKahPJrMsqNsbSPljN77Eed'


class LMS:
    def __init__(self):
        self.s = requests.Session()

        self.tabs: List[Tab] = []
        self.class_url = None

        self.status = False

    def is_auth(self) -> bool:
        return self.status

    def auth(self, login: str, password: str):
        random_code = get_random_code()

        response = self.s.post(URLS['auth']['login'], params={
            'context': random_code,
        }, data={
            'loginID': login,
            'password': password,
            'sessionExpiration': 0,
            'targetEnv': 'jssdk',
            'include': 'profile,data,emails,subscriptions,preferences',
            'includeUserInfo': True,
            'loginMode': 'standard',
            'lang': 'en',
            'APIKey': API_KEY_TWO,
            'source': 'showScreenSet',
            'sdk': 'js_latest',
            'authMode': 'cookie',
            'pageURL': URLS['auth']['init'],
            'format': 'jsonp',
            'callback': 'gigya.callback',
            'context': random_code,
            'utf8': ' &#x2713;'
        })

        data = json.loads(response.content.decode().split('callback(')[-1].split(');')[0])

        if data['statusCode'] == 403:
            self.status = False
            print(data['errorMessage'])

        else:
            self.status = True

            print('Successful authorized!')

            profile = data['profile']
            print()
            print('\t', profile['firstName'], profile['lastName'], '\t|', data['data']['clms']['role'].title())
            print('\t', '%s.%s.%s' % (profile['birthDay'], profile['birthMonth'], profile['birthYear']), '\t\t|',
                  profile['age'])
            print()

            self.s.post('https://www.cambridgelms.org/main/p/raas-login', data={
                'eventName': 'login',
                'remember': 'False',
                'provider': '',
                'loginMode': 'standard',
                'newUser': 'False',
                'UIDSignature': data['UIDSignature'],
                'signatureTimestamp': data['signatureTimestamp'],
                'UID': data['UID'],
                'profile': data['profile'],
                'data': data['data'],
                'isGlobal': True,
                'fullEventName': 'accounts.login',
                'source': 'showScreenSet',
            })

            self.s.cookies.set('glt_%s' % API_KEY_TWO, data['sessionInfo']['login_token'])
            self.s.cookies.set('org.springframework.web.servlet.i18n.CookieLocaleResolver.LOCALE', 'en')

    def __get_unit_tasks__(self, tab: Tab, unit: Unit):
        response = self.s.post(URLS['main']['unittasks'], data={
            'item_id': unit.item_id,
            'ccm_id': unit.ccm_id,
            'course_id': unit.course_id,
            'class_id': unit.class_id,
            'tab_id': tab.id,
            'level': 1,
            'visibility': True,
            'user_id': unit.user_id,
            'is_from_wa': unit.is_from_wa,
        })

        soup = bs4.BeautifulSoup(response.content, 'html.parser')

        lessons = soup.find_all('li', {'class': 'each-lesson'})
        if not lessons:
            return unit.add_lessons(self.__get_lesson_tasks__(content=soup.find_all('li', {'class': 'each-content'})))

        for lesson_obj in lessons:
            obj = lesson_obj.find('span')

            lessons = self.__get_lesson_tasks__(tab, unit, Lesson(
                ccm_id=obj.get('ccm_id'),
                class_id=obj.get('class_id'),
                course_id=obj.get('course_id'),
                item_id=obj.get('item_id'),
                expand_item_id=obj.get('expand_item_id'),
                user_id=obj.get('user_id'),
                title=obj.get('title'),
                url=obj.get('href'),
            ))

            unit.add_lessons(lessons)

    def __get_lesson_tasks__(self, tab: Tab = None, unit: Unit = None,
                             lesson: Lesson = None, content=None) -> List[Lesson]:
        if content is None:
            if lesson.ccm_id:
                return []

            response = self.s.post(URLS['main']['lessontasks'], data={
                'item_id': lesson.item_id,
                'course_id': lesson.course_id,
                'class_id': lesson.class_id,
                'tab_id': tab.id,
                'level': 2,
                'visibility': True,
                'user_id': lesson.user_id,
                'is_from_wa': unit.is_from_wa,
            })

            soup = bs4.BeautifulSoup(response.content, 'html.parser')
            content = soup.find_all('li', {'class': 'each-content'})

        lessons = []

        for lesson_obj in content:
            obj = lesson_obj.find('a')

            if obj is None:
                continue

            lesson = Lesson(
                class_id=-1,
                course_id=-1,
                item_id=-1,
                expand_item_id=-1,
                user_id=-1,
                title=obj.get('title'),
                url=obj.get('href'),
            )

            lessons.append(lesson)

        return lessons

    def update_tabs(self):
        print('\nLoading data ...\n')

        response = self.s.get(self.class_url)

        soup = bs4.BeautifulSoup(response.content, 'html.parser')

        tab_menu = soup.find('nav', {'class': 'search-tab-menu'})

        if not self.tabs:
            for tab in tab_menu.find_all('a'):
                tab_object = Tab(
                    tab_id=int(tab.get('tab_id')),
                    url=tab.get('href'),
                    title=tab.get('title')
                )
                self.tabs.append(tab_object)

        for tab in self.tabs:
            print(tab.title)

            response = self.s.get(tab.url)
            soup = bs4.BeautifulSoup(response.content, 'html.parser')
            units = soup.find('ul', {'class': 'units'}).find_all('li', {'class': 'each-unit'})

            for index, unit_obj in enumerate(units):
                span = unit_obj.find('span')
                percent = int(unit_obj.find('span', {'class': 'progress-percent'}).get('data-score'))
                unit = Unit(
                    ccm_id=int(span.get('ccm_id')),
                    class_id=int(span.get('class_id')),
                    course_id=int(span.get('course_id')),
                    expand_item_id=int(span.get('expand_item_id')),
                    is_from_wa=span.get('is_from_wa'),
                    item_id=int(span.get('item_id')),
                    title=span.get('title'),
                    user_id=int(span.get('user_id')),
                    percent=percent
                )
                tab.units.append(unit)

                self.__get_unit_tasks__(tab, unit)

                print('%s)' % (index + 1), unit.title, '{}%'.format(unit.percent), '%s lessons' % len(unit.lessons),
                      sep=' | ')

            print()

    def load(self, reload_data=False):
        status = False
        if not reload_data:
            status = self.load_from_file()

        if not status:
            response = self.s.get(URLS['main']['frontpage'])

            soup = bs4.BeautifulSoup(response.content, 'html.parser')

            self.class_url = soup.find('div', {'class': 'my-teaching-class'}).find('a').find('span').get('data-href')

            print('My class url:', self.class_url)

            self.update_tabs()

            self.save_to_file()

    def load_from_file(self, filepath='data.json'):
        try:
            with open(filepath, mode='r', encoding='utf-8') as file:
                data = json.load(file)

                for tab_data in data:
                    tab = Tab(tab_data['id'], tab_data['url'], tab_data['title'])

                    for unit_data in tab_data['units']:
                        unit = Unit(
                            ccm_id=unit_data['ccm_id'],
                            class_id=unit_data['class_id'],
                            course_id=unit_data['course_id'],
                            expand_item_id=unit_data['expand_item_id'],
                            is_from_wa=unit_data['is_from_wa'],
                            item_id=unit_data['item_id'],
                            title=unit_data['title'],
                            user_id=unit_data['user_id'],
                            percent=unit_data['percent']
                        )

                        for lesson_data in unit_data['lessons']:
                            lesson = Lesson(
                                class_id=lesson_data['class_id'],
                                course_id=lesson_data['course_id'],
                                item_id=lesson_data['item_id'],
                                expand_item_id=lesson_data['expand_item_id'],
                                title=lesson_data['title'],
                                user_id=lesson_data['user_id'],
                                url=lesson_data['url'],
                                ccm_id=lesson_data['ccm_id']
                            )
                            unit.lessons.append(lesson)

                        tab.units.append(unit)

                    self.tabs.append(tab)
            print('Data loaded successfully!')
            return True

        except (BaseException, Exception):
            return False

    def save_to_file(self, filepath='data.json'):
        with open(filepath, mode='w', encoding='utf-8') as file:
            file.write(json.dumps([tab.json() for tab in self.tabs], indent=2, ensure_ascii=False))
        print('Data saved successfully!')

    def solve(self, units: List[Unit]):
        for unit in units:
            for lesson in unit.lessons:
                print(lesson.title, '|', lesson.url)

                response = self.s.get(lesson.url)
                soup = bs4.BeautifulSoup(response.content, 'html.parser')

                launch_url = soup.find('iframe', {'id': 'content-iframe'}).get('src')

                response = self.s.get(launch_url)
                js_url = response.content.decode().split('PathToCourse = ')[-1].split(';')[0]
                course_url = js_url.replace('\\x3a', ':').replace('\\x2f', '/').replace('\\x5f', '_').strip("'")

                print(course_url)

                response = self.s.get(course_url + '/data/config.json')
                data_file = response.json()['activitites'][0]['datafile']

                response = self.s.get(course_url + '/data/' + data_file)

                from pprint import pprint
                pprint(response.json())

                exit()

    def ui(self):
        page = 'main'

        print('\n\nAutosolver for Cambridge LMS | Ready to work!\n')

        data = {}

        while True:
            try:
                start_message = 'Unknown message?'

                if page == 'main':
                    start_message = '1) Solve all tasks\n2) Choose tasks\n'

                elif page == 'choose_tabs':
                    start_message = '1) Back to main menu\n'

                    for index, tab in enumerate(self.tabs):
                        start_message += '%s) %s\n' % (index + 2, tab.title)

                elif page == 'choose_units':
                    start_message = '1) Back to tabs\n2) Select all\n'

                    for index, unit in enumerate(self.tabs[data['tab']].units):
                        start_message += '%s) %s\n' % (index + 3, unit.title)

                elif page == 'in_start':
                    tab = self.tabs[data['tab']]
                    if data['unit'] == -1:
                        units = tab.units
                    else:
                        units = [tab.units[data['unit']], ]
                    data['units'] = units

                    start_message = 'Your selected data:\n\nTab: %s\nUnits:\n' % tab.title

                    for unit in units:
                        start_message += '%s\n' % unit.title

                    start_message += '\n1) Back to main menu\n2) Start to solve'

                print(start_message, end='\n\n')

                command = input('Enter your command: ')

                end_message = '! Invalid command "%s"' % command

                if command.isdigit():
                    command = int(command)

                    if page == 'main':
                        if command == 1:
                            end_message = '\n\nI began to solve all tasks ...\n'

                        elif command == 2:
                            page = 'choose_tabs'
                            end_message = None

                    elif page == 'choose_tabs':
                        if command == 1:
                            page = 'main'
                            end_message = None

                        elif command in range(2, len(self.tabs) + 2):
                            print('I WRITE TO DATA')
                            page = 'choose_units'
                            end_message = None
                            data['tab'] = command - 2

                    elif page == 'choose_units':
                        if command == 1:
                            page = 'choose_tabs'
                            end_message = None

                        elif command in range(2, len(self.tabs[data['tab']].units) + 3):
                            page = 'in_start'
                            end_message = None
                            data['unit'] = command - 3

                    elif page == 'in_start':
                        if command == 1:
                            page = 'main'
                            end_message = None

                        elif command == 2:
                            page = 'main'
                            end_message = None

                            self.solve(data['units'])

                if end_message is not None:
                    print(end_message, end='\n\n')

            except EOFError:
                break
