class RegisterClassConstructorMetaclass(type):

    def __new__(mcs, name, bases, class_dict):
        cls = type.__new__(mcs, name, bases, class_dict)
        print("Metaclass!")
        return cls
