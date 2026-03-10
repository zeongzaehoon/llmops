import tiktoken

from utils.constants import *

def get_token_length(text:str, model_name:str):
    model_name = model_name if model_name in TIKTOKEN_MODEL_LIST else "gpt-4o"
    encoding = tiktoken.encoding_for_model(model_name)
    return len(encoding.encode(text))