from brain import Bot
import pandas as pd
import configparser

class InfoBot:
    
    def __init__(self, config_file):

        config = configparser.ConfigParser()
        config.read(config_file)
        
        # Intent Classification
        intent_section = config['intent classification']
        self.intents = intent_section.get('intents', fallback=None)
        self.intent_description = intent_section.get('description', fallback=None)
        
        # DataFrame
        dataframe_section = config['dataframe']
        path = dataframe_section.get('path', fallback=None)
        dataframe_description_file = dataframe_section.get('description', fallback=None)
        self.dataframe_description = self.read_file_into_string(dataframe_description_file)
        self.df = self.set_df(path) 
        self.bot = Bot(self.intents, self.intent_description, self.dataframe_description)

    def read_file_into_string(self, file_path):
        with open(file_path, 'r') as file:
            file_contents = file.read()
        return file_contents

    def set_df(self, path):
        
        df = pd.read_csv(path)
        return df

    def reply(self, message):
        try:
            reply = self.bot.logic(message, self.df)
            return reply

        except Exception as bErr:
            print(bErr)
            return "I need a maintainence"
