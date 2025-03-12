import os
from enum import Enum, EnumType


def validate_environment_variables_from_Enum(input: EnumType) -> dict[str, str]:
    """Runs validation on input enumeration class performing lookup for each enum.Value in the runtime environment context.

    Args:
        input (EnumType): enumeration class reference

    Raises:
        TypeError: invalid type for required input parameter
        ValueError: environment variable wasn't found in the runtime environment context.

    Returns:
        dict[str, str]: mappings between environment key and it's value
    """
    if not isinstance(input, EnumType):
        raise TypeError(
            "validate_environment_variables_from_Enum - input instance should be class Enum"
        )

    result: dict[str, str] = dict()

    enumeration: Enum
    for enumeration in input:
        env_value: str | None = os.environ.get(enumeration.value)
        if not env_value:
            raise ValueError(
                f"validate_environment_variables_from_Enum - missing environment variable '{enumeration.value}'"
            )

        result[enumeration.value] = env_value

    return result
