from pathlib import Path
import configparser


class BadConfigError(Exception):
    pass


class DoclyConfig(object):

    def __init__(self, config_file):
        if Path(config_file).exists() and Path(config_file).is_file():
            self.config = configparser.ConfigParser()
            self.config.read(config_file)
            if "skipDirs" not in self.config:
                raise BadConfigError("\n\n=====>\nYou have mentioned a config file but it is badly formatted")
        else:
            self.config = None
    
    def _parent_contains_child(self, parent_path: str, child_path: str):
        child_path_rev = list(reversed(child_path.split("/")))
        parent_path_list = list(reversed(parent_path))
        parent_path_to_compare = parent_path_list[:len(child_path_rev)]
        return child_path_rev == parent_path_to_compare

    def is_dir_skipped(self, file_path_until_last_parent: str):
        if not self.config:
            return False
        for p in self.config["skipDirs"].keys():
            if self._parent_contains_child(file_path_until_last_parent, p):
                return True
        return False