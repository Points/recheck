import contextlib

import mock
import pytest
from recheck import requirements


@contextlib.contextmanager
def requirements_parsed(lines, requirements_file_name='requirements.txt'):
    with mock.patch('recheck.requirements._read_lines_from_file') as mock_read_lines_from_file:
        mock_read_lines_from_file.return_value = lines
        requirements_parser = requirements.RequirementsParser(requirements_file_name)
        yield requirements_parser
        assert [mock.call(requirements_file_name)] == mock_read_lines_from_file.call_args_list


def assert_direct_requirements(requirements_file_lines, expected_direct_requirements,
                               expected_index_url=None, expected_extra_index_urls=None):
    with requirements_parsed(requirements_file_lines) as requirements_parser:
        assert requirements_parser.direct_requirements == expected_direct_requirements
        assert requirements_parser.index_url == expected_index_url
        assert requirements_parser.extra_index_urls == (expected_extra_index_urls or [])


def test_no_direct_requirements():
    assert_direct_requirements([], set())


def test_direct_requirements_single_file():
    assert_direct_requirements(['requests==1.3'], set(['requests']))


def test_multiple_direct_requirements_single_file():
    assert_direct_requirements(['requests==1.3', 'mock==0.1'], set(['requests', 'mock']))


def test_direct_requirements_no_version_single_file():
    assert_direct_requirements(['requests'], set(['requests']))


def test_direct_requirements_range_requirement():
    assert_direct_requirements(['requests>1.6'], set(['requests']))
    assert_direct_requirements(['requests<1.6'], set(['requests']))
    assert_direct_requirements(['requests<=1.6'], set(['requests']))
    assert_direct_requirements(['requests>=1.6'], set(['requests']))


def test_direct_requirements_with_spaces_around_requirement():
    assert_direct_requirements(['requests >1.6'], set(['requests']))
    assert_direct_requirements(['requests ==1.6'], set(['requests']))
    assert_direct_requirements([' requests ==1.6'], set(['requests']))


def test_direct_requirements_with_comment_line():
    assert_direct_requirements(['requests>1.6', '#this is a comment'], set(['requests']))


def test_with_index_url():
    assert_direct_requirements(['requests>1.6',
                                '--index-url=http://index.example.com'],
                               set(['requests']),
                               'http://index.example.com')
    assert_direct_requirements(['requests>1.6', '--index-url http://index.example.com'],
                               set(['requests']),
                               'http://index.example.com')


def test_with_extra_index_urls():
    assert_direct_requirements(['requests>1.6',
                                '--extra-index-url=http://index.example.com'],
                               set(['requests']),
                               None,
                               ['http://index.example.com'])
    assert_direct_requirements(['--extra-index-url=http://index0.example.com',
                                'requests>1.6',
                                '--extra-index-url=http://index1.example.com'],
                               set(['requests']),
                               None,
                               ['http://index0.example.com',
                                'http://index1.example.com'])
