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

document.addEventListener('DOMContentLoaded', function() {
    const list = document.getElementById('taskList');
    if (!list) return;
    let dragSrc = null;

    list.querySelectorAll('.task-item[draggable]').forEach(item => {
        item.addEventListener('dragstart', function(e) {
            dragSrc = this;
            this.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', this.dataset.id);
        });
        item.addEventListener('dragend', function() {
            this.classList.remove('dragging');
            list.querySelectorAll('.task-item').forEach(i => i.classList.remove('drag-over'));
        });
        item.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('drag-over');
        });
        item.addEventListener('dragleave', function() {
            this.classList.remove('drag-over');
        });
        item.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
            const taskId = e.dataTransfer.getData('text/plain');
            if (!taskId || !dragSrc || dragSrc === this) return;
            const parent = this.parentNode;
            const items = [...parent.querySelectorAll('.task-item')];
            const dragIdx = items.indexOf(dragSrc);
            const dropIdx = items.indexOf(this);
            if (dragIdx < dropIdx) {
                this.parentNode.insertBefore(dragSrc, this.nextSibling);
            } else {
                this.parentNode.insertBefore(dragSrc, this);
            }
            const newOrder = [...parent.querySelectorAll('.task-item')].map(i => i.dataset.id);
            const form = new FormData();
            newOrder.forEach(id => form.append('task_ids[]', id));
            fetch(list.dataset.reorderUrl, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCSRFToken() },
                body: form,
            }).then(r => {
                if (!r.ok) showToast('Error al reordenar', 'error');
            }).catch(() => showToast('Error de conexión', 'error'));
        });
    });
});
