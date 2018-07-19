from collections import OrderedDict
import json
from RegisterClassConstructorMetaclass import RegisterClassConstructorMetaclass

# todo base import then factories

class Task(object):
    __metaclass__ = RegisterClassConstructorMetaclass
    currentInstanceID = 0

    def __init__(self, state=None, dependencies=None, name="Task"):
        self.name = name + "#" + str(Task.currentInstanceID)
        Task.currentInstanceID += 1

        self.state = state
        self.dependencies = dependencies

        if state is None:
            self.state = {}

        if dependencies is None:
            self.dependencies = []

        self.result = None

    def toDict(self):
        result = OrderedDict()
        resultData = OrderedDict()
        resultData['class'] = self.__class__.__name__
        resultData['state'] = self.state
        resultData['dependencies'] = self.dependenciesList()
        result[self.name] = resultData
        return result

    # def fromDict(self):

    def save(self, fileName):
        with open(fileName, 'w') as jsonFile:
            json.dump(self.toDict(), jsonFile)

    def dependenciesList(self):
        return [task.toDict() for task in self.dependencies]

    def run(self):
        raise NotImplementedError("This method is only implemented for subclasses of Task")

    def visualize(self):
        return self.run().visualize()

    def compute(self):
        if self.result is None:
            self.result = self.run().compute()
