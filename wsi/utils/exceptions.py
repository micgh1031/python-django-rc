class ErrorConvention(Exception):
    def __init__(self, err_message, **kwargs):
        self.msg = err_message
        super(ErrorConvention, self).__init__(err_message, **kwargs)