# Web Scraping and Summarization API

This project provides a web scraping and summarization API using FastAPI. The API allows users to input URLs, scrape their contents, summarize the text, and store the results in a PostgreSQL database. It also includes endpoints for bulk URL processing and paginated reporting of the crawled URLs.

## Features

- **Single URL Scraping**: Scrape and summarize the contents of a single URL.
- **Bulk URL Scraping**: Submit multiple URLs for background processing and summarization.
- **Task Status Checking**: Check the status of bulk scraping tasks.
- **Paginated Reporting**: Retrieve a paginated list of all distinct URLs that have been crawled.
- **Logging**: Implements logging to keep track of the scraping of the URLs.

## Assumptions

- The project uses the `sshleifer/distilbart-cnn-12-6` model for text summarization.
- URLs and their summaries are stored in a PostgreSQL database.

## Setup and Installation

### Prerequisites

- Python 3.8 or higher
- PostgreSQL

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/web-scraping-api.git
   cd web-scraping-api
   ```

2. Create a virtual environment and activate it:
   ```bash
   python3 -m venv my_env
   source my_env/bin/activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

### Database Setup

1. Create a `.env` file in the root directory of the project and add your database connection URL:
   ```
   DB_URL=postgresql://username:password@localhost/dbname
   ```
   When the project is run for the first time assuming that the DB_URL is correct, the database and tables will be created accordingly. 

   It will take a considerable amount of time for the project to load the summarizer model and embeddings model the first time it is run, so be patient.

 

### Running the Project

1. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

2. The API will be available at `http://localhost:8000`.

## API Endpoints

### Scrape a Single URL

- **Endpoint**: `POST /scrape/`
- **Description**: Scrapes and summarizes the content of a single URL.
- **Request Body**:
  ```json
  {
      "url": "https://www.bbc.com/travel/article/20240730-how-climate-change-can-affect-your-summer-vacation"
  }
  ```

### Bulk Scrape URLs

- **Endpoint**: `POST /bulk-scrape/`
- **Description**: Submits multiple URLs for background processing and summarization.
- **Request Body**:
  ```json
  {
      "urls": [
          "https://www.bbc.com/culture/article/20240801-industry-why-the-most-cynical-show-on-tv-is-so-much-fun",
          "https://www.bbc.com/travel/article/20240730-how-climate-change-can-affect-your-summer-vacation"
      ]
  }
  ```

- **Response**:
  ```json
  {
      "task_id": "task_id"
  }
  ```

### Check Task Status

- **Endpoint**: `GET /bulk-scrape/status/{task_id}`
- **Description**: Checks the status of a bulk scraping task.
- **Response** (In Progress):
  ```json
  {
      "status": "in progress"
  }
  ```

- **Response** (Complete):
  ```json
  {
      "status": "complete",
      "results": [...]
  }
  ```

### Paginated Report

- **Endpoint**: `GET /report/`
- **Description**: Retrieves a paginated list of all distinct URLs that have been crawled.
- **Query Parameters**:
  - `page`: The page number (default: 1).
  - `page_size`: The number of items per page (default: 10).
- **Response**:
  ```json
  {
      "urls": [
          "https://www.bbc.com/culture/article/20240801-industry-why-the-most-cynical-show-on-tv-is-so-much-fun",
          "https://www.bbc.com/travel/article/20240730-how-climate-change-can-affect-your-summer-vacation"
      ],
      "pagination": {
          "current_page": 1,
          "page_size": 10,
          "total_pages": 1,
          "total_urls": 2
      }
  }
  ```

---