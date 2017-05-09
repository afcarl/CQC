import abc


class CCHandlerMixin(abc.ABC):

    def __init__(self, *args, **kw):
        self.ccobject = None

    @abc.abstractmethod
    def set_cc(self, name, data):
        raise NotImplementedError
