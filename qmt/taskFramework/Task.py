from dask import delayed

# todo base import then factories

class Task(object):

    def __init__(self, state=None, dependencies=None, name="Task"):
        self.name = name

        self.state = state
        self.dependencies = dependencies

        if state is None:
            self.state = {}

        if dependencies is None:
            self.dependencies = []

        self.result = None


    def toDict(self):
        return {self.name: {'state': self.state, 'dependencies': self.dependenciesDict()}}

    def dependenciesDict(self):
        return {task.name: task.toDict() for task in self.dependencies}

    def run(self):
        pass

    def visualize(self):
        return self.run().visualize()

    def compute(self):
        self.result = self.run().compute()


