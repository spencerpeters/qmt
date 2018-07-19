import json
from Task import Task

class IncrementTask(Task):

    def __init__(self, number, name="IncrementTask"):
        state = {'number': number}
        super(IncrementTask, self).__init__(state=state, name=name)
        self.number = number

    def run(self):
        return self.number + 1