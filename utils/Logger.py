from os import mkdir, path


class Logger:
    path_to_file: str
    
    def __init__(self, folder: str):
        if not path.exists(folder):
            mkdir(folder)

        self.path_to_file = path.join(folder, 'log.txt')
    
    def log(self, message: str):
        with open(self.path_to_file, 'a') as file:
            file.write(message + '\n')
