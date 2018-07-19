from dask import delayed
import json
from IncrementTask import IncrementTask
from Task import Task

def main():
    leftIncrementTask = IncrementTask(0)
    rightIncrementTask = IncrementTask(1)
    addTask = AddTask(leftIncrementTask, rightIncrementTask, 10)
    addTask.visualize()
    addTask.compute()
    print(addTask.result)
    print(addTask.compute())

class AddTask(Task):

    def __init__(self, leftIncrementTask, rightIncrementTask, number, name="AddTask"):
        state = {'number' : number}
        super(AddTask, self).__init__(state=state, dependencies=[leftIncrementTask, rightIncrementTask], name=name)
        self.leftIncrementTask = leftIncrementTask
        self.rightIncrementTask = rightIncrementTask
        self.number = number

    def run(self):
        if self.result is not None:
            return

        x = delayed(self.leftIncrementTask.run)()
        y = delayed(self.rightIncrementTask.run)()
        delayedAdd = delayed(sum([x, y, self.number]))
        return delayedAdd



if __name__=="main":
    main()