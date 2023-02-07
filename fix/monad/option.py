
class Option:
    def __init__(self, value = None):
        self.__value = value

    def is_none(self):
        return self.__value == None

    def get_value(self):
        return self.__value

    @staticmethod
    def some(value):
        return Option(value)

    @staticmethod
    def none():
        return Option()


