from collections import OrderedDict
import json
from TaskMetaclass import TaskMetaclass


# todo base import then factories

class Task(object):
    __metaclass__ = TaskMetaclass
    current_instance_id = 0


    # TODO put *args here, that way the subclass can dump them here.
    #
    def __init__(self, **kwargs):

        print("kwargs " + str(kwargs))

        if "name" not in kwargs:
            raise AttributeError("All subclasses of Task must have a 'name' keyword argument")

        self.name = kwargs["name"]

        self.dependencies = kwargs
        self.dependencies.pop("name", None)

        # self.hasBeenWritten = False

        if "#" not in name:
            self.name += "#" + str(Task.current_instance_id)
            Task.current_instance_id += 1

        self.result = None

    def to_dict(self):
        result = OrderedDict()
        result_data = OrderedDict()
        result_data['class'] = self.__class__.__name__
        result_data['dependencies'] = self.dependencies_dict()
        result[self.name] = result_data
        return result

    @staticmethod
    def from_dict(dict_representation):
        taskName, data = dict_representation.items()[0]
        className = data['class']
        target_class = TaskMetaclass.class_registry[className]
        kwargs = {name: Task.from_dict(value) for name, value in data['dependencies'].items()}
        return target_class(name=taskName, **kwargs)

    def save(self, file_name):
        with open(file_name, 'w') as jsonFile:
            json.dump(self.to_dict(), jsonFile)

    def dependencies_dict(self):
        return {name: task.to_dict() for name, task in self.dependencies.items()}

    def run(self):
        for task in self.dependencies.keys():
            task.run()
        self.runSelf()

    def runSelf(self):
        raise NotImplementedError("Task is abstract. This method is defined only for subclasses of Task.")

    def visualize(self):
        return self.run().visualize()

    def compute(self):
        if self.result is None:
            self.result = self.run().compute()

    @staticmethod
    def remove_self_argument(init_arguments):
        init_arguments.pop('self', None)
        return init_arguments
