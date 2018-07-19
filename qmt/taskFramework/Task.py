from collections import OrderedDict


# todo base import then factories

class Task(object):

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
        resultData['state'] = self.state
        resultData['dependencies'] = self.dependenciesDict()
        result[self.name] = resultData
        return result

    # def fromDict(self):

    def dependenciesDict(self):
        result = OrderedDict()
        for task in self.dependencies:
            result[task.name] = task.toDict()
        return result

    def run(self):
        pass

    def visualize(self):
        return self.run().visualize()

    def compute(self):
        if self.result is None:
            self.result = self.run().compute()
