class EmployeeAlreadyExistsError(Exception):
    """Raised when POST tries to create an employee whose ID already exists."""

    def __init__(self, employee_id: int, position: str):
        self.employee_id = employee_id
        self.position = position
        super().__init__(
            f"Employee already exists: id={employee_id}, position={position}"
        )
