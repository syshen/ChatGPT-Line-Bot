import json
import datetime


class FileStorage:
    def __init__(self, file_name):
        self.fine_name = file_name
        self.history = {}

    def save(self, data):
        self.history.update(data)
        with open(self.fine_name, "w", newline="") as f:
            json.dump(self.history, f)

    def load(self):
        with open(self.fine_name, newline="") as jsonfile:
            data = json.load(jsonfile)
        self.history = data
        return self.history


class Storage:
    def __init__(self, storage):
        self.storage = storage

    def save(self, data):
        self.storage.save(data)

    def load(self):
        return self.storage.load()
