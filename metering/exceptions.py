class ApiError(Exception):
    """
    For wrapping API errors.
    """

    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text

    def __str__(self):
        return "{0}: {1}".format(self.status_code, self.text)
