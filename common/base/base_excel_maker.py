#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@File    ：base_excel_maker.py
@Author  ：zhaolin
@Date    ：2022/1/10 16:07 
"""
import openpyxl


class BaseExcelMaker:
    def __init__(self, title=""):
        self.workbook = openpyxl.Workbook()
        self.worksheet = self.workbook.active
        self.worksheet.title = title

    def make_header(self):
        raise NotImplementedError("you must implement this method")

    def make_excel(self, queryset, file_name=""):
        raise NotImplementedError("you must implement this method")

    def save_excel(self, file_name):
        self.workbook.save(file_name)
