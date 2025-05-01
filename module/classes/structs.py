class Instructor(object):
    """
    A class to represent an instructor.

    Attributes:
            first_name (str): The first name of the instructor.
            last_name (str): The last name of the instructor.
            link (str): The link to the instructor's profile.

    Examples:
        ```
        # Instructor: John Doe
        instructor = Instructor("John", "Doe", "https://www.marshall.usc.edu/instructor/johndoe")

        # John Doe
        print(instructor)
        ```
    """

    def __init__(self, first_name: str, last_name: str, link: str) -> None:
        """
        Initialize an Instructor object.

        Args:
            first_name (str): The first name of the instructor.
            last_name (str): The last name of the instructor.
            link (str): The link to the instructor's profile.
        """
        self.first_name = first_name
        self.last_name = last_name
        self.link = link

    def __str__(self) -> str:
        """
        Return a string representation of the Instructor object.

        Examples:
            ```
            # Instructor: John Doe
            instructor = Instructor("John", "Doe", "https://www.marshall.usc.edu/instructor/johndoe")

            # John Doe
            print(instructor)
            ```

        Returns:
            output (str): A string representation of the Instructor object.
        """
        return f"{self.first_name} {self.last_name}"

    def full_info(self) -> str:
        """
        Get the full information of the instructor.

        Returns:
            output (str): A string containing the full information of the instructor.
        """
        return f"{self.first_name} {self.last_name} {self.link}"
