import axios from "axios";

const API = axios.create({
    baseURL: "http://127.0.0.1:8000"
});

export const sendMessage = async (domain, message, history) => {
    const response = await API.post("/chat", {
        domain,
        message,
        history
    });
    return response.data;
};

export const streamMessage = async (domain, message, history, onChunk, signal) => {
    const response = await fetch("http://127.0.0.1:8000/chat/stream", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            domain,
            message,
            history
        }),
        signal
    });

    if (!response.ok) {
        throw new Error("Streaming request failed");
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        onChunk(chunk);
    }
};