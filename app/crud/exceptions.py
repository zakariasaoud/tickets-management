class DuplicateTitleException(Exception):
    """Raised when a ticket with the same name exist and reject_duplicates=True."""

    def __init__(self, resource: str, resource_title: str):
        self.resource = resource
        self.resource_title = resource_title
        self.message = f"A {resource} with the title: {resource_title}, already exists."
        super().__init__(self.message)


class NotFoundError(Exception):
    """Raised when a ticket is not found in the database."""

    def __init__(self, resource: str, resource_id: int):
        self.resource = resource
        self.resource_id = resource_id
        self.message = f"{resource} with ID {resource_id} is not found."
        super().__init__(self.message)


class InvalidUUIDError(ValueError):
    """Raised when the provided UUID string used to get a ticket, is invalid."""

    pass
