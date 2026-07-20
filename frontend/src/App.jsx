import { useEffect, useState } from "react";
import "./styles/app.css";
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import { streamMessage } from "./services/api";

const domainProfiles = {
    programming: {
        name: "Programming",
        tagline: "Architecture, debugging, and modern software guidance."
    },
    gaming: {
        name: "Gaming",
        tagline: "Game strategy, setup ideas, and performance advice."
    },
    startup: {
        name: "Startup",
        tagline: "Product thinking, GTM plans, and founder support."
    },
    cybersecurity: {
        name: "Cybersecurity",
        tagline: "Security education, best practices, and threat awareness."
    },
    content_creator: {
        name: "Content Creator",
        tagline: "Content strategy, copywriting, and audience growth."
    }
};

const quickPrompts = {
    programming: [
        "Explain async/await in simple terms",
        "Help me debug a React issue"
    ],
    gaming: [
        "Recommend a high-performance gaming setup",
        "Give me a winning strategy for this game"
    ],
    startup: [
        "Help me craft a startup pitch",
        "Suggest an MVP roadmap"
    ],
    cybersecurity: [
        "Explain phishing in plain English",
        "How do I secure my home network"
    ],
    content_creator: [
        "Write a social media post for my brand",
        "Create a one-week content calendar"
    ]
};

const domainKeywords = {
    programming: ["code", "python", "javascript", "react", "debug", "api", "function", "class", "program"],
    gaming: ["game", "steam", "pc", "console", "fps", "strategy", "build", "quest", "level"],
    startup: ["founder", "mvp", "pitch", "investor", "market", "customer", "growth", "business"],
    cybersecurity: ["security", "hacker", "phishing", "password", "network", "encryption", "threat"],
    content_creator: ["content", "post", "social", "video", "copy", "brand", "marketing", "audience"]
};

const createWelcomeMessage = (domain) => ({
    id: `welcome-${domain}`,
    sender: "bot",
    type: "system",
    text: `Hello! I’m Domainly.ai. I can help with ${domainProfiles[domain].name.toLowerCase()} and related work.`
});

const createSession = (domain) => ({
    id: `${domain}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
    title: `${domainProfiles[domain].name} Chat`,
    messages: [createWelcomeMessage(domain)]
});

const buildInitialConversations = () => {
    const initial = {};
    Object.keys(domainProfiles).forEach((domain) => {
        initial[domain] = [createSession(domain)];
    });
    return initial;
};

const initialConversations = buildInitialConversations();
const initialActiveConversationIds = Object.fromEntries(
    Object.keys(initialConversations).map((domain) => [domain, initialConversations[domain][0].id])
);

function App() {
    const [conversations, setConversations] = useState(initialConversations);
    const [selectedDomain, setSelectedDomain] = useState("programming");
    const [activeConversationIds, setActiveConversationIds] = useState(initialActiveConversationIds);
    const [loading, setLoading] = useState(false);
    const [thinkingDots, setThinkingDots] = useState(".");
    const [activeController, setActiveController] = useState(null);
    const [theme, setTheme] = useState(() => localStorage.getItem("domainly-theme") || "light");

    useEffect(() => {
        if (!loading) {
            return undefined;
        }

        const frames = [".", "..", "..."];
        let index = 0;
        const interval = window.setInterval(() => {
            index = (index + 1) % frames.length;
            setThinkingDots(frames[index]);
        }, 500);

        return () => window.clearInterval(interval);
    }, [loading]);

    useEffect(() => {
        localStorage.setItem("domainly-theme", theme);
    }, [theme]);

    const currentSession = conversations[selectedDomain]?.find(
        (session) => session.id === activeConversationIds[selectedDomain]
    ) ?? conversations[selectedDomain]?.[0];

    const messages = currentSession?.messages ?? [];

    const createMessage = (sender, type, text, extra = {}) => ({
        id: `${sender}-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        sender,
        type,
        text,
        ...extra
    });

    const updateCurrentSession = (updater) => {
        setConversations((prev) => {
            const existing = prev[selectedDomain] ?? [];
            const activeId = activeConversationIds[selectedDomain] ?? existing[0]?.id;

            return {
                ...prev,
                [selectedDomain]: existing.map((session) =>
                    session.id === activeId ? updater(session) : session
                )
            };
        });
    };

    const openNewChatForDomain = (domain) => {
        const newSession = createSession(domain);
        setSelectedDomain(domain);
        setConversations((prev) => ({
            ...prev,
            [domain]: [newSession, ...(prev[domain] ?? [])]
        }));
        setActiveConversationIds((prev) => ({ ...prev, [domain]: newSession.id }));
    };

    const switchDomain = (domain) => {
        setSelectedDomain(domain);
    };

    const selectConversation = (domain, conversationId) => {
        setSelectedDomain(domain);
        setActiveConversationIds((prev) => ({ ...prev, [domain]: conversationId }));
    };

    const dismissSuggestion = (messageId) => {
        updateCurrentSession((session) => ({
            ...session,
            messages: session.messages.filter((message) => message.id !== messageId)
        }));
    };

    const detectDomain = (text) => {
        const normalized = text.toLowerCase();
        const scores = Object.entries(domainKeywords).map(([domain, keywords]) => ({
            domain,
            score: keywords.reduce((count, keyword) => count + (normalized.includes(keyword) ? 1 : 0), 0)
        }));

        const bestMatch = scores.sort((a, b) => b.score - a.score)[0];
        if (!bestMatch || bestMatch.score < 2 || bestMatch.domain === selectedDomain) {
            return null;
        }
        return bestMatch.domain;
    };

    const appendSuggestion = (suggestedDomain, messageId) => {
        updateCurrentSession((session) => ({
            ...session,
            messages: [
                ...session.messages,
                createMessage("bot", "domain_suggestion", `This looks more related to ${domainProfiles[suggestedDomain].name}. Would you like to switch domains?`, {
                    suggestedDomain,
                    relatedMessageId: messageId
                })
            ]
        }));
    };

    const handleSend = async (message) => {
        if (loading) {
            return;
        }

        const trimmed = message.trim();
        if (!trimmed) {
            return;
        }

        const domain = selectedDomain;
        const conversationId = activeConversationIds[domain] ?? conversations[domain]?.[0]?.id;
        const history = (conversations[domain]?.find((session) => session.id === conversationId)?.messages ?? [])
            .filter((msg) => msg.type === "user" || msg.type === "answer")
            .map((msg) => ({
                role: msg.sender === "bot" ? "assistant" : "user",
                content: msg.text
            }));

        const userMessage = createMessage("user", "user", trimmed);
        const botMessage = createMessage("bot", "streaming", "");

        setConversations((prev) => ({
            ...prev,
            [domain]: (prev[domain] ?? []).map((session) =>
                session.id === conversationId
                    ? {
                        ...session,
                        title: session.messages.length <= 1 ? trimmed.slice(0, 28) : session.title,
                        messages: [...session.messages, userMessage, botMessage]
                    }
                    : session
            )
        }));

        setThinkingDots(".");
        setLoading(true);
        const controller = new AbortController();
        setActiveController(controller);

        try {
            await streamMessage(
                domain,
                trimmed,
                history,
                (chunk) => {
                    setConversations((prev) => ({
                        ...prev,
                        [domain]: (prev[domain] ?? []).map((session) => {
                            if (session.id !== conversationId) {
                                return session;
                            }

                            const updatedMessages = [...session.messages];
                            updatedMessages[updatedMessages.length - 1] = {
                                ...updatedMessages[updatedMessages.length - 1],
                                text: updatedMessages[updatedMessages.length - 1].text + chunk
                            };

                            return {
                                ...session,
                                messages: updatedMessages
                            };
                        })
                    }));
                },
                controller.signal
            );

            setConversations((prev) => ({
                ...prev,
                [domain]: (prev[domain] ?? []).map((session) => {
                    if (session.id !== conversationId) {
                        return session;
                    }

                    const updatedMessages = [...session.messages];
                    updatedMessages[updatedMessages.length - 1] = {
                        ...updatedMessages[updatedMessages.length - 1],
                        type: "answer"
                    };

                    return {
                        ...session,
                        messages: updatedMessages
                    };
                })
            }));

            const suggestedDomain = detectDomain(trimmed);
            if (suggestedDomain) {
                appendSuggestion(suggestedDomain, userMessage.id);
            }
        } catch (error) {
            if (controller.signal.aborted) {
                setConversations((prev) => ({
                    ...prev,
                    [domain]: (prev[domain] ?? []).map((session) => {
                        if (session.id !== conversationId) {
                            return session;
                        }

                        const updatedMessages = [...session.messages];
                        updatedMessages[updatedMessages.length - 1] = {
                            ...updatedMessages[updatedMessages.length - 1],
                            sender: "bot",
                            type: "stopped",
                            text: "⏹️ Generation stopped."
                        };

                        return {
                            ...session,
                            messages: updatedMessages
                        };
                    })
                }));
            } else {
                console.error(error);
                setConversations((prev) => ({
                    ...prev,
                    [domain]: (prev[domain] ?? []).map((session) => {
                        if (session.id !== conversationId) {
                            return session;
                        }

                        const updatedMessages = [...session.messages];
                        updatedMessages[updatedMessages.length - 1] = {
                            sender: "bot",
                            type: "error",
                            text: "❌ The assistant is temporarily unavailable. Please try again shortly."
                        };

                        return {
                            ...session,
                            messages: updatedMessages
                        };
                    })
                }));
            }
        } finally {
            setLoading(false);
            setActiveController(null);
        }
    };

    const handleStop = () => {
        activeController?.abort();
    };

    const handleSwitchDomain = (nextDomain) => {
        switchDomain(nextDomain);
    };

    return (
        <div className="app" data-theme={theme}>
            <Navbar
                theme={theme}
                onToggleTheme={() => setTheme((current) => current === "dark" ? "light" : "dark")}
            />
            <div className="main-layout">
                <Sidebar
                    selectedDomain={selectedDomain}
                    setSelectedDomain={switchDomain}
                    conversations={conversations[selectedDomain] ?? []}
                    activeConversationId={activeConversationIds[selectedDomain]}
                    onSelectConversation={selectConversation}
                    onNewChat={() => openNewChatForDomain(selectedDomain)}
                />
                <ChatWindow
                    messages={messages}
                    onSend={handleSend}
                    onStop={handleStop}
                    loading={loading}
                    domainProfile={domainProfiles[selectedDomain]}
                    quickPrompts={quickPrompts[selectedDomain]}
                    thinkingDots={thinkingDots}
                    onSwitchDomain={handleSwitchDomain}
                    onDismissSuggestion={dismissSuggestion}
                />
            </div>
        </div>
    );
}

export default App;
