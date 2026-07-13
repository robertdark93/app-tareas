document.addEventListener('DOMContentLoaded', function() {
    const profileTrigger = document.getElementById('profileTrigger');
    const profileMenu = document.getElementById('profileMenu');
    if (profileTrigger && profileMenu) {
        profileTrigger.addEventListener('click', function(e) {
            e.preventDefault();
            profileMenu.classList.toggle('open');
        });
        document.addEventListener('click', function(e) {
            if (!e.target.closest('.profile-dropdown')) {
                profileMenu.classList.remove('open');
            }
        });
    }

    const themeToggle = document.getElementById('themeToggle');
    const saved = localStorage.getItem('theme');
    if (saved === 'light') document.body.classList.add('light-theme');

    if (themeToggle) {
        themeToggle.addEventListener('click', function() {
            document.body.classList.toggle('light-theme');
            const isLight = document.body.classList.contains('light-theme');
            localStorage.setItem('theme', isLight ? 'light' : 'dark');
            themeToggle.textContent = isLight ? '🌙' : '🌓';
        });
        themeToggle.textContent = saved === 'light' ? '🌙' : '🌓';
    }

    // Notifications WebSocket — only runs when user is authenticated
    // The template wraps this in {% if user.is_authenticated %}.
    // In static JS, this depends on the presence of .notif-link in the DOM.
    const notifLink = document.querySelector('.notif-link');
    function updateNotifBadge(count) {
        let badge = document.querySelector('.notif-badge');
        if (count > 0) {
            if (badge) {
                badge.textContent = count;
            } else {
                badge = document.createElement('span');
                badge.className = 'notif-badge';
                badge.textContent = count;
                if (notifLink) notifLink.appendChild(badge);
            }
        } else if (badge) {
            badge.remove();
        }
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    // TODO: inject WebSocket URL via data-attribute on body or a meta tag
    const wsUrl = protocol + '//' + window.location.host + '/ws/notifications/';
    let ws = null;
    function connectWs() {
        ws = new WebSocket(wsUrl);
        ws.onmessage = function(e) {
            const data = JSON.parse(e.data);
            if (data.count !== undefined) updateNotifBadge(data.count);
        };
        ws.onclose = function() {
            setTimeout(connectWs, 3000);
        };
    }
    if (notifLink) {
        connectWs();
    }


});

function getCSRFToken() {
    const name = 'csrftoken';
    if (document.cookie && document.cookie !== '') {
        for (const c of document.cookie.split(';')) {
            const cookie = c.trim();
            if (cookie.startsWith(name + '=')) {
                return decodeURIComponent(cookie.substring(name.length + 1));
            }
        }
    }
    return '';
}

function showToast(msg, type) {
    const t = document.getElementById('toast-container');
    if (!t) return;
    const el = document.createElement('div');
    el.className = 'toast toast-' + (type || 'info');
    el.textContent = msg;
    t.appendChild(el);
    setTimeout(() => { el.remove(); }, 4000);
}
