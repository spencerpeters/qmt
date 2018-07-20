from collections import OrderedDict
import json
from TaskMetaclass import TaskMetaclass


# todo base import then factories

class Task(object):
    __metaclass__ = TaskMetaclass
    current_instance_id = 0


    # TODO put *args here, that way the subclass can dump them here.
    #
    def __init__(self, state=None, dependencies=None, name="Task"):

        self.name = name
        if "#" not in name:
            self.name += "#" + str(Task.current_instance_id)
            Task.current_instance_id += 1

        self.state = state
        self.dependencies = dependencies

        if state is None:
            self.state = {}

        if dependencies is None:
            self.dependencies = []

        self.result = None

    def to_dict(self):
        result = OrderedDict()
        result_data = OrderedDict()
        result_data['class'] = self.__class__.__name__
        result_data['state'] = self.state
        result_data['dependencies'] = self.dependencies_list()
        result[self.name] = result_data
        return result

    @staticmethod
    def from_dict(dict_representation):
        taskName, data = dict_representation.items()[0]
        className = data['class']
        target_class = TaskMetaclass.class_registry[className]
        state = data['state']
        dependencies = [Task.from_dict(dependency) for dependency in data['dependencies']]
        return target_class.from_serialized_form(taskName, state, dependencies)

    def save(self, file_name):
        with open(file_name, 'w') as jsonFile:
            json.dump(self.to_dict(), jsonFile)

    def dependencies_list(self):
        return [task.to_dict() for task in self.dependencies]

    def run(self):
        # TODO should run all the dependencies
        raise NotImplementedError("This method is only implemented for subclasses of Task")

    def visualize(self):
        return self.run().visualize()

    def compute(self):
        if self.result is None:
            self.result = self.run().compute()

    @staticmethod
    def parseArgumentsToDict(arguments):
        state = {}
        dependencies = []
        arguments.pop('name', None)
        for argName, argValue in arguments.items():


        return state, dependencies