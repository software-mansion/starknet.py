from abc import ABC, abstractmethod

from starknet_py.utils.decorators import add_code_examples


class Animal(ABC):
    """
    Base class representing an animal.
    """

    @abstractmethod
    def get_species(self) -> str:
        """
        Returns animal species.
        """

    @abstractmethod
    def get_legs(self) -> int:
        """
        Returns number of animal's legs.
        """


@add_code_examples
class Cat(Animal):
    """
    Class representing a cat.
    """

    def __init__(self, name: str = "Filemon"):
        """
        :param name: Cat's name.
        """
        self.name = name

    def get_legs(self) -> int:
        return 4

    def get_species(self) -> str:
        return "Mammal"


def test_codesnippet_added():
    assert len(Cat.get_legs.__doc__) > len(Animal.get_legs.__doc__)  # pyright: ignore
    assert len(Cat.get_species.__doc__) > len(
        Animal.get_species.__doc__  # pyright: ignore
    )

    assert Cat.__init__.__doc__.find("codesnippet")
    assert Cat.get_legs.__doc__.find("codesnippet")
    assert Cat.get_species.__doc__.find("codesnippet")
