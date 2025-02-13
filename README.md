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

1. Install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your configurations:

   ```
   DATABASE_URL=your_database_url
   HUGGINGFACE_API_KEY=your_api_key
   Model Link - https://huggingface.co/facebook/bart-large-cnn
   ```

3. Set up your MySQL database and update `database.py` with your credentials.

4. Run the FastAPI server:

   ```bash
   uvicorn main:app --reload
   ```

   The backend will be available at `http://localhost:8000`

## Frontend Setup

1. Navigate to the frontend directory:

   ```bash
   cd chatbot-ui
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



