import zlib
import hashlib
import shelve

from itertools import repeat
import shutil
import os
from time import sleep

class ResultsLogger:
    def __init__(self, file_name):
        self._file_name = file_name

    def log(self, r):
        s = ",".join(str(sr) for sr in r)
        with open(self._file_name, "a") as f:
            f.write(s + "\n")


class MockCSP:
    def __init__(self, path):
        self.path = path

    def get_full_path(self, file_name):
        return self.path + '/' + file_name

    def put(self, file_name, file_body):
        full_file_name = self.get_full_path(file_name)
        f = open(full_file_name, "wb")
        f.write(file_body)
        f.close()

    def get(self, file_name):
        full_file_name = self.get_full_path(file_name)
        f = open(full_file_name, "rb")
        buff = f.read()
        f.close()
        return buff

    @staticmethod
    def default_mocked_clouds(path_to_mocked_clouds, count):
        clouds = []
        for i in range(count):
            clouds.append(MockCSP(path_to_mocked_clouds + 'c' + str(i)))
        return clouds

class InMemCSP:
    def __init__(self, path):
        self.name = path
        self.d = {}

    def put(self, file_name, file_body):
        sleep(0.1)
        self.d[file_name] = file_body

    def get(self, file_name):
        sleep(0.1)
        return self.d[file_name]

    @staticmethod
    def default_mocked_clouds(path_to_mocked_clouds, count):
        clouds = []
        for i in range(count):
            clouds.append(InMemCSP(path_to_mocked_clouds + 'c' + str(i)))
        return clouds

class DropboxCSP:
    def __init__(self):
        pass

    def put(self, file_name, file_body):
        pass

    def get(self, file_name):
        pass
