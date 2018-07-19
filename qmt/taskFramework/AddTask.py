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


class AddTask(Task):

    def __init__(self, left_increment_task, right_increment_task, number, name="AddTask"):
        state = {'number': number}
        super(AddTask, self).__init__(state=state, dependencies=[left_increment_task, right_increment_task], name=name)
        self.left_increment_task = left_increment_task
        self.right_increment_task = right_increment_task
        self.number = number

    @staticmethod
    def from_serialized_form(name, state, dependencies):
        return AddTask(dependencies[0], dependencies[1], state['number'], name)

    def run(self):
        x = delayed(self.left_increment_task.run)()
        y = delayed(self.right_increment_task.run)()
        delayed_add = delayed(sum)([x, y, self.number])
        return delayed_add


if __name__ == "main":
    main()


# versions:
