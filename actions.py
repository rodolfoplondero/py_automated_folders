import os
import sys
import json
import urllib.request
from pathvalidate import sanitize_filename
import configparser


class Actions:
    def __init__(self, path=''):
        path_config_file = self.__getInitPath('config.ini')
        config = configparser.ConfigParser()
        config.read(path_config_file)
        config_link = config['DEFAULT']['config_link']

        self.path = path
        self.config = self.__loadConfig(config_link)
        self.actions = self.__loadActions(self.config)

    def __loadConfig(self, link):
        with urllib.request.urlopen(link) as url:
            data = json.loads(url.read().decode())
        return data

    def __loadActions(self, config):
        return [item['type'] for item in config]

    def __getInitPath(self, fileName):
        return fileName if os.path.isfile(fileName) else os.path.join(os.path.dirname(sys.executable, fileName))

    def __createFoldersFromList(folders, baseFolder=''):
        baseFolder = sanitize_filename(baseFolder)

        for folder in folders:
            folderName = os.path.join(self.path, baseFolder, folder)
            os.makedirs(folderName, True)

    def __downloadFilesFromList(files, baseFolder=''):
        baseFolder = sanitize_filename(baseFolder)

        for file in files:
            link = file["from"]
            destination = file["to"]
            fileName = link.rsplit("/", 1)[-1]
            fullPathFile = os.path.join(self.path, baseFolder, destination, fileName)

            if not os.path.exists(fullPathFile):
                print("Downloading {} to {}".format(link, fullPathFile))
                urllib.request.urlretrieve(link, fullPathFile)

    def doActions(self, actionType, folderName):
        [actions] = [item['actions'] for item in self.config if (item['type'] == actionType)]

        self.__createFoldersFromList(actions['folders'], folderName)
        self.__downloadFilesFromList(actions['files'], folderName)

if __name__ == '__main__':
    path = '.'
    actions = Actions(path)
    actions.doActions("New", "teste")