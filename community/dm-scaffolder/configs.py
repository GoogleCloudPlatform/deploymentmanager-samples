from ruamel.yaml import YAML

class Config:
    
    yaml = YAML()

    def __init__(self, path):
        self.path = path
        f = open(path, "r")
        self.configs = self.yaml.load(f.read())
        f.close()

    def update_folders(self, folders):
        self.configs['folders_list_cache'] = folders
        print 'lets write'
        with open(self.path, 'w') as yf:
            self.yaml.dump(self.configs, stream=yf)
