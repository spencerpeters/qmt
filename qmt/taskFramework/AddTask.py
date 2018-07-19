from dask import delayed
import json
from IncrementTask import IncrementTask
from Task import Task

def main():
    leftIncrementTask = IncrementTask(0)
    rightIncrementTask = IncrementTask(1)
    addTask = AddTask()

class AddTask(Task):

    def __init__(self, leftIncrementTask, rightIncrementTask, number, name="AddTask"):
        state = {'number' : number}
        super(AddTask, self).__init__(state=state, dependencies=[leftIncrementTask, rightIncrementTask], name=name)
        self.leftIncrementTask = leftIncrementTask
        self.rightIncrementTask = rightIncrementTask
        self.number = number

    def run(self):
        x = delayed(self.leftIncrementTask.run)()
        y = delayed(self.rightIncrementTask.run)()
        result = delayed(sum([x, y, self.number]))
        return result

    def compute(self):
        return self.run().compute()



if __name__=="main":
    main()