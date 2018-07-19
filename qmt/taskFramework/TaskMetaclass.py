class TaskMetaclass(type):

    class_registry = {}

    def __new__(mcs, name, bases, class_dict):
        cls = type.__new__(mcs, name, bases, class_dict)

        TaskMetaclass.register_class(cls)

        if not 'from_serialized_form' in class_dict:
            raise ValueError("Subclasses of Task must provide a from_serializable_form method")

        return cls

    @staticmethod
    def register_class(class_to_register):
        TaskMetaclass.class_registry[class_to_register.__name__] = class_to_register