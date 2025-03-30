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
// Ang form murag di naman needed
async function PostComment(form, announcement_id, csrf_token) {
    if (form) {
        const id = announcement_id;
        const comment = form.getElementsByTagName('textarea')[0].value;

        // Manually call input validation
        const input = form.getElementsByTagName('textarea')[0];
        if(input && !input.checkValidity()) {
            input.reportValidity();
            return;
        }

        try {
            let response = await fetch(`/announcements/${id}/comments/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrf_token,
                },
                body: JSON.stringify({
                    comment: comment,
                })
            });
            
            let data = await response.json();

            if (response.ok) {
                setAlertMessageInLocalStorage(data);
                window.location.reload();
            } else {
                // Display validation errors
                RenderErrorDiv(document.getElementById('announcement-body'), data);
            }
        } catch (error) {
            RenderErrorDiv(document.getElementById('announcement-body'), {'Error': 'Failed to connect to the server. Please try again.'});
        } finally {
            window.location.href = "#";
        }
    }
}

function setAlertMessageInLocalStorage(data) {
    localStorage.setItem('alertMessages', JSON.stringify(data));
}

async function EditComment(form, announcement_id, comment_id, csrf_token, toggleEditForm) {
    if (form) {
        let commentTag = form.getElementsByTagName('textarea')[0];
        let displayCommentTag = document.getElementById(`comment-text-${comment_id}`).firstElementChild;
        const comment = commentTag.value;

        console.log(commentTag.checkValidity());
        if (commentTag && !commentTag.checkValidity()) {
            commentTag.reportValidity();
            return;
        }

        try {
            let response = await fetch(`/announcements/${announcement_id}/comments/${comment_id}/`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrf_token
                },
                body: JSON.stringify({
                    comment: comment
                })
            });

            let data = await response.json();

            if (response.ok) {
                // setAlertMessageInLocalStorage(data);
                displayCommentTag.textContent = comment;
                RenderSuccessDiv(document.getElementById('announcement-body'), data);
                toggleEditForm(comment_id);
            } else {
                RenderErrorDiv(document.getElementById('announcement-body'), data);
            }
        } catch (error) {
            RenderErrorDiv(document.getElementById('announcement-body'), {'Error': 'Failed to connect to the server. Please try again.'});
        } finally {
            window.location.href = "#";
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