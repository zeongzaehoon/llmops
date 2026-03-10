import tiktoken

from utils.constants import *



def get_token_length(text:str, model_name:str=None):
    try:
        model_name = model_name if model_name in TIKTOKEN_MODEL_LIST else TIKTOKEN_MODEL_LIST[0]
        encoding = tiktoken.encoding_for_model(model_name)
        return len(encoding.encode(text))
    except Exception as e:
        raise e


def chunking_text(text: str, model_name: str, max_tokens: int, overlap_tokens: int = 100):
    """    
    Args:
        text: 입력 텍스트
        model_name: 토크나이저 모델 이름
        max_tokens: 각 청크의 최대 토큰 수
        overlap_tokens: 청크 간 겹치는 토큰 수
    """
    encoding = tiktoken.encoding_for_model(model_name)
    tokens = encoding.encode(text)
    
    chunks = []
    start_idx = 0
    
    while start_idx < len(tokens):
        end_idx = min(start_idx + max_tokens, len(tokens))
        chunks.append(tokens[start_idx:end_idx])
        start_idx = end_idx - overlap_tokens if end_idx < len(tokens) else len(tokens)
    
    return [encoding.decode(chunk) for chunk in chunks]