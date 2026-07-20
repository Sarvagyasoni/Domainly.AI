import "../styles/navbar.css";

function Navbar({ theme, onToggleTheme }) {
    const isDark = theme === "dark";

    return (
        <div className="navbar">
            <div className="brand-block">
                <div>
                    <h2>Domainly.ai</h2>
                    <p>Your multi-domain assistant</p>
                </div>
            </div>
            <button
                className="theme-toggle"
                type="button"
                onClick={onToggleTheme}
                aria-label={`Switch to ${isDark ? "light" : "dark"} mode`}
                title={`Switch to ${isDark ? "light" : "dark"} mode`}
            >
                <span className="theme-icon" aria-hidden="true">
                    {isDark ? "☀" : "☾"}
                </span>
            </button>
        </div>
    );
}

export default Navbar;
