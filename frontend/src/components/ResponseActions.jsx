import { useState } from "react";
import { CopyToClipboard } from "react-copy-to-clipboard";
import "../styles/responseactions.css";

function ResponseActions({ text }) {
    const [copied, setCopied] = useState(false);

    return (
        <div className="response-actions">
            <CopyToClipboard
                text={text}
                onCopy={() => {
                    setCopied(true);
                    setTimeout(() => {
                        setCopied(false);
                    }, 2000);
                }}
            >
                <button
                    className="response-copy"
                    type="button"
                    aria-label={copied ? "Copied" : "Copy response"}
                    title={copied ? "Copied" : "Copy response"}
                >
                    {copied ? (
                        <svg
                            aria-hidden="true"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2.5"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                        >
                            <path d="M20 6 9 17l-5-5" />
                        </svg>
                    ) : (
                        <svg
                            aria-hidden="true"
                            viewBox="0 0 24 24"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                        >
                            <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                            <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
                        </svg>
                    )}
                </button>
            </CopyToClipboard>
        </div>
    );
}

export default ResponseActions;
