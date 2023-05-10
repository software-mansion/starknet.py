from starknet_py.serialization.data_serializers.unit_serializer import UnitSerializer

serializer = UnitSerializer()


def test_deserialize_unit():
    deserialized = serializer.deserialize([])

    assert deserialized is None


def test_serialize_unit():
    # pylint: disable=use-implicit-booleaness-not-comparison
    serialized = serializer.serialize(None)

    assert serialized == []
