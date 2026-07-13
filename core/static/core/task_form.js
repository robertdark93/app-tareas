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

// Hours/minutes to decimal conversion for horas_tomadas and horas_estimadas fields
// These are invoked per-field by inline scripts in the template.
// In static form, this function can be called for each field.
function initHoursField(fieldName) {
    const field = document.getElementById('id_' + fieldName);
    const hInp = document.getElementById('id_' + fieldName + '_h');
    const mInp = document.getElementById('id_' + fieldName + '_m');
    if (!field || !hInp || !mInp) return;
    field.type = 'hidden';
    if (field.value) {
        const v = parseFloat(field.value) || 0;
        hInp.value = Math.floor(v);
        mInp.value = Math.round((v - Math.floor(v)) * 60);
    }
    function sync() {
        const h = parseInt(hInp.value) || 0;
        const m = parseInt(mInp.value) || 0;
        field.value = h + (m / 60);
    }
    hInp.addEventListener('input', sync);
    mInp.addEventListener('input', sync);
}

document.addEventListener('DOMContentLoaded', function() {
    // Initialize flatpickr on elements with .datepicker and .datetimepicker
    // Requires flatpickr library to be loaded separately
    if (typeof flatpickr !== 'undefined') {
        flatpickr('.datepicker', {
            locale: 'es',
            dateFormat: 'd/m/Y',
            allowInput: true,
        });
        flatpickr('.datetimepicker', {
            locale: 'es',
            enableTime: true,
            dateFormat: 'd/m/Y H:i',
            time_24hr: true,
            allowInput: true,
        });
    }
});

// Task lock on edit — called when the page contains an object (edit mode)
// Expects pk and csrfToken to be available, or reads from DOM data-attributes
function acquireLock(pk, csrfToken) {
    // TODO: inject lock/unlock URLs via data-attributes
    // Original: '{% url "task_lock" object.id %}'
    fetch('/tasks/' + pk + '/lock/', {
        method: 'POST',
        headers: { 'X-CSRFToken': csrfToken },
    }).catch(() => {});

    // Release lock when leaving
    window.addEventListener('beforeunload', function() {
        navigator.sendBeacon('/tasks/' + pk + '/unlock/', new URLSearchParams({csrfmiddlewaretoken: csrfToken}));
    });

    const cancelBtn = document.getElementById('cancelEditBtn');
    if (cancelBtn) {
        cancelBtn.addEventListener('click', function(e) {
            e.preventDefault();
            // TODO: inject unlock URL via data-attribute
            fetch('/tasks/' + pk + '/unlock/', {
                method: 'POST',
                headers: { 'X-CSRFToken': csrfToken },
            }).finally(() => {
                window.location.href = this.href;
            });
        });
    }
}
