from Task import Task


class IncrementTask(Task):

    def __init__(self, number, name="IncrementTask"):
        super(IncrementTask, self).__init__(**Task.remove_self_argument(locals()))
        self.number = number  # optional

    def run_self(self):
        return self.number + 1
