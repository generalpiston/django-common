class BasicManager(object):
    """
    Provides the basic management features missing from Django:
        get_or_none - returns the instance or nothing.
    """
    def __init__(self, *args, **kwargs):
        super(BasicManager, self).__init__()


    def get_or_none(self, *args, **kwargs):
        try:
            return self.get(*args, **kwargs)
        except self.model.DoesNotExist:
            return None
