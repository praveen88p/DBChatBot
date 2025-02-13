import React, { useState } from "react";
import axios from "axios";
import "./App.css";

function App() {
    // State to store user messages and chatbot responses
    const [messages, setMessages] = useState([]);
    const [query, setQuery] = useState("");

    const formatMessage = (text) => {
        // Check if the text contains product or supplier information
        if (text.includes("Product:") || text.includes("Supplier:")) {
            // Split by the separator we added in backend
            const sections = text.split("-------------------");
            return sections.map((section, index) => (
                <div key={index} className="info-section">
                    {section.split('\n').map((line, i) => {
                        if (line.trim()) {
                            const [label, value] = line.split(":").map(s => s.trim());
                            return (
                                <div key={i} className="info-line">
                                    <strong>{label}:</strong> {value}
                                </div>
                            );
                        }
                        return null;
                    })}
                </div>
            ));
        }
        // Return regular text for normal messages
        return text;
    };

    // Function to handle sending a query to the chatbot API
    const handleSendMessage = async () => {
        if (!query.trim()) return;

        const userMessage = { text: query, sender: "user" };
        setMessages((prevMessages) => [...prevMessages, userMessage]);
        
        try {
            const response = await axios.post("http://localhost:8000/chat/", { text: query });
            const botMessage = { 
                text: response.data.response, 
                sender: "bot",
                formatted: true  // Flag to indicate this needs formatting
            };
            setMessages((prevMessages) => [...prevMessages, botMessage]);
        } catch (error) {
            console.error("Error:", error);
            const errorMessage = { 
                text: `Error: ${error.response?.data?.detail || error.message || "Unable to get response"}`, 
                sender: "bot" 
            };
            setMessages((prevMessages) => [...prevMessages, errorMessage]);
        }

        setQuery(""); // Clear input field
    };

    return (
        <div className="chat-container">
            <h1>AI Product Assistant</h1>
            <div className="chat-messages">
                {messages.map((msg, index) => (
                    <div 
                        key={index} 
                        className={`message ${msg.sender === "user" ? "user-message" : "bot-message"}`}
                    >
                        <div className="message-header">
                            {msg.sender === "user" ? "You" : "Bot"}
                        </div>
                        <div className="message-content">
                            {msg.formatted ? formatMessage(msg.text) : msg.text}
                        </div>
                    </div>
                ))}
            </div>
            <div className="chat-input">
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                    placeholder="Type your message..."
                />
                <button onClick={handleSendMessage}>Send</button>
            </div>
        </div>
    );
}

export default App;
