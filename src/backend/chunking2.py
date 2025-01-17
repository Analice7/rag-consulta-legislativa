import json
import requests
from langchain_text_splitters import RecursiveJsonSplitter

with open('data_teste/L15041/L15041_processed.json', 'r', encoding='utf-8', errors='ignore') as file:
    json_data = json.load(file);

splitter = RecursiveJsonSplitter(max_chunk_size=100)
json_chunks = splitter.split_json(json_data=json_data)
texts = splitter.split_text(json_data=json_data, convert_lists=True)

print([len(text) for text in texts][:10])