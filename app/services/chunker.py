
def chunk_text(text: str, chunk_size:int=500, chunk_overlap:int=50) -> list[str]:
  if chunk_size <= chunk_overlap:
    raise ValueError(f"chunk_overlap({chunk_overlap})必须小于chunk_size({chunk_size})")
  start = 0
  list_text = []
  while start < len(text):
    end = min(start + chunk_size,len(text))
    list_text.append(text[start:end])
    if end == len(text):
      break
    start = end - chunk_overlap
  return list_text