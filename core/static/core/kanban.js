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
    const board = document.getElementById('kanbanBoard');
    let dragSrc = null;

    document.querySelectorAll('.kanban-card[draggable]').forEach(card => {
        card.addEventListener('dragstart', function(e) {
            dragSrc = this;
            this.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
            e.dataTransfer.setData('text/plain', this.dataset.id);
        });
        card.addEventListener('dragend', function() {
            this.classList.remove('dragging');
            document.querySelectorAll('.kanban-col').forEach(c => c.classList.remove('drag-over'));
        });
    });

    document.querySelectorAll('.kanban-col').forEach(col => {
        col.addEventListener('dragover', function(e) {
            e.preventDefault();
            this.classList.add('drag-over');
        });
        col.addEventListener('dragleave', function() {
            this.classList.remove('drag-over');
        });
        col.addEventListener('drop', function(e) {
            e.preventDefault();
            this.classList.remove('drag-over');
            const taskId = e.dataTransfer.getData('text/plain');
            const newEstado = this.dataset.estado;
            if (!taskId || !dragSrc) return;
            const oldEstado = dragSrc.closest('.kanban-col').dataset.estado;
            if (oldEstado === newEstado) return;

            const card = dragSrc;
            card.className = 'kanban-card ' + newEstado;
            this.insertBefore(card, this.querySelector('p') || null);
            updateCounts();

            // POST to server
            const updateUrl = board.dataset.updateUrl;
            const form = new FormData();
            form.append('estado', newEstado);
            fetch(updateUrl ? updateUrl.replace('0', taskId) : '/kanban/' + taskId + '/update/', {
                method: 'POST',
                headers: { 'X-CSRFToken': getCSRFToken() },
                body: form,
            }).then(r => {
                if (!r.ok) {
                    card.className = 'kanban-card ' + oldEstado;
                    const oldCol = document.querySelector(`.kanban-col[data-estado="${oldEstado}"]`);
                    if (oldCol) oldCol.insertBefore(card, oldCol.querySelector('p') || null);
                    updateCounts();
                    showToast('Error al mover la tarea', 'error');
                }
            }).catch(() => {
                card.className = 'kanban-card ' + oldEstado;
                const oldCol = document.querySelector(`.kanban-col[data-estado="${oldEstado}"]`);
                if (oldCol) oldCol.insertBefore(card, oldCol.querySelector('p') || null);
                updateCounts();
                showToast('Error de conexión', 'error');
            });
        });
    });

    function updateCounts() {
        [('pendiente'), ('proceso'), ('revision'), ('terminada')].forEach(est => {
            const col = document.querySelector(`.kanban-col[data-estado="${est}"]`);
            if (!col) return;
            const count = col.querySelectorAll('.kanban-card').length;
            const span = col.querySelector('h2 .count');
            if (span) span.textContent = count;
        });
    }
});
