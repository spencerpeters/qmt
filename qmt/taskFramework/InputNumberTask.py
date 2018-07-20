from qmt.taskFramework.Task import Task


class InputNumberTask(Task):

    def run_self(self):
        pass

    def __init__(self):
        super(InputNumberTask, self).__init__(**Task.remove_self_argument(locals()))

