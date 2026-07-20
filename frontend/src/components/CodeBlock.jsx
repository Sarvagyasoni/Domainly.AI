import { useState } from "react";
import { CopyToClipboard } from "react-copy-to-clipboard";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { tomorrow } from "react-syntax-highlighter/dist/esm/styles/prism";
import "../styles/codeblock.css";
function CodeBlock({ language, code }) {
    const [copied, setCopied] = useState(false);
    return (
        <div className="code-block">
            <div className="code-header">
                <span className="language">
                    {language || "text"}
                </span>
                <CopyToClipboard
                    text={code}
                    onCopy={() => {
                        setCopied(true);
                        setTimeout(() => {
                            setCopied(false);
                        }, 2000);
                    }}
                >
                    <button className="copy-btn">
                        {copied ? "✅ Copied!" : "📋 Copy"}
                    </button>
                </CopyToClipboard>
            </div>
            <SyntaxHighlighter
                language={language}
                style={tomorrow}
                PreTag="div"
            >
                {code}
            </SyntaxHighlighter>
        </div>
    );
}
export default CodeBlock;