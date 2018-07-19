import json
from Task import Task

class IncrementTask(Task):

    def __init__(self, number, name="IncrementTask"):
        state = {'number': number}
        super(IncrementTask, self).__init__(state=state, name=name)
        self._number = number

    @property
    def number(self):
        return self._number

    @number.setter
    def number(self, number):
        if number < 0:
            raise ValueError("number must be >= 0")
        self._number = number

    @staticmethod
    def from_serialized_form(name, state, dependencies):
        return IncrementTask(state['number'], name)

    def run(self):
        return self.number + 1