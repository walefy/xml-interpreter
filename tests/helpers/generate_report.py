from os import popen
from typing import Literal


class TestItem:
    passed: bool
    name: str

    def __init__(self, name: str, passed: Literal['passed', 'failed']):
        self.name = name
        self.passed = passed == 'passed'

    def __str__(self) -> str:
        return f'TestItem (name = {self.name}, passed = {self.passed})'


def find_index(lines: list[str], keyword: str) -> int:
    for index, line in enumerate(lines):
        if keyword in line:
            return index

    return -1


def filter_lines(lines: list[str], includes: list[str], callback=None):
    filtered_lines = []
    for line in lines:
        if any(keyword in line for keyword in includes):
            if callback is not None:
                line = callback(line)

            filtered_lines.append(line)

    return filtered_lines


def callback_transform(line: str) -> str:
    splitted_line = line.split(' ')
    test_name = splitted_line[0].split('::')[1]
    test_passed = splitted_line[1].lower()
    test = TestItem(test_name, test_passed)
    return f'{test.name} | {"✅" if test.passed else "❌"}'


def generate_report():
    pytest_output = popen('pytest -W ignore::DeprecationWarning -v').read()
    index = find_index(pytest_output.splitlines(), '[100%]')
    pytest_output = pytest_output.splitlines()[:index + 1]

    lines = filter_lines(
        pytest_output,
        ['PASSED', 'FAILED'],
        callback_transform
    )

    with open('report.md', 'w') as file:
        file.write('*name* | *passed*\n')
        file.write('--- | :---:\n')
        file.write('\n'.join(lines))
        file.write('\n')


generate_report()
