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

// Inline hours conversion (from the complete-section script in the template)
document.querySelector('.complete-section form')?.addEventListener('submit', function() {
    const h = parseInt(document.getElementById('horas_h').value) || 0;
    const m = parseInt(document.getElementById('horas_m').value) || 0;
    document.getElementById('horas_tomadas').value = h + (m / 60);
});

document.addEventListener('DOMContentLoaded', function() {
    // Share button
    const shareBtn = document.getElementById('shareBtn');
    if (shareBtn) {
        shareBtn.addEventListener('click', function() {
            // TODO: inject task detail URL via data-attribute instead of Django template tag
            // Original: window.location.origin + '{% url "task_detail" tarea.id %}'
            const url = window.location.origin + '/tasks/' + shareBtn.dataset.pk + '/';
            fallbackCopy(url);
        });
        function fallbackCopy(url) {
            if (navigator.clipboard) {
                navigator.clipboard.writeText(url).then(showCopied).catch(() => promptCopy(url));
            } else {
                promptCopy(url);
            }
        }
        function promptCopy(url) {
            const input = document.createElement('input');
            input.value = url;
            input.style.position = 'fixed'; input.style.opacity = '0';
            document.body.appendChild(input);
            input.select();
            try { document.execCommand('copy'); showCopied(); }
            catch (e) { prompt('Copiar enlace:', url); }
            document.body.removeChild(input);
        }
        function showCopied() {
            const orig = shareBtn.textContent;
            shareBtn.textContent = '✅';
            setTimeout(() => { shareBtn.textContent = orig; }, 2000);
        }
    }

    // Subtask drag & drop reorder
    const subtaskList = document.getElementById('subtaskList');
    if (subtaskList) {
        let dragItem = null;
        subtaskList.querySelectorAll('li[draggable]').forEach(li => {
            li.addEventListener('dragstart', function(e) {
                dragItem = this;
                this.style.opacity = '0.4';
                e.dataTransfer.effectAllowed = 'move';
            });
            li.addEventListener('dragend', function() {
                this.style.opacity = '1';
                document.querySelectorAll('#subtaskList li').forEach(l => l.style.borderTop = '');
            });
            li.addEventListener('dragover', function(e) {
                e.preventDefault();
                if (this !== dragItem) {
                    const rect = this.getBoundingClientRect();
                    const after = e.clientY > rect.top + rect.height / 2;
                    this.style.borderTop = after ? '' : '2px solid var(--accent)';
                }
            });
            li.addEventListener('dragleave', function() { this.style.borderTop = ''; });
            li.addEventListener('drop', function(e) {
                e.preventDefault();
                this.style.borderTop = '';
                if (dragItem && this !== dragItem) {
                    const rect = this.getBoundingClientRect();
                    const after = e.clientY > rect.top + rect.height / 2;
                    if (after) {
                        this.parentNode.insertBefore(dragItem, this.nextSibling);
                    } else {
                        this.parentNode.insertBefore(dragItem, this);
                    }
                    // save new order
                    const ids = [...subtaskList.querySelectorAll('li[draggable]')].map(li => li.dataset.id);
                    const form = new FormData();
                    ids.forEach(id => form.append('subtask_ids[]', id));
                    const reorderUrl = subtaskList.dataset.reorderUrl
                        || ('/tasks/' + (subtaskList.dataset.taskPk || '') + '/reorder-subtasks/');
                    fetch(reorderUrl, {
                        method: 'POST',
                        headers: { 'X-CSRFToken': getCSRFToken() },
                        body: form,
                    });
                }
            });
        });
    }

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            document.querySelectorAll('.message').forEach(m => m.remove());
        }
    });

    // Watch / Unwatch
    const watchBtn = document.getElementById('watchBtn');
    if (watchBtn) {
        let watching = watchBtn.dataset.watching === 'true';
        watchBtn.addEventListener('click', function() {
            // TODO: inject watch/unwatch URLs via data-attributes
            // Original: watching ? '{% url "unwatch_task" tarea.id %}' : '{% url "watch_task" tarea.id %}'
            const url = watching ? '/tasks/' + watchBtn.dataset.pk + '/unwatch/' : '/tasks/' + watchBtn.dataset.pk + '/watch/';
            fetch(url, { method: 'POST', headers: { 'X-CSRFToken': getCSRFToken() } })
                .then(r => r.json())
                .then(d => {
                    watching = d.watching;
                    watchBtn.textContent = watching ? '🔔' : '🔕';
                    watchBtn.dataset.watching = watching ? 'true' : 'false';
                    watchBtn.title = watching ? 'Dejar de seguir' : 'Seguir esta tarea';
                })
                .catch(() => {});
        });
    }

    // Inline status change
    const statusSelect = document.querySelector('.status-select-detail');
    if (statusSelect) {
        statusSelect.addEventListener('change', function() {
            const pk = this.dataset.pk;
            const estado = this.value;
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
                    document.querySelector('.status-badge').textContent = d.display;
                    document.querySelector('.status-badge').className = 'badge status-badge ' + d.estado;
                }
            })
            .catch(() => {});
        });
    }
});
