import json
from Task import Task
from Task import Task

class IncrementTask(Task):

    def __init__(self, number, name="IncrementTask"):
        super(IncrementTask, self).__init__(Task.remove_self_argument(locals()))
        self.number = number  #optional

    # @property
    # def number(self):
    #     return self._number
    #
    # @number.setter
    # def number(self, number):
    #     if number < 0:
    #         raise ValueError("number must be >= 0")
    #     self._number = number

    @staticmethod
    def from_serialized_form(name, state, dependencies):
        return IncrementTask(state['number'], name)

    def run(self):
        return self.number + 1