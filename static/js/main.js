// Initialize sidebar functionality
document.addEventListener('DOMContentLoaded', function() {
    // Set active menu item based on current page
    const currentPath = window.location.pathname;
    const menuLinks = document.querySelectorAll('.sidebar-menu a');
    
    menuLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    // Flash message auto-dismiss
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            setTimeout(() => {
                message.remove();
            }, 300);
        }, 5000);
    });

    // Template selection handler
    const templateSelect = document.getElementById('template');
    if (templateSelect) {
        templateSelect.addEventListener('change', function() {
            loadTemplate(this);
        });
    }

    // Select all recipients checkbox
    const selectAllCheckbox = document.getElementById('select-all');
    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const recipientCheckboxes = document.querySelectorAll('input[name="recipients"]');
            recipientCheckboxes.forEach(checkbox => {
                checkbox.checked = this.checked;
                updateRecipientCard(checkbox);
            });
            updateSelectedCount();
            updateEmailPreview();
        });
    }

    // Initialize alphabet filtering
    initAlphabetFilter();

    // Initialize recipient cards
    initRecipientCards();

    // Initialize recipient search
    initRecipientSearch();

    // Initialize email preview
    initEmailPreview();

    // Initialize collapse/expand functionality
    initCollapseExpand();

    // Form validation
    const emailForm = document.getElementById('email-form');
    if (emailForm) {
        emailForm.addEventListener('submit', function(event) {
            const recipients = document.querySelectorAll('input[name="recipients"]:checked');
            const subject = document.getElementById('subject').value;
            const body = document.getElementById('body').value;
            
            if (recipients.length === 0) {
                event.preventDefault();
                showAlert('Please select at least one recipient', 'error');
            } else if (!subject.trim()) {
                event.preventDefault();
                showAlert('Subject is required', 'error');
            } else if (!body.trim()) {
                event.preventDefault();
                showAlert('Email body is required', 'error');
            }
        });
    }

    // Initialize real-time input for email preview
    const subjectInput = document.getElementById('subject');
    const bodyInput = document.getElementById('body');
    
    if (subjectInput && bodyInput) {
        subjectInput.addEventListener('input', updateEmailPreview);
        bodyInput.addEventListener('input', updateEmailPreview);
    }

    // Initialize send type toggle
    const sendTypeRadios = document.querySelectorAll('input[name="send_type"]');
    if (sendTypeRadios.length) {
        sendTypeRadios.forEach(radio => {
            radio.addEventListener('change', updateEmailPreview);
        });
    }
});

// Template loading function
function loadTemplate(selectElement) {
    const value = selectElement.value;
    if (value) {
        const parts = value.split('|||');
        document.getElementById('subject').value = parts[0];
        document.getElementById('body').value = parts[1];
        updateEmailPreview();
    }
}

// Show alert function
function showAlert(message, type) {
    const alertsContainer = document.querySelector('.flash-messages');
    if (!alertsContainer) {
        const container = document.createElement('div');
        container.className = 'flash-messages';
        document.body.appendChild(container);
    }
    
    const alert = document.createElement('div');
    alert.className = `flash-message flash-${type}`;
    alert.textContent = message;
    
    document.querySelector('.flash-messages').appendChild(alert);
    
    setTimeout(() => {
        alert.style.opacity = '0';
        setTimeout(() => {
            alert.remove();
        }, 300);
    }, 5000);
}

// Initialize alphabet filter
function initAlphabetFilter() {
    const alphabetContainer = document.getElementById('recipients-alphabet');
    if (!alphabetContainer) return;

    const alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');
    
    // Create alphabet buttons
    alphabet.forEach(letter => {
        const letterBtn = document.createElement('div');
        letterBtn.className = 'alphabet-letter';
        letterBtn.textContent = letter;
        letterBtn.addEventListener('click', () => {
            // Remove active class from all letters
            document.querySelectorAll('.alphabet-letter').forEach(el => {
                el.classList.remove('active');
            });
            
            // Add active class to clicked letter
            letterBtn.classList.add('active');
            
            // Filter recipients by letter
            filterRecipientsByLetter(letter);
        });
        alphabetContainer.appendChild(letterBtn);
    });

    // Add "All" button
    const allBtn = document.createElement('div');
    allBtn.className = 'alphabet-letter active';
    allBtn.textContent = 'All';
    allBtn.addEventListener('click', () => {
        // Remove active class from all letters
        document.querySelectorAll('.alphabet-letter').forEach(el => {
            el.classList.remove('active');
        });
        
        // Add active class to "All" button
        allBtn.classList.add('active');
        
        // Show all recipients
        showAllRecipients();
    });
    alphabetContainer.prepend(allBtn);
}

// Filter recipients by letter
function filterRecipientsByLetter(letter) {
    const recipientCards = document.querySelectorAll('.recipient-card');
    recipientCards.forEach(card => {
        const name = card.querySelector('.recipient-name').textContent.trim();
        if (name.toUpperCase().startsWith(letter)) {
            card.style.display = 'flex';
        } else {
            card.style.display = 'none';
        }
    });
}

// Show all recipients
function showAllRecipients() {
    const recipientCards = document.querySelectorAll('.recipient-card');
    recipientCards.forEach(card => {
        card.style.display = 'flex';
    });
}

// Initialize recipient cards
function initRecipientCards() {
    const recipientCheckboxes = document.querySelectorAll('input[name="recipients"]');
    recipientCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            updateRecipientCard(this);
            updateSelectedCount();
            updateEmailPreview();
        });
        
        // Initialize card state
        updateRecipientCard(checkbox);
    });
    
    // Initial count update
    updateSelectedCount();
}

// Update recipient card based on checkbox state
function updateRecipientCard(checkbox) {
    const card = checkbox.closest('.recipient-card');
    if (card) {
        if (checkbox.checked) {
            card.classList.add('selected');
        } else {
            card.classList.remove('selected');
        }
    }
}

// Update selected recipients count
function updateSelectedCount() {
    const selectedCount = document.querySelectorAll('input[name="recipients"]:checked').length;
    const totalCount = document.querySelectorAll('input[name="recipients"]').length;
    const countElement = document.getElementById('selected-count');
    
    if (countElement) {
        countElement.textContent = `${selectedCount} of ${totalCount} selected`;
    }
    
    // Update tags container
    updateSelectedTags();
}

// Update selected recipients tags
function updateSelectedTags() {
    const tagsContainer = document.getElementById('selected-tags');
    if (!tagsContainer) return;
    
    // Clear existing tags
    tagsContainer.innerHTML = '';
    
    // Get selected recipients
    const selectedCheckboxes = document.querySelectorAll('input[name="recipients"]:checked');
    
    // Create tags for selected recipients (max 5, then show count)
    const maxVisibleTags = 5;
    let visibleCount = 0;
    
    selectedCheckboxes.forEach((checkbox, index) => {
        if (index < maxVisibleTags) {
            const card = checkbox.closest('.recipient-card');
            if (card) {
                const name = card.querySelector('.recipient-name').textContent.trim();
                
                const tag = document.createElement('div');
                tag.className = 'recipient-tag';
                tag.innerHTML = `${name} <i class="fas fa-times"></i>`;
                
                // Add remove functionality
                tag.querySelector('i').addEventListener('click', () => {
                    checkbox.checked = false;
                    updateRecipientCard(checkbox);
                    updateSelectedCount();
                    updateEmailPreview();
                });
                
                tagsContainer.appendChild(tag);
                visibleCount++;
            }
        }
    });
    
    // If more than maxVisibleTags, show count
    if (selectedCheckboxes.length > maxVisibleTags) {
        const moreTag = document.createElement('div');
        moreTag.className = 'recipient-tag';
        moreTag.textContent = `+${selectedCheckboxes.length - maxVisibleTags} more`;
        tagsContainer.appendChild(moreTag);
    }
}

// Initialize recipient search
function initRecipientSearch() {
    const searchInput = document.getElementById('search-recipients');
    if (!searchInput) return;
    
    searchInput.addEventListener('input', function() {
        const searchTerm = this.value.toLowerCase();
        const recipientCards = document.querySelectorAll('.recipient-card');
        
        recipientCards.forEach(card => {
            const name = card.querySelector('.recipient-name').textContent.toLowerCase();
            const email = card.querySelector('.recipient-email').textContent.toLowerCase();
            
            if (name.includes(searchTerm) || email.includes(searchTerm)) {
                card.style.display = 'flex';
            } else {
                card.style.display = 'none';
            }
        });
        
        // Reset alphabet filter
        document.querySelectorAll('.alphabet-letter').forEach(el => {
            el.classList.remove('active');
        });
        
        // Set "All" as active
        const allBtn = document.querySelector('.alphabet-letter');
        if (allBtn) {
            allBtn.classList.add('active');
        }
    });
}

// Initialize email preview
function initEmailPreview() {
    // Initial preview update
    updateEmailPreview();
}

// Update email preview
function updateEmailPreview() {
    const previewSubject = document.getElementById('preview-subject');
    const previewBody = document.getElementById('preview-body');
    const previewSignature = document.getElementById('preview-signature');
    
    if (!previewSubject || !previewBody) return;
    
    const subject = document.getElementById('subject').value || 'Your email subject';
    const body = document.getElementById('body').value || 'Your email content';
    
    // Update subject
    previewSubject.textContent = subject;
    
    // Update body with personalization and links
    let formattedBody = body.replace(/\n/g, '<br>');
    
    // Replace {name} with "Sample Name"
    formattedBody = formattedBody.replace(/\{name\}/g, '<span style="color: #007BFF;">Sample Name</span>');
    
    // Replace [text]{url} with links
    formattedBody = formattedBody.replace(/\[([^\]]+)\]\{([^\}]+)\}/g, '<a href="$2" style="color: #007BFF; text-decoration: underline;">$1</a>');
    
    previewBody.innerHTML = formattedBody;
    
    // Update signature if available
    if (previewSignature) {
        // We'll use a placeholder signature for the preview
        previewSignature.innerHTML = '<div style="color: #666;">Best regards,<br>Your Name<br>Your Company</div>';
    }
    
    // Update recipient in preview
    updatePreviewRecipient();
}

// Update recipient in preview
function updatePreviewRecipient() {
    const previewTo = document.getElementById('preview-to');
    if (!previewTo) return;
    
    const selectedRecipients = document.querySelectorAll('input[name="recipients"]:checked');
    const sendType = document.querySelector('input[name="send_type"]:checked').value;
    
    if (selectedRecipients.length === 0) {
        previewTo.textContent = 'No recipients selected';
        return;
    }
    
    if (sendType === 'to') {
        if (selectedRecipients.length === 1) {
            const card = selectedRecipients[0].closest('.recipient-card');
            const name = card ? card.querySelector('.recipient-name').textContent.trim() : '';
            const email = selectedRecipients[0].value;
            previewTo.textContent = `To: ${name} <${email}>`;
        } else {
            previewTo.textContent = `To: ${selectedRecipients.length} recipients`;
        }
    } else {
        previewTo.textContent = `BCC: ${selectedRecipients.length} recipients`;
    }
}

// Initialize collapse/expand functionality
function initCollapseExpand() {
    const collapseBtn = document.getElementById('recipients-collapse');
    const recipientsContainer = document.getElementById('recipients-list');
    
    if (!collapseBtn || !recipientsContainer) return;
    
    collapseBtn.addEventListener('click', function() {
        if (this.classList.contains('collapsed')) {
            // Expand
            recipientsContainer.style.maxHeight = '400px';
            this.classList.remove('collapsed');
            this.innerHTML = 'Collapse <i class="fas fa-chevron-up"></i>';
        } else {
            // Collapse
            recipientsContainer.style.maxHeight = '0';
            this.classList.add('collapsed');
            this.innerHTML = 'Expand <i class="fas fa-chevron-down"></i>';
        }
    });
}

// Get initials from name
function getInitials(name) {
    return name
        .split(' ')
        .map(part => part.charAt(0))
        .join('')
        .toUpperCase()
        .substring(0, 2);
}
