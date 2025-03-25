# LLM Knowledge Graph Generation

This repository provides tools and scripts to generate knowledge graphs using Large Language Models (LLMs). It includes backend services, a frontend interface, testing scripts, and additional resources to facilitate the creation and visualization of knowledge graphs.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Testing](#testing)

## Features

- **Backend Services**: Provides APIs for knowledge graph generation.
- **Frontend Interface**: User-friendly interface for interacting with the backend services.
- **Testing Scripts**: Includes various testing scripts to ensure the reliability and performance of the application.

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/MSimsek07/llm_knowledge_graph_generation.git

2. **Navigate to the Project Directory**:

   ```bash
   cd llm_knowledge_graph_generation
   
3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   
4. **Set Up Docker Environment (Optional)**:

   ```bash
   docker build -t llm_knowledge_graph .
   
## Usage
   
1. **Running the Backend Service**:

   ```bash
   python backend2.py
   
2. **Running the Frontend Interface**:
   ```bash
   python backend2.py
   
3. **Using Docker**:
   ```bash
   docker run -p 8000:8000 llm_knowledge_graph

## Testing

test_backend_app.py: Tests for the backend application.

test_streamlitapp_compability.py: Tests for Streamlit app compatibility.

test_streamlitapp_with_playwright.py: Tests using Playwright for end-to-end testing.

locustfile.py: Performance testing using Locust.

 To run the tests, execute:
   ```bash
    pytest test_backend_app.py





    
