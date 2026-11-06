"""Smoke test: the contract package installs and reports its versions."""
import stdash_contract


def test_contract_version_is_1_0_0():
    assert stdash_contract.CONTRACT_VERSION == "1.0.0"


def test_package_has_a_version():
    assert stdash_contract.__version__