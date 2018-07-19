from Task import Task

class TaskMetaclass(type):

    def __new__(mcs, name, bases, class_dict):
        cls = type.__new__(mcs, name, bases, class_dict)

        Task.register_class(cls)

        if not 'from_serializable_form' in class_dict:
            raise ValueError("Subclasses of Task must provide a from_serializable_form method")

        return cls
