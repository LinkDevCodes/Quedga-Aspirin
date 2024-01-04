import json
import re
import os
import configparser
import pickle
import shelve
from xml.dom.minidom import parse
import xml.dom.minidom
import pygame
from typing import *

pygame.init()


def writeJson(obj: Any, file_path: str) -> None:
    with open(file_path, encoding='utf-8', mode='w') as file:
        json.dump(obj, file)


def readJson(file_path: str) -> None:
    with open(file_path, encoding='utf-8', mode='r') as file:
        return json.load(file)


class xmlReader(object):
    DOMTree, collections = None, None

    def __init__(self, path: str) -> None:
        self.DOMTree = xml.dom.minidom.parse(path)
        self.collection = self.DOMTree.documentElement

    def __stop(self) -> None:
        raise Warning()

    def __judge_pattern(self, inputInterface: str or list) -> list:
        if type(inputInterface[0]) == list:
            outInterface = inputInterface[0]
        else:
            outInterface = inputInterface
        return outInterface

    def get_data(self, *setList: str or list) -> str:
        setList = self.__judge_pattern(setList)
        objectMain = None
        objectCopy = self.collection.getElementsByTagName(setList[0])
        if len(setList) == 1:
            objectMain = self.collection.getElementsByTagName(setList[0])
        for SET in setList:
            if SET != setList[0]:
                objectMain = objectCopy[0].getElementsByTagName(SET)
                objectCopy = objectMain
        return objectMain[0].childNodes[0].data

    def get_datas(self, *setList: str or list) -> tuple:
        setList = self.__judge_pattern(setList)
        objectMain = None

        def embed(source: list, push: list) -> list:
            return source + push

        def boost(objects: list, setts: str) -> list:
            returnList = []
            for label in objects:
                returnList = embed(source=returnList, push=label.getElementsByTagName(setts))
            return returnList

        returnTuple = []
        objectCopy = self.collection.getElementsByTagName(setList[0])
        if len(setList) == 1:
            objectMain = self.collection.getElementsByTagName(setList[0])
        SET: str
        for SET in setList:
            if SET != setList[0]:
                objectCopy = boost(objects=objectCopy, setts=SET)
        objectMain = objectCopy
        for elementObject in objectMain:
            returnTuple.append(elementObject.childNodes[0].data)
        return tuple(returnTuple)

    def get_attribute(self, *setList: str or list, attribute: str) -> str:
        setList = self.__judge_pattern(setList)
        objectMain = None
        objectCopy = self.collection.getElementsByTagName(setList[0])
        if len(setList) == 1:
            objectMain = self.collection.getElementsByTagName(setList[0])
        for SET in setList:
            if SET != setList[0]:
                objectMain = objectCopy[0].getElementsByTagName(SET)
                objectCopy = objectMain
        if objectMain[0].hasAttribute(attribute):
            return objectMain[0].getAttribute(attribute)

    def get_attributes(self, *setList: str or list, attribute: str) -> tuple:
        setList = self.__judge_pattern(setList)
        objectMain = None

        def embed(source: list, push: list) -> list:
            return source + push

        def boost(objects: list, setts: str) -> list:
            returnList = []
            for label in objects:
                returnList = embed(source=returnList, push=label.getElementsByTagName(setts))
            return returnList

        returnTuple = []
        objectCopy = self.collection.getElementsByTagName(setList[0])
        if len(setList) == 1:
            objectMain = self.collection.getElementsByTagName(setList[0])
        SET: str
        for SET in setList:
            if SET != setList[0]:
                objectCopy = boost(objects=objectCopy, setts=SET)
        objectMain = objectCopy
        for elementObject in objectMain:
            returnTuple.append(elementObject.getAttribute(attribute) if elementObject.hasAttribute(attribute) else None)
        return tuple(returnTuple)

    def get_attributesGroup(self, *setList: str or list, attributesList: list) -> tuple:
        setList = self.__judge_pattern(setList)
        objectMain = None

        def embed(source: list, push: list) -> list:
            return source + push

        def boost(objects: list, setts: str) -> list:
            returnList = []
            for label in objects:
                returnList = embed(source=returnList, push=label.getElementsByTagName(setts))
            return returnList

        returnTuple = []
        objectCopy = self.collection.getElementsByTagName(setList[0])
        if len(setList) == 1:
            objectMain = self.collection.getElementsByTagName(setList[0])
        SET: str
        for SET in setList:
            if SET != setList[0]:
                objectCopy = boost(objects=objectCopy, setts=SET)
        objectMain = objectCopy
        for elementObject in objectMain:
            unit = []
            for attributeObject in attributesList:
                unit.append(elementObject.getAttribute(attributeObject) if elementObject.hasAttribute(attributeObject) else None)
            returnTuple.append(tuple(unit))
        return tuple(returnTuple)

    def get_dataAndAttribute(self, *setList: str or list, attribute: str) -> tuple:
        setList = self.__judge_pattern(setList)
        return self.get_data(setList), self.get_attribute(setList, attribute=attribute)

    def get_datasAndAttribute(self, *setList: str or list, attribute: str) -> tuple:
        setList = self.__judge_pattern(setList)
        return self.get_datas(setList), self.get_attribute(setList, attribute=attribute)

    def get_dataAndAttributes(self, *setList: str or list, attribute: str) -> tuple:
        setList = self.__judge_pattern(setList)
        return self.get_data(setList), self.get_attributes(setList, attribute=attribute)

    def get_datasAndAttributes(self, *setList: str or list, attribute: str) -> tuple:
        setList = self.__judge_pattern(setList)
        return self.get_datas(setList), self.get_attributes(setList, attribute=attribute)

    def get_dataAndAttributesGroup(self, *setList: str or list, attributesList: list):
        setList = self.__judge_pattern(setList)
        return self.get_data(setList), self.get_attributesGroup(setList, attributesList=attributesList)

    def get_datasAndAttributesGroup(self, *setList: str or list, attributesList: list):
        setList = self.__judge_pattern(setList)
        return self.get_datas(setList), self.get_attributesGroup(setList, attributesList=attributesList)

    def get_appointedData(self, *setList: str or list, **keyAttributes) -> str:
        global data
        setList = self.__judge_pattern(setList)
        judgeBoolean = []
        for keyAttribute in keyAttributes.keys():
            data, attribute = self.get_dataAndAttributes(setList, attribute=keyAttribute)
            if keyAttributes[keyAttribute] == attribute:
                judgeBoolean.append(True)
            else:
                judgeBoolean.append(False)
        if all(judgeBoolean):
            return data
        else:
            return str(None)


    def get_appointedDatas(self, *setList: str or list, **keyAttributes) -> tuple:
        global data
        setList = self.__judge_pattern(setList)
        outList = []
        for keyAttribute in keyAttributes.keys():
            data, attribute = self.get_dataAndAttributes(setList, attribute=keyAttribute)
            for data_ in data:
                if keyAttributes[keyAttribute] == attribute:
                    outList.append(data_)
        return tuple(outList)

    def get_appointedAttribute(self, setList: str or list, attribute: str, keyData: str) -> None:
        return self.__stop()

    def get_appointedAttributes(self, setList: str or list, attribute: str, keyData: str) -> None:
        return self.__stop()

    def get_appointedAttributesGroup(self, *setList: str or list, attributesList: list, keyData: str) -> None:
        return self.__stop()

