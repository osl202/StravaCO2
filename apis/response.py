from abc import ABC, abstractmethod
from inspect import signature
from typing import Any, Self, Union, overload

APIResponse = Union[dict[str, Any], list[Any]]

class Model(ABC):
    """
    A API response model, i.e. a class to hold all the fields returned in
    a response.
    To create a response model, inherit from this class and give the child
    class properties with names matching those of the response JSON. Fields
    will be passed to the `parse_field` method, which you must implement to
    correctly parse each field of the response.
    See strava_api/models.py for examples.
    """

    @classmethod
    @abstractmethod
    def parse_field(cls, key: str, value: Any) -> Any:
        """
        Decides how each field should be parsed from a provided JSON
        dictionary. This must be implemented for each `Model`.
        For example, to parse every field as a string, you would
        implement with `return str(value)`.
        """
        raise NotImplementedError()

    @overload
    @classmethod
    def fromResponse(cls, res: list[Any]) -> list[Self]:
        ...
    @overload
    @classmethod
    def fromResponse(cls, res: dict[str, Any]) -> Self:
        ...
    @classmethod
    def fromResponse(cls, res: APIResponse) -> Union[Self, list[Self]]:
        """
        Initialises a model (or list of models) with keys from a dict by matching key
        and parameter names. A derived class will need to initialise non-primitive types
        (e.g. fields that are a `Model` themselves) before passing the JSON.
        """
        if isinstance(res, dict):
            # Filter the JSON keys to those defined in the model
            keys = list(signature(cls.__init__).parameters.keys())[1:]
            # Set fields not in the JSON to None
            return cls(**{k: cls.parse_field(k, res[k]) if k in res else None for k in keys})
        else:
            return [cls.fromResponse(r) for r in res]
