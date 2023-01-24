# pylint: disable=unused-variable
from starknet_py.utils.decorators.code_examples.code_examples_test import Cat


def test_init():
    # docs: init_start
    cat = Cat()
    # or
    cat = Cat(name="Bonifacy")
    # docs: init_end


def test_get_legs():
    cat = Cat()
    # docs: get_legs_start
    legs = cat.get_legs()
    # docs: get_legs_end


def test_get_species():
    cat = Cat()
    # docs: get_species_start
    species = cat.get_species()
    # docs: get_species_end
