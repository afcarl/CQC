import abc


class CCHandlerMixin(abc.ABC):

    def __init__(self):
        self.ccobject = None

    @abc.abstractmethod
    def set_cc(self, data):
        raise NotImplementedError
