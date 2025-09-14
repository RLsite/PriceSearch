/**
 * PriceHunter Frontend JavaScript
 * מטפל בכל האינטרקציות בצד הלקוח
 */

// Global variables
let searchInProgress = false;

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializePriceHunter();
});

/**
 * אתחול המערכת
 */
function initializePriceHunter() {
    console.log('🔍 PriceHunter initialized');
    
    // Setup search form if exists
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', handleSearchSubmit);
    }
    
    // Setup quick search tags
    setupQuickSearchTags();
    
    // Setup keyboard shortcuts
    setupKeyboardShortcuts();
}

/**
 * טיפול בשליחת טופס החיפוש
 */
function handleSearchSubmit(e) {
    e.preventDefault();
    
    if (searchInProgress) {
        return;
    }
    
    const searchInput = document.getElementById('searchInput');
    const query = searchInput.value.trim();
    
    if (!query) {
        showMessage('אנא הכנס מוצר לחיפוש', 'error');
        searchInput.focus();
        return;
    }
    
    // Redirect to search page
    window.location.href = `/search?q=${encodeURIComponent(query)}`;
}

/**
 * הגדרת תגיות חיפוש מהיר
 */
function setupQuickSearchTags() {
    document.querySelectorAll('.tag').forEach(tag => {
        tag.addEventListener('click', function(e) {
            e.preventDefault();
            const query = this.textContent.trim();
            
            // Update search input if exists
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {
                searchInput.value = query;
            }
            
            // Navigate to search
            window.location.href = `/search?q=${encodeURIComponent(query)}`;
        });
    });
}

/**
 * קיצורי מקלדת
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + K - focus search
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            const searchInput = document.getElementById('searchInput');
            if (searchInput) {
                searchInput.focus();
                searchInput.select();
            }
        }
        
        // Escape - clear search
        if (e.key === 'Escape') {
            const searchInput = document.getElementById('searchInput');
            if (searchInput && searchInput === document.activeElement) {
                searchInput.blur();
            }
        }
    });
}

/**
 * הצגת הודעות למשתמש
 */
function showMessage(message, type = 'info', duration = 3000) {
    // Remove existing messages
    const existingMessages = document.querySelectorAll('.message');
    existingMessages.forEach(msg => msg.remove());
    
    // Create new message
    const messageEl = document.createElement('div');
    messageEl.className = `message message-${type}`;
    messageEl.textContent = message;
    
    // Style the message
    Object.assign(messageEl.style, {
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '15px 20px',
        borderRadius: '10px',
        color: 'white',
        fontWeight: 'bold',
        zIndex: '10000',
        maxWidth: '300px',
        wordWrap: 'break-word',
        transform: 'translateX(400px)',
        transition: 'transform 0.3s ease'
    });
    
    // Set background color based on type
    const colors = {
        success: '#28a745',
        error: '#dc3545',
        warning: '#ffc107',
        info: '#17a2b8'
    };
    messageEl.style.background = colors[type] || colors.info;
    
    // Add to page
    document.body.appendChild(messageEl);
    
    // Animate in
    setTimeout(() => {
        messageEl.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after duration
    setTimeout(() => {
        messageEl.style.transform = 'translateX(400px)';
        setTimeout(() => {
            if (messageEl.parentNode) {
                messageEl.parentNode.removeChild(messageEl);
            }
        }, 300);
    }, duration);
}

/**
 * עזרה לעיצוב מחירים
 */
function formatPrice(price) {
    return new Intl.NumberFormat('he-IL', {
        style: 'currency',
        currency: 'ILS',
        minimumFractionDigits: 0
    }).format(price);
}

/**
 * הוספת אפקטים ויזואליים
 */
function addVisualEffects() {
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add loading effect to buttons
    document.querySelectorAll('.btn').forEach(btn => {
        btn.addEventListener('click', function() {
            if (!this.disabled) {
                this.style.transform = 'scale(0.95)';
                setTimeout(() => {
                    this.style.transform = '';
                }, 150);
            }
        });
    });
}

// Initialize visual effects when DOM is ready
document.addEventListener('DOMContentLoaded', addVisualEffects);

// Global functions for HTML onclick handlers
window.quickSearch = function(query) {
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.value = query;
    }
    window.location.href = `/search?q=${encodeURIComponent(query)}`;
};

window.shareProduct = function(name, price, store) {
    const text = `מצאתי את ${name} ב-${store} במחיר ${formatPrice(price)}`;
    const url = window.location.href;
    
    if (navigator.share) {
        navigator.share({
            title: 'PriceHunter - מחיר מעולה!',
            text: text,
            url: url
        });
    } else {
        // Fallback - copy to clipboard
        const fullText = `${text}\n${url}`;
        copyToClipboard(fullText);
        showMessage('הקישור הועתק!', 'success');
    }
};

function copyToClipboard(text) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.opacity = '0';
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);
}
