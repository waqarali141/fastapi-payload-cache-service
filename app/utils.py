import hashlib
import json


# Generate Unique Identifier for Input Strings
def generate_hash(list_1, list_2):
    data_string = json.dumps({"list_1": list_1, "list_2": list_2}, sort_keys=True)
    return hashlib.sha256(data_string.encode()).hexdigest()


# Transformer function
def transformer_function(text: str) -> str:
    return text.upper()
