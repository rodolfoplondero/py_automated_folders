import os
import sys
import json
import urllib.request
from pathvalidate import sanitize_filename
import configparser
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

class Actions:
    def __init__(self, path=''):
        path_config_file = self.__getIniPath('config.ini')
        config = configparser.ConfigParser()
        config.read(path_config_file)
        config_link = config['DEFAULT']['config_link']

        self.path = path
        self.config = self.__loadConfig(config_link)
        self.actions = self.__loadActions(self.config)

    def __loadConfig(self, link):
        with urllib.request.urlopen(link) as url:
            data = json.loads(url.read())
        # with open(link) as f:
        #     data = json.load(f)            
        return data

    def __loadActions(self, config):
        return [item['type'] for item in config]

    def __getIniPath(self, fileName):
        return fileName if os.path.isfile(fileName) else os.path.join(os.path.dirname(sys.executable, fileName))

    def __createFoldersFromList(self, folders, baseFolder=''):
        baseFolder = sanitize_filename(baseFolder)

        try:
            for folder in folders:
                folderName = os.path.join(self.path, baseFolder, folder)
                os.makedirs(folderName, True)
        except OSError as e:
            print("Pasta já existe")

    def __downloadFilesFromList(self, files, baseFolder=''):
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

def initApp(myActions):
    print("============================================")
    print(" ESCOLHA UMA OPÇÃO: ")
    print("============================================")
    optionNumber = 0
    for action in myActions.actions:
        optionNumber += 1
        print(f" {optionNumber} - {action}")
    optionSelected = int(input("> "))

    print("============================================")
    print(" NOME DA PASTA: ")
    print("============================================")
    folderName = input("> ")

    print("============================================")
    print(" CONFIRMA? ([s]/n) ")
    print(f"Ação: {myActions.actions[optionSelected-1]}")
    print(f"Pasta: {folderName}")
    print("============================================")
    confirm = (input("> "))
    
    if confirm in ["s", "S", ""]:
        myActions.doActions(myActions.actions[optionSelected-1], folderName)

    input(": Pressione ENTER para Terminar... ")

if __name__ == '__main__':
    path = '.' if sys.argv else sys.argv[1]
    actions = Actions(path)
    initApp(actions)