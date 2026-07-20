import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import CodeBlock from "./CodeBlock";
import "../styles/message.css";
import ResponseActions from "./ResponseActions";

function Message({ sender, type, text, thinkingDots, isLatest }) {
    const isUser = sender === "user";
    const isThinking = sender === "bot" && type === "streaming" && isLatest;

    return (
        <div className={`message-row ${isUser ? "user-row" : "bot-row"}`}>
            <div className="message-stack">
                <div className={`message-bubble ${isUser ? "user-message" : "bot-message"}`}>
                    <div className="message-content">
                        {text && !isThinking ? (
                            <ReactMarkdown
                                remarkPlugins={[remarkGfm]}
                                components={{
                                    code({ className, children }) {
                                        const match = /language-(\w+)/.exec(className || "");
                                        const codeString = String(children).replace(/\n$/, "");
                                        // react-markdown v10 no longer passes an `inline` prop,
                                        // so we infer it: real fenced code blocks either have a
                                        // language class or span multiple lines. Anything else
                                        // (like a single word in single backticks) is inline.
                                        const isInline = !match && !codeString.includes("\n");

                                        if (!isInline) {
                                            return (
                                                <CodeBlock
                                                    language={match ? match[1] : "text"}
                                                    code={codeString}
                                                />
                                            );
                                        }
                                        return <code className={className}>{children}</code>;
                                    }
                                }}
                            >
                                {text}
                            </ReactMarkdown>
                        ) : null}
                        {isThinking ? (
                            <span className="thinking-indicator" aria-label={`Thinking${thinkingDots}`}>
                                <span className="thinking-dot" />
                                <span className="thinking-dot" />
                                <span className="thinking-dot" />
                            </span>
                        ) : null}
                    </div>
                </div>
                {sender === "bot" && type === "answer" && text.trim() !== "" && (
                    <ResponseActions text={text} />
                )}
            </div>
        </div>
    );
}

export default Message;
