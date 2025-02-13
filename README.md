# DBChatBot

## Features

- Product information retrieval
- Supplier details with AI-powered summarization
- Specific product search functionality
- Real-time chat interface
- Integration with Hugging Face API
- MySQL database integration

## Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- MySQL database
- Hugging Face API key

## Backend Setup

1. Navigate to the frontend directory:

   ```bash
   cd backend
   ```
   
2. Create virtual environment:

   ```bash
   python3 -m venv venv
   ```

3. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your configurations:

   ```
   HUGGINGFACE_API_KEY=your_api_key
   ```

5. Set up your MySQL database and update `database.py` with your credentials.

6. Run the FastAPI server:

   ```bash
   uvicorn main:app --reload
   ```

   The backend will be available at `http://localhost:8000`

## Frontend Setup

1. Navigate to the frontend directory:

   ```bash
   cd frontend
   ```

2. Install dependencies:

   ```bash
   npm install
   ```

3. Start the React development server:

   ```bash
   npm start
   ```

   The frontend will be available at `http://localhost:3000`

## API Endpoints

- `POST /chat/` - Main chat endpoint
  - Request body:
    ```json
    { "text": "your message here" }
    ```
  - Response:
    ```json
    { "response": "bot response here" }
    ```

## Usage Examples

1. Get all products:
   ```bash
   curl -X GET "http://localhost:8000/products"
   ```



