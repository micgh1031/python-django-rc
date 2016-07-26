from wsi.utils.exceptions import ErrorConvention
from wsi.utils.views import GeneralResponseMixin


class ViewExceptionMiddleware(GeneralResponseMixin):
    def process_exception(self, request, exception):
        if isinstance(exception, ErrorConvention):
            return self.error(exception.msg)