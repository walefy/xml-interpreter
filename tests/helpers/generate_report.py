from typing import Literal


class TestItem:
    passed: bool
    name: str

    def __init__(self, name: str, passed: Literal['passed', 'failed']):
        self.name = name
        self.passed = passed.lower() == 'passed'

    def __str__(self) -> str:
        return f' TestItem (name = {self.name}, passed = {self.passed})'


def generate_report():
    tests: list[TestItem] = []

    with open('report.txt', 'r') as file:
        for line in file.readlines():
            if line.startswith('test'):
                test = line.split(' ')
                test_name = test[0].split('::')[1]
                test = TestItem(test_name, test[1])
                tests.append(test)

            if line.strip().endswith('[100%]'):
                break

    with open('report.md', 'w') as file:
        file.write('| *name* | *passed* |\n')
        file.write('| --- | --- |\n')
        for test in tests:
            file.write(f'| {test.name} | {"✅" if test.passed else "❌"} |\n')


generate_report()
