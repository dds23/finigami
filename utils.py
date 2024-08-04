from bs4 import BeautifulSoup
import requests
from fastapi import HTTPException
import logging
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(level=logging.INFO)


def process_chunk(chunk, index, summarizer):
    try:
        chunk_len = len(chunk.split())
        logging.info(f"Processing chunk {index} of size: {chunk_len} words")

        tokenized_chunk = summarizer.tokenizer.encode(
            chunk, return_tensors='pt')
        if tokenized_chunk.size(1) > summarizer.model.config.max_position_embeddings:
            raise HTTPException(
                status_code=400, detail=f"Chunk {index} size exceeds model's max position embeddings limit.")
        summary = summarizer(chunk, min_length=int(
            chunk_len * 0.3), max_length=int(chunk_len * 0.5), do_sample=False)
        return summary[0]['summary_text']

    except IndexError as e:
        error_str = f"Tokenization error in chunk {index}: {str(e)}"
        logging.error(error_str)
        raise HTTPException(status_code=500, detail=error_str)

    except Exception as e:
        error_str = f"Summarization error in chunk {index}: {str(e)}"
        logging.error(error_str)
        raise HTTPException(status_code=500, detail=error_str)


def scrape_url(url, summarizer):
    response = requests.get(url)
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Invalid URL")

    soup = BeautifulSoup(response.content, 'html.parser')

    title = soup.find('h1').get_text() if soup.find(
        'h1') else "No H1 Title Found"

    paragraphs = soup.find_all('p')
    if not paragraphs:
        raise HTTPException(
            status_code=400, detail="No paragraph content found to summarize.")

    text = " ".join([para.get_text() for para in paragraphs])

    if len(text.split()) < 50:
        raise HTTPException(
            status_code=400, detail="Content is too short to summarize.")

    logging.info(f"Text length: {len(text.split())} words")

    max_chunk_size = 1024
    text_chunks = [text[i:i + max_chunk_size]
                   for i in range(0, len(text), max_chunk_size)]
    summaries = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_chunk = {executor.submit(
            process_chunk, text_chunks[i], i + 1, summarizer): text_chunks[i] for i in range(len(text_chunks))}
        chunk_tracker = {}
        i = 0
        for key in future_to_chunk.keys():
            key_val = str(key.__dict__['_condition'])
            start = key_val.find('at ') + 3
            end = key_val.find('>', start + 1)
            code = key_val[start: end]
            # print(key_val, code)
            chunk_tracker[code] = i
            i += 1

        for future in as_completed(future_to_chunk):
            key_val = str(future.__dict__['_condition'])
            start = key_val.find('at ') + 3
            end = key_val.find('>', start + 1)
            code = key_val[start: end]
            try:
                summaries.append(future.result())
                logging.info(
                    f"Completed processing of chunk {chunk_tracker[code] + 1}")
            except HTTPException as e:
                raise e
            except Exception as e:
                logging.error(
                    f"Error processing chunk {chunk_tracker[code] + 1}: {str(e)}")
                raise HTTPException(
                    status_code=500, detail=f"Error processing chunk {chunk_tracker[code] + 1}: {str(e)}")

    final_summary = " ".join(summaries)

    links = [urljoin(url, a['href']) for a in soup.find_all('a', href=True)]

    return {
        "title": title,
        "summary": final_summary,
        "links": links
    }
