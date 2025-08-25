# Project Summary and Detailed Instructions

## 1. Project Summary

### 1.1. Objectives

The primary objective of this project is to establish a robust and efficient local AI agent environment integrated with n8n for automated workflows. This involves deploying large language models (LLMs) locally using Ollama and exposing them via a FastAPI service, enabling seamless interaction with n8n's automation capabilities.

### 1.2. Scope

The project encompasses the following key areas:
- **Local AI Model Deployment:** Setting up Ollama to serve `tinyllama` and `phi3:mini` models within a Dockerized environment.
- **API Service Development:** Creating a Python FastAPI application (`foundation_sec_api_lite.py`) to provide a standardized interface for interacting with the deployed AI models.
- **n8n Integration:** Configuring n8n to communicate with the local AI API service, allowing for the creation of automated workflows that leverage AI capabilities.
- **Environment Management:** Ensuring all components are properly containerized using Docker and Docker Compose for easy deployment and management.
- **Documentation:** Providing clear instructions and configuration details for setting up and using the integrated system.

### 1.3. Key Deliverables

- **Docker Compose Setup:** A `docker-compose.yml` file that orchestrates the deployment of Ollama, the FastAPI AI service, and n8n.
- **AI API Service:** The `foundation_sec_api_lite.py` script providing endpoints for chat completion and text generation.
- **Ollama Modelfile:** `Modelfile.foundation-sec` for custom Ollama model setup.
- **n8n Workflow:** An example n8n workflow (`n8n-ollama-workflow.json`) demonstrating integration with the local AI agent.
- **API Configuration Guide:** The `ollama-api-config.md` document detailing API endpoints and n8n configuration.
- **Project Summary and Instructions Document:** This comprehensive guide for setup, configuration, and usage.```
## Detailed Instructions

This section provides step-by-step guidance for setting up and running the project.

### Prerequisites

Before you begin, ensure you have the following installed:

1.  **Docker and Docker Compose:** The project relies heavily on Docker for containerization. Follow the official Docker documentation to install Docker Engine and Docker Compose for your operating system.
    -   [Install Docker Engine](https://docs.docker.com/engine/install/)
    -   [Install Docker Compose](https://docs.docker.com/compose/install/)
2.  **Python 3.x:** Required for running the `foundation_sec_api_lite.py` service.
3.  **Git:** For cloning the repository (if applicable).

### Configuration

Follow these steps to set up and run the project:

1.  **Clone the Repository (if applicable):**
    ```bash
    git clone <repository_url>
    cd n8n_sec
    ```

2.  **Navigate to the Project Directory:**
    Ensure you are in the `/home/sa/projects/n8n_sec` directory where `docker-compose.yml` is located.
    ```bash
    cd /home/sa/projects/n8n_sec
    ```

3.  **Build and Run Docker Containers:**
    The `docker-compose.yml` file defines three services: `n8n`, `foundation-sec`, and `ollama`.
    -   `n8n`: The workflow automation platform.
    -   `foundation-sec`: A lightweight API for the Foundation-Sec model, communicating with Ollama.
    -   `ollama`: The Ollama server hosting the AI models.

    To build and start the services, run:
    ```bash
    docker-compose up -d --build
    ```
    -   `--build`: This flag ensures that the `foundation-sec` service (which uses a custom `foundation-sec-dockerfile`) is rebuilt if there are any changes.
    -   `-d`: Runs the containers in detached mode (in the background).

4.  **Verify Container Status:**
    Check if all containers are running correctly:
    ```bash
    docker ps
    ```
    You should see `n8n`, `foundation-sec-8b`, and `foundation-sec-ai` listed as running.

5.  **Access n8n:**
    Once the `n8n` container is running, you can access the n8n interface in your web browser at:
    `http://localhost:5678`

6.  **Ollama API Configuration for n8n Integration:**
    The `ollama-api-config.md` file provides details on how to configure n8n to interact with the Ollama API.
    -   **Base URL for n8n:** `http://foundation-sec-ai:11434` (This is the internal Docker network address for the Ollama service).
    -   **Available Models:** `tinyllama` and `phi3:mini`.
    -   **API Endpoints:** Refer to `ollama-api-config.md` for `GET /api/tags`, `POST /api/chat`, and `POST /api/generate` examples.

    When configuring an HTTP Request node in n8n for chat completion, use the following:
    -   **Method:** `POST`
    -   **URL:** `http://foundation-sec-ai:11434/api/chat`
    -   **Headers:** `Content-Type: application/json`
    -   **Body (JSON):**
        ```json
        {
          "model": "phi3:mini",
          "messages": [
            {
              "role": "user",
              "content": "{{ $json.message }}"
            }
          ],
          "stream": false
        }
        ```

7.  **Import n8n Workflow (Optional):**
    If you have an existing n8n workflow (e.g., `n8n-ollama-workflow.json`), you can import it into your n8n instance.

### Best Practices

-   **Resource Management:** The `ollama` service is configured with `mem_limit: 12g` and `memswap_limit: 12g`. Ensure your host system has sufficient memory, especially in nested Docker environments, to avoid performance issues or crashes.
-   **Health Checks:** The `docker-compose.yml` includes health checks for `foundation-sec` and `ollama` services. Monitor these to ensure the AI services are responsive.
-   **Troubleshooting:**
    -   If containers fail to start, use `docker-compose down` to stop and remove all services and networks, then try `docker-compose up -d --build` again.
    -   Check container logs for errors: `docker logs <container_name>` (e.g., `docker logs foundation-sec-ai`).
    -   Verify network connectivity between containers if API calls fail.
-   **Model Management:** If you need to use different models with Ollama, you can pull them using `docker exec foundation-sec-ai ollama pull <model_name>`.
-   **Security:** Be mindful of exposing ports to the host system. For production environments, consider more robust security measures.
```