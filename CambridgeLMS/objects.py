# -*- coding: utf-8 -*-
from typing import List


class Lesson:
    def __init__(self, class_id: int, course_id: int, item_id: int, expand_item_id: int, title: str,
                 user_id: int, url: str, ccm_id=None):
        self.ccm_id = int(ccm_id) if ccm_id is not None else None
        self.class_id = int(class_id)
        self.course_id = int(course_id)
        self.item_id = int(item_id)
        self.expand_item_id = int(expand_item_id)
        self.title = title
        self.user_id = int(user_id)
        self.url = url

    def __repr__(self):
        return '<Lesson (ccm_id:{} | class_id:{} | course_id:{} | item_id:{} |' \
               ' expand_item_id:{} | title:{} | user_id:{} | url:{})>'.format(
            self.ccm_id, self.class_id,
            self.course_id,
            self.item_id,
            self.expand_item_id,
            self.title, self.user_id,
            self.url,
        )

    def json(self):
        return {
            'ccm_id': self.ccm_id,
            'class_id': self.class_id,
            'course_id': self.course_id,
            'item_id': self.item_id,
            'expand_item_id': self.expand_item_id,
            'title': self.title,
            'user_id': self.user_id,
            'url': self.url
        }


class Tab:
    def __init__(self, tab_id: int, url: str, title: str):
        self.id = tab_id
        self.url = url
        self.title = title
        self.units: List[Unit] = []

    def json(self):
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'units': [unit.json() for unit in self.units]
        }


class Unit:
    def __init__(self, ccm_id: int, class_id: int, course_id: int, expand_item_id: int,
                 is_from_wa: str, item_id: int, title: str, user_id: int, percent: int):
        self.ccm_id = ccm_id
        self.class_id = class_id
        self.course_id = course_id
        self.expand_item_id = expand_item_id
        self.is_from_wa = is_from_wa
        self.item_id = item_id
        self.title = title
        self.user_id = user_id
        self.percent = percent
        self.lessons: List[Lesson] = []

    def add_lessons(self, lessons: List[Lesson]):
        for lesson in lessons:
            self.lessons.append(lesson)

    def json(self):
        return {
            'ccm_id': self.ccm_id,
            'class_id': self.class_id,
            'course_id': self.course_id,
            'expand_item_id': self.expand_item_id,
            'item_id': self.item_id,
            'is_from_wa': self.is_from_wa,
            'title': self.title,
            'user_id': self.user_id,
            'percent': self.percent,
            'lessons': [lesson.json() for lesson in self.lessons]
        }
