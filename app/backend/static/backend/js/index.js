document.addEventListener('DOMContentLoaded', function () {
    const alertMessages = JSON.parse(localStorage.getItem('alertMessages'));
    // Define 'parent' as container to append success message in any html script.
    if (parent) {
        RenderSuccessDiv(parent, alertMessages);
    }

    if (alertMessages) {
        localStorage.removeItem('alertMessages');
    }
});

function RenderErrorDiv(parentElement, data) {    
    for (let field in data) {
        let errorDiv = document.createElement('div');
        let text = document.createElement('div');
        errorDiv.classList.add('custom-alerts', 'alert', 'alert-danger', 'mb-1', 'small', 'fade-in');
        text.classList.add('container');
        text.textContent = `${field.toUpperCase()}: ${data[field]}`;
        errorDiv.appendChild(text);
        if(parentElement) {
            parentElement.insertAdjacentElement("beforebegin", errorDiv);
        } else {
            console.log('nabuang na')
        }
    }

    document.querySelectorAll('.custom-alerts').forEach(el => {
        setTimeout(() => el.remove(), 10000);
    });
}

function RenderSuccessDiv(parentElement, data) {    
    for (let field in data) {
        let successDiv = document.createElement('div');
        let text = document.createElement('div');
        successDiv.classList.add('custom-alerts','alert', 'alert-success', 'mb-1', 'small', 'fade-in');
        text.classList.add('container');
        text.textContent = `${field.toUpperCase()}: ${data[field]}`;
        successDiv.appendChild(text);
        if(parentElement) {
            parentElement.insertAdjacentElement("beforebegin", successDiv);
        } else {
            console.log('nabuang na')
        }
    }

    document.querySelectorAll('.custom-alerts').forEach(el => {
        setTimeout(() => el.remove(), 10000);
    });
}

// POST Comment on Announcement
async function PostComment(btn, form) {
    if (form) {
        // Manually call input validation
        const input = form.getElementsByTagName('textarea')[0];
        if(input && !input.checkValidity()) {
            input.reportValidity();
            return;
        }

        const url = `/announcements/${btn.dataset.announcement_id}/comments/`
        const request = {
            'method': 'POST',
            'headers': {
                'Content-Type': 'application/json',
                'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value,
            },
            'body': JSON.stringify({ comment: input.value })
        };

        let spinner = document.getElementById('loading-spinner');
        
        try {
            spinner.style.display = 'block';
            window.location.href = "#";
            let response = await fetch(url, request);
            let data = await response.json();

            if (response.ok) {
                setAlertMessageInLocalStorage({'Comment': 'Successfully submitted.'});
                window.location.reload();
            } else {
                console.error(data);
                RenderErrorDiv(document.getElementById('announcement-body'), {'Comment': 'Failed to submit.'});
            }
        } catch (error) {
            console.error(error);
            window.location.href = "#";
            RenderErrorDiv(document.getElementById('announcement-body'), {'Error': 'Failed to connect to the server. Please try again.'});
        } finally {
            spinner.style.display = 'none';
        }
    }
}

function setAlertMessageInLocalStorage(data) {
    localStorage.setItem('alertMessages', JSON.stringify(data));
}

async function EditComment(btn, form) {
    if (form) {
        let commentTag = form.getElementsByTagName('textarea')[0];

        console.log(commentTag.checkValidity());
        if (commentTag && !commentTag.checkValidity()) {
            commentTag.reportValidity();
            return;
        }
        
        const url = `/announcements/${btn.dataset.announcement_id}/comments/${btn.dataset.id}/`;
        const request = {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value
            },
            body: JSON.stringify({ comment: commentTag.value })
        };
        let spinner = document.getElementById('loading-spinner');

        try {
            spinner.style.display = 'block';
            window.location.href = "#";
            let response = await fetch(url, request);
            let data = await response.json();
            if (response.ok) {
                setAlertMessageInLocalStorage({'Comment': 'Successfully updated.'});
                window.location.reload();
            } else {
                console.error(data);
                RenderErrorDiv(document.getElementById('announcement-body'), {'Comment': 'Failed to update.'});
            }
        } catch (error) {
            console.error(data);
            window.location.href = "#";
            RenderErrorDiv(document.getElementById('announcement-body'), {'Error': 'Failed to connect to the server. Please try again.'});
        } finally {
            spinner.style.display = 'none';
        }
    }
}

async function DeleteComment(announcement_id, comment_id, csrf_token) {
    try {
        let res = await fetch(`/announcements/${announcement_id}/comments/${comment_id}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrf_token
            }
        });
        let data = await res.json();

        if(res.ok) {
            setAlertMessageInLocalStorage(data);
            window.location.reload();
        } else {
            RenderErrorDiv(document.getElementById('announcement-body'), data);
        }
    } catch(error) {
        console.log('error: ', error);
        RenderErrorDiv(document.getElementById('announcement-body'), {'Error': 'Failed to connect to the server. Please try again.'});
    } finally {
        window.location.href = "#";
    }
}

function timeAgo(isoDateTime) {
    if (!isoDateTime) return "";
    
    const now = new Date();
    const date = new Date(isoDateTime);
    const diff = now - date; // difference in milliseconds
    
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (seconds < 60) {
        return `${seconds} second${seconds !== 1 ? 's' : ''} ago`;
    } else if (minutes < 60) {
        return `${minutes} minute${minutes !== 1 ? 's' : ''} ago`;
    } else if (hours < 24) {
        return `${hours} hour${hours !== 1 ? 's' : ''} ago`;
    } else {
        // Format as "Month Day, Year, Time" for dates older than 1 day
        return date.toLocaleString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric',
            hour: 'numeric',
            minute: '2-digit',
            hour12: true
        });
    }
}