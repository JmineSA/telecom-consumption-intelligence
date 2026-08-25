"""
Keyboard shortcuts for power users
"""
import streamlit as st
import streamlit.components.v1 as components


class KeyboardShortcuts:
    """Keyboard shortcuts for the app"""
    
    @staticmethod
    def add_shortcuts():
        """Add keyboard shortcuts to the app"""
        components.html("""
        <script>
            document.addEventListener('keydown', function(e) {
                // Ctrl+Enter to predict
                if (e.ctrlKey && e.key === 'Enter') {
                    const predictBtn = document.querySelector('[data-testid="baseButton-secondary"]');
                    if (predictBtn) {
                        predictBtn.click();
                        e.preventDefault();
                    }
                }
                
                // Ctrl+Shift+T to train model
                if (e.ctrlKey && e.shiftKey && e.key === 'T') {
                    const trainBtn = document.querySelector('[data-testid="baseButton-primary"]');
                    if (trainBtn && trainBtn.textContent.includes('Train')) {
                        trainBtn.click();
                        e.preventDefault();
                    }
                }
                
                // Ctrl+R to retrain
                if (e.ctrlKey && e.shiftKey && e.key === 'R') {
                    const retrainBtn = document.querySelector('[data-testid="baseButton-primary"]');
                    if (retrainBtn && retrainBtn.textContent.includes('Retrain')) {
                        retrainBtn.click();
                        e.preventDefault();
                    }
                }
                
                // Ctrl+1 to Ctrl+0 for tabs
                if (e.ctrlKey && e.key >= '0' && e.key <= '9') {
                    const tabIndex = parseInt(e.key) - 1;
                    if (tabIndex >= 0) {
                        const tabs = document.querySelectorAll('[data-baseweb="tab"]');
                        if (tabs[tabIndex]) {
                            tabs[tabIndex].click();
                            e.preventDefault();
                        }
                    }
                }
                
                // Alt+S for sidebar toggle
                if (e.altKey && e.key === 's') {
                    const sidebarBtn = document.querySelector('[data-testid="collapsedControl"]');
                    if (sidebarBtn) {
                        sidebarBtn.click();
                        e.preventDefault();
                    }
                }
            });
        </script>
        """, height=0)
    
    @staticmethod
    def show_shortcuts_help():
        """Show keyboard shortcuts help"""
        with st.expander("⌨️ Keyboard Shortcuts"):
            st.markdown("""
            | Shortcut | Action |
            |----------|--------|
            | `Ctrl + Enter` | Make Prediction |
            | `Ctrl + Shift + T` | Train Model |
            | `Ctrl + Shift + R` | Retrain Model |
            | `Ctrl + 1-9` | Switch Tabs (1-9) |
            | `Ctrl + 0` | Switch to Tab 10 |
            | `Alt + S` | Toggle Sidebar |
            """)