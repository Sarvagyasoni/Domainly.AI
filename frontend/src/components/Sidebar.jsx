import "../styles/domain.css";

function Sidebar({
    selectedDomain,
    setSelectedDomain,
    conversations = [],
    activeConversationId,
    onSelectConversation,
    onNewChat,
    onDeleteConversation,
    deletingConversationId
}) {
    const domains = [
        { id: "programming", name: "Programming" },
        { id: "gaming", name: "Gaming" },
        { id: "startup", name: "Startup" },
        { id: "cybersecurity", name: "Cybersecurity" },
        { id: "content_creator", name: "Content Creator" }
    ];

    return (
        <div className="sidebar">
            <div className="sidebar-title">
                <h3>Expert Domains</h3>
                <p>Switch focus instantly</p>
            </div>
            {domains.map((domain) => (
                <button
                    key={domain.id}
                    className={selectedDomain === domain.id ? "active-domain" : ""}
                    onClick={() => setSelectedDomain(domain.id)}
                >
                    {domain.name}
                </button>
            ))}

            <div className="history-section">
                <div className="history-title-row">
                    <h4>Recent chats</h4>
                    <button className="new-chat-btn" onClick={onNewChat}>+ New</button>
                </div>
                {conversations.length === 0 ? (
                    <p className="history-empty">No chats yet for this domain.</p>
                ) : (
                    conversations.map((conversation) => (
                        <div className="history-item-row" key={conversation.id}>
                            <button
                                type="button"
                                className="delete-chat-btn"
                                aria-label={`Delete ${conversation.title}`}
                                title="Delete chat"
                                disabled={deletingConversationId === conversation.id}
                                onClick={(event) => {
                                    event.stopPropagation();
                                    onDeleteConversation(selectedDomain, conversation.id);
                                }}
                            >
                                &minus;
                            </button>
                            <button
                                type="button"
                                className={`history-item ${activeConversationId === conversation.id ? "history-active" : ""}`}
                                onClick={() => onSelectConversation(selectedDomain, conversation.id)}
                            >
                                {conversation.title}
                            </button>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}

export default Sidebar;
