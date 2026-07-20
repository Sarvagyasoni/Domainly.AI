import { useEffect, useRef, useState } from "react";
import "../styles/chat.css";
import ChatInput from "./ChatInput";
import Message from "./Message";

function ChatWindow({
    messages,
    onSend,
    onStop,
    loading,
    domainProfile,
    quickPrompts,
    thinkingDots,
    onSwitchDomain,
    onDismissSuggestion
}) {
    const messagesEndRef = useRef(null);
    const messagesContainerRef = useRef(null);
    const [autoScroll, setAutoScroll] = useState(true);

    useEffect(() => {
        if (autoScroll) {
            messagesEndRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
        }
    }, [messages, autoScroll]);

    useEffect(() => {
        const container = messagesContainerRef.current;
        if (!container) {
            return undefined;
        }

        const handleScroll = () => {
            const distanceFromBottom = container.scrollHeight - container.scrollTop - container.clientHeight;
            setAutoScroll(distanceFromBottom < 80);
        };

        container.addEventListener("scroll", handleScroll, { passive: true });
        return () => container.removeEventListener("scroll", handleScroll);
    }, []);

    const latestBotMessage = [...messages].reverse().find((msg) => msg.sender === "bot");

    return (
        <div className="chat-window">
            <div className="chat-shell">
                <div className="chat-hero">
                    <div>
                        <p className="eyebrow">Multi-Domain Assistant</p>
                        <h1>Domainly.ai</h1>
                        <p className="hero-copy">
                            Specialized guidance for {domainProfile.name.toLowerCase()} and other high-impact work.
                        </p>
                    </div>
                </div>

                <div className="messages" ref={messagesContainerRef}>
                    {messages.length <= 1 && (
                        <div className="welcome-card">
                            <h3>How can I help you today?</h3>
                            <p>{domainProfile.tagline}</p>
                            <div className="quick-prompts">
                                {quickPrompts.map((prompt) => (
                                    <button key={prompt} onClick={() => onSend(prompt)}>
                                        {prompt}
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}

                    {messages.map((msg, index) => (
                        <div key={msg.id ?? index}>
                            {msg.type === "domain_suggestion" ? (
                                <div className="domain-suggestion">
                                    <p>{msg.text}</p>
                                    <div className="suggestion-actions">
                                        <button onClick={() => onSwitchDomain(msg.suggestedDomain)}>Switch domain</button>
                                        <button className="secondary" onClick={() => onDismissSuggestion(msg.id)}>
                                            Dismiss
                                        </button>
                                    </div>
                                </div>
                            ) : (
                                <Message
                                    sender={msg.sender}
                                    type={msg.type}
                                    text={msg.text}
                                    thinkingDots={thinkingDots}
                                    isLatest={msg.id === latestBotMessage?.id}
                                />
                            )}
                        </div>
                    ))}
                    <div ref={messagesEndRef}></div>
                </div>

                <ChatInput onSend={onSend} onStop={onStop} loading={loading} thinkingDots={thinkingDots} />
            </div>
        </div>
    );
}

export default ChatWindow;
