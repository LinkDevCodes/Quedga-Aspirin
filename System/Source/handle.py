import re
import os
from typing import *


temp = []


# 冒泡排序
def bubble_sort(array: list) -> list:
    length: int = len(array)
    for i in range(length - 1):
        for j in range(length - i - 1):
            if array[j] > array[j + 1]:
                array[j], array[j + 1] = array[j + 1], array[j]
    return array


# 快速排序
def quick_sort(array: list) -> list:
    if len(array) <= 1:
        return array
    else:
        pivot = array[0]
        less = [x for x in array[1:] if x <= pivot]
        greater = [x for x in array[1:] if x > pivot]
        return quick_sort(less) + [pivot] + quick_sort(greater)


# 描述转换集类
class DescribeCollection:
    collections: set
    value: None

    def __init__(self, collections: set, value) -> None:
        self.collections, self.value = collections, value
        if not self.collections is {}:
            _L = list(self.collections)
            standard = type(_L[0])
            self.collections = set([value for value in _L if type(value) == standard])

    def addCollection(self, collection):
        if type(collection) == set or type(collection) == list or type(collection) == tuple:
            self.collections = self.collections | set(collection) if type(collection) != set else collection
            return self.collections
        else:
            return self.collections.add(collection if type(collection) == type(list(self.collections)[0]) else 0) if \
                not self.collections is {} else self.value

    def check(self, _input) -> bool:
        return self.value if _input in self.collections else None


# 双正序数据修正
def sizeOfDataCorrection_ascending(data: list or tuple) -> tuple:
    x, y = tuple(data) if type(data) == list else data
    return (y, x) if x > y else (x, y)


# 双降序数据修正
def sizeOfDataCorrection_descending(data: list or tuple) -> tuple:
    x, y = tuple(data) if type(data) == list else data
    return (y, x) if x < y else (x, y)


# 带有逗号字符串切割为元组
def tupleCommasString(String: str) -> Tuple:
    return tuple(re.split(',', String))


# 任意字符串切割为类型为元组
def tupleString(String: str, seq: str) -> Tuple:
    return tuple([index for index in re.split(seq, String)])


# 任意字符串切割为类型为整型的元组
def intTupleString(String: str, seq: str) -> Tuple[int]:
    return tuple([int(index) for index in re.split(seq, String)])


# 带有逗号字符串切割为类型为整型的元组
def intTupleCommasString(String: str) -> Tuple[int]:
    return tuple([int(index) for index in re.split(',', String)])


# 遍历目录下所有文件
def traverse_files(path) -> temp:
    global temp
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path):
            traverse_files(file_path)
        else:
            temp.append(file_path)
    return temp


# 遍历目录下所有文件(格式化)
def traverse_filesFormat(path) -> temp:
    global temp
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isdir(file_path) and 'venv' not in file_path and '.idea' not in file_path:
            traverse_filesFormat(file_path)
        else:
            temp.append(f"Read:Processing file {file_path}")
    return temp

