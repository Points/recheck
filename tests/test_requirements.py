import mock
import pytest
from recheck import requirements


@mock.patch('recheck.requirements._read_lines_from_file')
def test_no_direct_requirements(mock_read_lines_from_file):
    mock_read_lines_from_file.return_value = []
    requirements_parser = requirements.RequirementsParser('requirements.txt')
    assert requirements_parser.direct_requirements == set()


@mock.patch('recheck.requirements._read_lines_from_file')
def test_direct_requirements_single_file(mock_read_lines_from_file):
    mock_read_lines_from_file.return_value = ['requests==1.3']
    requirements_parser = requirements.RequirementsParser('requirements.txt')
    assert requirements_parser.direct_requirements == set(['requests'])

@mock.patch('recheck.requirements._read_lines_from_file')
def test_multiple_direct_requirements_single_file(mock_read_lines_from_file):
    mock_read_lines_from_file.return_value = ['requests==1.3', 'mock==0.1']
    requirements_parser = requirements.RequirementsParser('requirements.txt')
    assert requirements_parser.direct_requirements == set(['requests', 'mock'])
