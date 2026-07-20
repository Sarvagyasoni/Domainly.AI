import { useEffect, useState } from "react";
import "./styles/app.css";
import Navbar from "./components/Navbar";
import Sidebar from "./components/Sidebar";
import ChatWindow from "./components/ChatWindow";
import {
    createConversation,
    deleteConversation,
    getConversations,
    streamMessage
} from "./services/api";

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

const toUiSession = (conversation) => ({
    id: conversation.id,
    title: conversation.title === "New Chat"
        ? `${domainProfiles[conversation.domain].name} Chat`
        : conversation.title,
    messages: [
        createWelcomeMessage(conversation.domain),
        ...conversation.messages.map((message, index) => ({
            id: `${conversation.id}-${message.role}-${message.timestamp}-${index}`,
            sender: message.role === "user" ? "user" : "bot",
            type: message.role === "assistant"
                ? "answer"
                : message.role === "system" ? "system" : "user",
            text: message.content
        }))
    ]
});

function App() {
    const [conversations, setConversations] = useState({});
    const [selectedDomain, setSelectedDomain] = useState("programming");
    const [activeConversationIds, setActiveConversationIds] = useState({});
    const [loading, setLoading] = useState(false);
    const [thinkingDots, setThinkingDots] = useState(".");
    const [activeController, setActiveController] = useState(null);
    const [deletingConversationId, setDeletingConversationId] = useState(null);
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

    useEffect(() => {
        let cancelled = false;
        getConversations()
            .then((savedConversations) => {
                if (cancelled) return;
                const grouped = Object.fromEntries(
                    Object.keys(domainProfiles).map((domain) => [domain, []])
                );
                savedConversations.forEach((conversation) => {
                    if (grouped[conversation.domain]) {
                        grouped[conversation.domain].push(toUiSession(conversation));
                    }
                });
                setConversations(grouped);
                setActiveConversationIds(
                    Object.fromEntries(
                        Object.entries(grouped)
                            .filter(([, sessions]) => sessions.length > 0)
                            .map(([domain, sessions]) => [domain, sessions[0].id])
                    )
                );
            })
            .catch((error) => console.error("Could not load conversations", error));
        return () => {
            cancelled = true;
        };
    }, []);

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

    const openNewChatForDomain = async (domain) => {
        try {
            const conversation = await createConversation(domain);
            const newSession = toUiSession(conversation);
            setSelectedDomain(domain);
            setConversations((prev) => ({
                ...prev,
                [domain]: [newSession, ...(prev[domain] ?? [])]
            }));
            setActiveConversationIds((prev) => ({ ...prev, [domain]: newSession.id }));
        } catch (error) {
            console.error("Could not create conversation", error);
        }
    };

    const switchDomain = (domain) => {
        setSelectedDomain(domain);
    };

    const selectConversation = (domain, conversationId) => {
        setSelectedDomain(domain);
        setActiveConversationIds((prev) => ({ ...prev, [domain]: conversationId }));
    };

    const removeConversation = async (domain, conversationId) => {
        if (deletingConversationId || (loading && activeConversationIds[domain] === conversationId)) {
            return;
        }
        setDeletingConversationId(conversationId);
        try {
            await deleteConversation(conversationId);
            const remaining = (conversations[domain] ?? []).filter(
                (conversation) => conversation.id !== conversationId
            );
            setConversations((prev) => ({
                ...prev,
                [domain]: (prev[domain] ?? []).filter(
                    (conversation) => conversation.id !== conversationId
                )
            }));
            setActiveConversationIds((prev) => {
                if (prev[domain] !== conversationId) {
                    return prev;
                }
                const next = { ...prev };
                if (remaining[0]) {
                    next[domain] = remaining[0].id;
                } else {
                    delete next[domain];
                }
                return next;
            });
        } catch (error) {
            console.error("Could not delete conversation", error);
        } finally {
            setDeletingConversationId(null);
        }
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
        let conversationId = activeConversationIds[domain] ?? conversations[domain]?.[0]?.id;
        let domainConversations = conversations[domain] ?? [];
        if (!conversationId) {
            const created = await createConversation(domain);
            const newSession = toUiSession(created);
            conversationId = created.id;
            domainConversations = [newSession];
            setConversations((prev) => ({
                ...prev,
                [domain]: [newSession, ...(prev[domain] ?? [])]
            }));
            setActiveConversationIds((prev) => ({
                ...prev,
                [domain]: conversationId
            }));
        }
        const history = (domainConversations.find((session) => session.id === conversationId)?.messages ?? [])
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
                conversationId,
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
                    onDeleteConversation={removeConversation}
                    deletingConversationId={deletingConversationId}
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
