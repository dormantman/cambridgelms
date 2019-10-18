# -*- coding: utf-8 -*-

from CambridgeLMS.lms import LMS

from config import LOGIN, PASSWORD

lms = LMS()
lms.auth(LOGIN, PASSWORD)

if lms.is_auth():
    lms.load()
    lms.ui()
