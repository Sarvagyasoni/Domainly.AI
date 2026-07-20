import { useEffect, useRef, useState } from "react";
import "../styles/input.css";

function ChatInput({ onSend, onStop, loading, thinkingDots }) {
    const [message, setMessage] = useState("");
    const [isMultiline, setIsMultiline] = useState(false);
    const textareaRef = useRef(null);

    useEffect(() => {
        const textarea = textareaRef.current;
        if (!textarea) {
            return;
        }

        textarea.style.height = "auto";
        const nextHeight = Math.min(textarea.scrollHeight, 180);
        textarea.style.height = `${nextHeight}px`;
        setIsMultiline(textarea.scrollHeight > 52);
    }, [message]);

    const handleSend = () => {
        const trimmed = message.trim();
        if (!trimmed || loading) return;
        onSend(trimmed);
        setMessage("");
    };

    return (
        <div className={`chat-input-container ${isMultiline ? "input-multiline" : ""}`}>
            <textarea
                ref={textareaRef}
                placeholder="Ask for a plan, explanation, draft, or strategy..."
                value={message}
                disabled={loading}
                rows={1}
                onChange={(e) => setMessage(e.target.value)}
                onKeyDown={(e) => {
                    if (e.key === "Enter" && !e.shiftKey) {
                        e.preventDefault();
                        handleSend();
                    }
                }}
            />
            {loading ? (
                <button onClick={onStop} className="stop-button">
                    Stop{thinkingDots}
                </button>
            ) : (
                <button onClick={handleSend}>Send</button>
            )}
        </div>
    );
}

export default ChatInput;
