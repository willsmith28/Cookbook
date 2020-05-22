"""
Common functionality
"""


def user_owns_item(author_id: int, user_id: int, is_superuser: bool) -> bool:
    """checks if user owns thing they are trying to edit

    Args:
        author_id (int): author ID of item
        user_id (int): [description]
        is_superuser (bool): [description]

    Returns:
        bool: [description]
    """
    return user_id == author_id or is_superuser


def serialize_errors(errors: dict) -> dict:
    """Creates a copy of serializer errors dict with error messages cast to string

    Args:
        errors (dict): serializer errors dict

    Returns:
        dict: new dict with error messages cast to string
    """
    return {
        key: tuple(str(error) for error in errors) for key, errors in errors.items()
    }
