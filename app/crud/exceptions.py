class DuplicateTitleException(Exception):
    """Raised when a ticket with the same name exist and reject_duplicates=True."""

    def __init__(self, resource: str, resource_title: str):
        self.resource = resource
        self.resource_title = resource_title
        self.message = f"A {resource} with the title: {resource_title}, already exists."
        super().__init__(self.message)
