from os import path
import tempfile

import pytest

from utils import Logger


@pytest.mark.asyncio
async def test_logger_class():
    temp_folder = tempfile.mkdtemp('logs')

    logger = Logger(folder=temp_folder)
    logger.log('test')

    with open(logger.path_to_file, 'r') as file:
        assert file.read() == 'test\n'


@pytest.mark.asyncio
async def test_logger_class_with_nonexistent_folder():
    temp_folder = tempfile.mkdtemp('test')

    logger = Logger(folder=temp_folder + '/logs')
    logger.log('test')

    with open(logger.path_to_file, 'r') as file:
        assert file.read() == 'test\n'

    assert path.exists(temp_folder + '/logs')
