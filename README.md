# Threat-Lense

## Table of Contents
- [Overview](#overview)
- [Technologies Used](#technologies-used)
- [Features](#features)
- [Running](#running)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Run the application](#run-the-application)
  - [Access the API](#access-the-api)
- [Endpoints](#endpoints)
  - [GET /health](#get-health)
  - [DELETE /purge](#delete-purge)
  - [GET /search](#get-search)
  - [GET /search/status/<task_id>](#get-searchstatustask_id)
  - [GET /sources](#get-sources)
  - [GET /sources/configured](#get-sourcesconfigured)
  - [POST /sources/<source_id>](#post-sourcessource_id)
  - [DELETE /sources/<source_id>](#delete-sourcessource_id)
  - [Error handling](#error-handling)

---

## Overview
Threat-lense combines mutiple Open-Source Threat Intel souces to one API platform for enriching Indicators of Compromises (IOCs). Platform is built with Docker. 

---

## Technologies Used

- **Python**: Core programming language.

- **Flask**: Web framework for building APIs.

- **Celery**: Task queue for managing background tasks.

- **Redis**: Cache and message broker for Celery.

- **Docker Compose**: For container orchestration and dependency management.

---

## Features
- Multiple Open-Source Threat Intel sources
- Modular design for adding more intel sources
- Supports enriching multiple different digital artifacts
    - IPv4 & IPv6
    - Domains
    - URLs
    - File-hashes (MD5, SHA1 & SHA256)

---

## Running

### Prerequisites
- Docker
- Docker Compose

### Installation
Clone the repository:

```
git clone https://github.com/sampob/threat-lense.git
cd threat-lense
```

Configure Docker environment variables by modifying `docker-compose.yml`.  
> Setting a secure secret key is required. 

Build the Docker containers:
```
docker compose build
```

### Run the application
Start the application with Docker Compose:
```
docker compose up
```

### Access the API
Once the containers are running, the API will be available at:
```
http://localhost:5000
```

---

## Endpoints

### GET /health
- **Description**: Checks the health of the API.
- **Response**:
  - **200 OK**:
    ```json
    {
        "status": "successful",
        "message": "API is running"
    }
    ```

---

### DELETE /purge
- **Description**: Flushes the cache.
- **Response**:
  - **200 OK**:
    ```json
    {
        "status": "successful",
        "message": "cache flushed successfully"
    }
    ```

---

### GET /search
- **Description**: Starts a background search task.
- **Headers**:
  - `Content-Type: application/json`
- **Request Body**:
  ```json
  {
      "indicator": "example_indicator"
  }
- **Response**:
    - **202 Accepted**:
    ```json
    {
        "status": "started",
        "task_id": "task-id",
        "status_url": "/search/status/<task-id>"
    }
    ```
    - **400 Bad Request**:
    ```json
    {
        "error": "Bad Request",
        "message": "Invalid parameter",
        "status_code": 400
    }
    ```

---

### GET /search/status/<task_id>
- **Description**: Retrieves the status or result of a search task.
- **Path Parameters**:
    - `task_id`: The ID of the task.
- **Response**:
    - **200 OK** (Pending task):
    ```json
    {
        "state": "PENDING",
        "status": "Pending..."
    }
    ```
    - **200 OK** (Task completed successfully):
    ```json
    {
        "state": "SUCCESS",
        "status": "Task completed successfully!",
        "result": {
            "source_name": {
                "summary": "summary",
                "verdict": "VERDICT",
                "url": "url",
                "data": {}
            }
        }
    }
    ```

---

### GET /sources
- **Description**: Lists all data sources.
- **Response**:
    **200 OK**:
    ```json
    {
        "status": "successful",
        "sources": [
            {
                "id": 1,
                "name": "source_name",
                "requires_api_key": true,
                "api_key_configured": false
            }
        ]
    }
    ```

---

### GET /sources/configured
- **Description**: Retrieves names of all configured data sources.
- **Response**:
    - **200 OK**:
    ```json
    {
        "status": "successful",
        "configured_sources": ["source1", "source2"]
    }
    ```

---

### POST /sources/<source_id>
- **Description**: Sets an API key for a specific source.
- **Path Parameters**:
    - `source_id`: The ID or name of the source.
- **Request Body**:
    ```json
    {
        "api_key": "your-api-key"
    }
    ```
- **Response**:
    - **200 OK**:
    ```json
    {
        "status": "successful",
        "message": "API key for source_name set successfully"
    }
    ```
    - **404 Not Found**:
    ```json
    {
        "error": "Not Found",
        "message": "Source not found",
        "status_code": 404
    }
    ```

---

### DELETE /sources/<source_id>
- **Description**: Deletes the API key for a specific source.
- **Path Parameters**:
    - `source_id`: The ID or name of the source.
- **Response**:
    - **200 OK**:
    ```json
    {
        "status": "successful",
        "message": "API key for source_name deleted successfully"
    }
    ```
    - **404 Not Found**:
    ```json
    {
        "error": "Not Found",
        "message": "No API key found for source_name",
        "status_code": 404
    }
    ```

### Error Handling
- **400 Bad Request**: Returned when the request is malformed or invalid.
```json
{
    "error": "Bad Request",
    "message": "Detailed error message",
    "status_code": 400,
    "path": "/path/endpoint",
    "timestamp": "timestamp_here"
}
```

- **404 Not Found**: Returned when the requested resource or endpoint is not found.
```json
{
    "error": "Not Found",
    "message": "Detailed error message",
    "status_code": 404,
    "path": "/path/endpoint",
    "timestamp": "timestamp_here"
}
```

## License

This project is licensed under the MIT License.