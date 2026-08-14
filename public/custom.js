/**
 * Custom JavaScript for Chainlit UI Enhancement
 * Adds labels and tooltips to UI buttons
 */

(function () {
    // Wait for DOM to be ready
    function addButtonLabels() {
        // Find and label the attachment/upload button
        const attachmentButtons = document.querySelectorAll('[data-testid="button-attachment"], button[aria-label*="attach"], button[aria-label*="Attach"], [class*="attachment"]');
        attachmentButtons.forEach(btn => {
            btn.setAttribute('title', 'Upload Files (CSV/XLSX)');
            btn.setAttribute('aria-label', 'Upload Files - Click to upload CSV or XLSX files');
        });

        // Find and label send button
        const sendButtons = document.querySelectorAll('button[aria-label*="send"], button[aria-label*="Send"], [data-testid="button-send"]');
        sendButtons.forEach(btn => {
            btn.setAttribute('title', 'Send Message (Enter)');
            btn.setAttribute('aria-label', 'Send your message');
        });

        // Find and label settings button
        const settingsButtons = document.querySelectorAll('button[aria-label*="setting"], button[aria-label*="Setting"], [data-testid="button-settings"]');
        settingsButtons.forEach(btn => {
            btn.setAttribute('title', 'Settings');
            btn.setAttribute('aria-label', 'Open settings');
        });

        // Find and label input field
        const inputFields = document.querySelectorAll('input[type="text"], textarea, [class*="composer"]');
        inputFields.forEach(input => {
            if (!input.placeholder) {
                input.setAttribute('placeholder', 'Ask me a question or type a command...');
            }
            input.setAttribute('title', 'Type your question in natural language');
        });

        // Add class for styling tooltip on attachment button
        const allButtons = document.querySelectorAll('button');
        allButtons.forEach(btn => {
            const ariaLabel = btn.getAttribute('aria-label') || '';
            if (ariaLabel.toLowerCase().includes('attach') || ariaLabel.toLowerCase().includes('upload') || ariaLabel.toLowerCase().includes('file')) {
                btn.classList.add('attachment-button');
                btn.setAttribute('data-button-type', 'upload');
            } else if (ariaLabel.toLowerCase().includes('send')) {
                btn.classList.add('send-button');
                btn.setAttribute('data-button-type', 'send');
            } else if (ariaLabel.toLowerCase().includes('setting') || ariaLabel.toLowerCase().includes('config')) {
                btn.classList.add('settings-button');
                btn.setAttribute('data-button-type', 'settings');
            }
        });
    }

    // Run on initial load
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', addButtonLabels);
    } else {
        addButtonLabels();
    }

    // Watch for dynamic content changes and re-apply labels
    const observer = new MutationObserver(function (mutations) {
        // Re-apply labels when DOM changes (e.g., after scrolling, new messages)
        const hasNewButtons = mutations.some(mutation => {
            return Array.from(mutation.addedNodes).some(node =>
                (node.nodeType === 1 && node.tagName === 'BUTTON') ||
                (node.nodeType === 1 && node.querySelector && node.querySelector('button'))
            );
        });

        if (hasNewButtons) {
            setTimeout(addButtonLabels, 100);
        }
    });

    // Start observing the document for changes
    observer.observe(document.body, {
        childList: true,
        subtree: true,
        attributes: false
    });

    // Also re-run periodically to catch any missed elements
    setInterval(addButtonLabels, 2000);
})();
