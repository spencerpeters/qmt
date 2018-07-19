from collections import OrderedDict
import json
from TaskMetaclass import TaskMetaclass


# todo base import then factories

class Task(object):
    __metaclass__ = TaskMetaclass
    current_instance_id = 0
    class_registry = {}

    def __init__(self, state=None, dependencies=None, name="Task"):
        self.name = name + "#" + str(Task.current_instance_id)
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
        target_class = Task.class_registry[className]
        state = data['state']
        dependencies = [Task.from_dict(dependency) for dependency in data['dependencies']]
        return target_class.from_serialized_form(taskName, state, dependencies)

    def save(self, file_name):
        with open(file_name, 'w') as jsonFile:
            json.dump(self.to_dict(), jsonFile)

    def dependencies_list(self):
        return [task.to_dict() for task in self.dependencies]

    def run(self):
        raise NotImplementedError("This method is only implemented for subclasses of Task")

    @staticmethod
    def from_serialized_form(name, state, dependencies):
        raise NotImplementedError("This method is only implemented for subclasses of Task")

    def visualize(self):
        return self.run().visualize()

    def compute(self):
        if self.result is None:
            self.result = self.run().compute()

    @staticmethod
    def register_class(classToRegister):
        Task.class_registry[classToRegister.__name__] = classToRegister