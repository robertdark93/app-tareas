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

document.getElementById('select-all')?.addEventListener('change', function() {
    document.querySelectorAll('.task-checkbox').forEach(cb => cb.checked = this.checked);
});

document.querySelectorAll('.status-select').forEach(sel => {
    sel.addEventListener('change', function() {
        const pk = this.dataset.pk;
        const estado = this.value;
        this.disabled = true;
        fetch('/tasks/' + pk + '/change-status/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken(),
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: 'estado=' + encodeURIComponent(estado),
        })
        .then(r => r.json())
        .then(d => {
            if (d.ok) {
                this.closest('.task-item').className = 'task-item status-' + d.estado;
            } else {
                showToast('Error al cambiar estado', 'error');
            }
        })
        .catch(() => {
            showToast('Error de conexión al cambiar estado', 'error');
        })
        .finally(() => { this.disabled = false; });
    });
});
