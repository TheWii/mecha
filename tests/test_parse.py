import pytest
from beet import Function
from beet.core.utils import JsonDict
from pytest_insta import SnapshotFixture
from tokenstream import InvalidSyntax

from mecha import Mecha, delegate, get_argument_examples, get_command_examples


def test_basic1(snapshot: SnapshotFixture, mc: Mecha):
    assert snapshot() == mc.parse_command("gamerule fallDamage false").dump()


def test_basic2(snapshot: SnapshotFixture, mc: Mecha):
    function = Function(
        [
            "gamerule doMobLoot false",
            "gamerule doDaylightCycle false",
        ]
    )
    assert snapshot() == mc.parse_function(function).dump()


def test_command_examples(snapshot: SnapshotFixture, mc: Mecha):
    assert snapshot() == mc.parse_function(get_command_examples()).dump()


@pytest.mark.parametrize(
    "test_name, properties, is_error, value",
    params := [
        (
            f"{argument_parser} {i} {j}",
            suite.get("properties", {}),
            suite.get("is_error", False),
            value,
        )
        for argument_parser, suites in get_argument_examples().items()
        for i, suite in enumerate(suites)
        for j, value in enumerate(suite["examples"])
    ],
    ids=[args[0] for args in params],
)
def test_argument_examples(
    snapshot: SnapshotFixture,
    mc: Mecha,
    test_name: str,
    properties: JsonDict,
    is_error: bool,
    value: str,
):
    argument_parser = f"command:argument:{test_name.partition(' ')[0]}"
    if argument_parser not in mc.spec.parsers:
        pytest.skip()

    stream = mc.create_token_stream(value)

    with stream.syntax(literal=r"\S+"), stream.provide(properties=properties):
        if is_error:
            with pytest.raises(InvalidSyntax) as exc_info:
                delegate(argument_parser, stream)
            assert snapshot() == "\n---\n".join(
                [
                    test_name,
                    str(properties),
                    value,
                    str(exc_info.value),
                ]
            )
        else:
            assert snapshot() == "\n---\n".join(
                [
                    test_name,
                    str(properties),
                    value,
                    delegate(argument_parser, stream).dump(),
                ]
            )
