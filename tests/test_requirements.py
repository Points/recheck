import mock
import pytest
from recheck.requirements import OutdatedRequirement


@pytest.fixture
def ignored_requirement():
    requirement = mock.Mock()
    requirement.name = 'abc'
    return OutdatedRequirement(requirement,
                               [mock.Mock(), mock.Mock()],
                               [mock.Mock(), mock.Mock()],
                               {'abc'})


@pytest.fixture
def outdated_requirement_minor():
    requirement = mock.Mock()
    requirement.name = 'abc'
    installed_version = ('1.2.1', ('000001', '000002', '000001', '*final'))
    remote_version = ('1.4.0', ('000001', '000004', '000000', '*final'))
    return OutdatedRequirement(requirement, installed_version, remote_version, {'def'})


@pytest.fixture
def outdated_requirement_major():
    requirement = mock.Mock()
    requirement.name = 'abc'
    installed_version = ('1.2.1', ('000001', '000002', '000001', '*final'))
    remote_version = ('2.4.0', ('000002', '000004', '000000', '*final'))
    return OutdatedRequirement(requirement, installed_version, remote_version, {'def'})


def test_outdated_requirement_status(ignored_requirement, outdated_requirement_minor, outdated_requirement_major):
    assert ignored_requirement.status == 'ignored'
    assert outdated_requirement_minor.status == 'outdated:minor'
    assert outdated_requirement_major.status == 'outdated:major'
