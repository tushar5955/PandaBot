
import openai
import json
import re
import pandas as pd
import ast
import configparser
config = configparser.ConfigParser()
config.read('config.ini')

# Intent Classification
section = config['openai']
key = section.get('key', fallback=None)

openai.api_key = key

class Bot:
    def __init__(self, intents, intent_description, dataframe_description):
        self.intents = intents
        self.intent_description = intent_description
        self.dataframe_description = dataframe_description
    

    def get_response(self, prompt, content="You are multiple brains"):
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "system", "content": content},
                {"role": "user", "content": prompt}
            ],
        )
        return response.choices[0].message.content
    
    def get_unique_categorical_values(self, df):
            categorical_columns = df.select_dtypes(include=['object', 'category']).columns
            unique_values_string = ""

            for col in categorical_columns:
                unique_values = df[col].unique()
                unique_values_string += f"{col}: {', '.join(map(str, unique_values))}\n"

            return unique_values_string
    
    

    def get_intent(self, prompt):
        intent_prompt = { "prompt": prompt, 'intents':self.intents, 'description':self.intent_description, 'expected output':"json with one key classification and value classification code {'classification':'1 or 2'}"}
        intent = self.get_response(str(intent_prompt))
        return intent

    def extract_integer_from_json(self, json_str):
        try:
            # Correct the JSON string by replacing single quotes with double quotes
            corrected_json_str = json_str.replace("'", "\"")
            
            # Parse the JSON string
            data = json.loads(corrected_json_str)
            
            # Extract the integer value from the JSON data
            number_as_integer = int(data.get('classification', 0))
            return number_as_integer
        except (json.JSONDecodeError, ValueError):
            # Handle any potential parsing errors and return None if extraction fails
            return None
    
    
    def get_code(self, message, info, task="assume dataframe is already loaded as df. use dataframe information and suggest only lines of python code that can be executed to get the new additional information require to respond to the prompt. assume values for neccessary variables"):
        code_prompt = { "prompt": message, 'dataframe information':info, 'task':task, 'expected output':"{'code':'lines of code for dataframe (df)'}"}
        code = self.get_response(str(code_prompt))
        #code = preprocess_code(str(code))
        return code
    

    def extract_code(self, json_string):
        try:
            # Convert the JSON string to a Python dictionary
            data = ast.literal_eval(json_string)

            if isinstance(data, dict) and 'code' in data:
                # Extract the value of the "code" key and split it into lines of code
                code_lines = data['code'].splitlines()
                return code_lines
            else:
                raise ValueError('Invalid JSON string format. Missing "code" key.')
        except (ValueError, SyntaxError) as e:
            print(f"Error: {e}")
            return [] 
    

    def execute_code(self, code_list, df):
        output_string = ""
        for code in code_list:
            try:
                # Use eval() to execute the code with the provided DataFrame
                # The result of the code execution will be stored in 'result' variable
                result = eval(code)
                
                # Convert the output to a string and append it to the output_string
                output_string += f"{code}:\n{str(result)}\n\n"
            except Exception as e:
                output_string += f"{code} - Error: {e}\n\n"
        
        return output_string
    
    def get_reply(self, prompt, facts, task='as an assistant use prompt, facts and dataframe information to generate an apt response'):
        reply_prompt = { "prompt": prompt, 'dataframe information':self.dataframe_description, 'facts':facts, 'task':task, 'expected output':"Json with one key response and value as reply text. eg {'response':'reply'}"}
        #reply_prompt = truncate_message(str(reply_prompt),4097)
        reply = self.get_response(str(reply_prompt))
        return reply
        
    
    def extract_response_from_json(self, json_str):
        try:
            # Correct the JSON string by replacing single quotes with double quotes
            corrected_json_str = json_str.replace("'", "\"")
            
            # Parse the JSON string
            data = json.loads(corrected_json_str)
            
            # Extract the 'response' value from the JSON data
            response = data.get('response', None)
            return response
        except (json.JSONDecodeError, ValueError):
            # Handle any potential parsing errors and return None if extraction fails
            return None

    def get_satisfaction(self,message, reply):
        satisfaction_prompt = { "prompt": message, "synthesis response":reply,  'expected output':"give a json with key satisfaction with value 1 indicating synthesis response is satisfactory response to prompt else 0"}
        satisfaction = self.get_response(str(satisfaction_prompt))
        satisfaction = self.extract_number_from_string(satisfaction)
        return satisfaction
    
    def extract_number_from_string(self, string):
        number = re.search(r'\d+', string)
        if number:
            return int(number.group())
        else:
            return None


    def logic(self, string, df):
        intent = self.get_intent(string)
        intent = self.extract_integer_from_json(str(intent))
        if intent == 1:
            col_info = self.get_unique_categorical_values(df) 
            info = self.dataframe_description + '\n' + col_info
            code = self.get_code(string, info)
            code = self.extract_code(str(code))
            
            info = self.execute_code(code, df)
            reply = self.get_reply(string, info)
            
            reply = self.extract_response_from_json(str(reply))
            
            return reply
        else:
            reply = self.get_response(string, "You are an advisor for indian agriculture market and a personalized assistant")
            return reply
