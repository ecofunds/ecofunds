
class ForceResponse(Exception):
    def __init__(self, response):
        self.response = response
        
class ForceResponseMiddleware:
    def process_exception(self, request, e):
        """Because django plugins cannot throw raw response
        (redirect is required to user dashboard after form is submitted),
        a solution is to raise an exception, catch it with middleware and
        react.

        This middleware checks for ForceResponse exception and returns it's
        response object.

        In reality, ForceResponse is caught as TemplateSyntaxtError in cms
        plugin. So we have to extract ForceResponse from it.

        Instance of TemplateSyntaxError has exc_info field where it has the
        original exception. exc_info[1] is the exception instance.
        """
        from django.template import TemplateSyntaxError
        if isinstance(e, TemplateSyntaxError) and getattr(e, 'exc_info', 0):
            try:
                e = e.exc_info[1]
            except: # Not iterable or IndexError
                raise e # as if nothing had happened
        if isinstance(e, ForceResponse):
            return e.response