function openBookingModal() {
    document.getElementById('bookingModal').classList.remove('hidden');
}
function closeBookingModal() {
    document.getElementById('bookingModal').classList.add('hidden');
}
function toggleReschedule(id) {
    const el = document.getElementById('reschedule-' + id);
    el.classList.toggle('hidden');
}
function toggleHighlight(checkbox) {
    if (checkbox.checked) {
        checkbox.closest('.service-item').classList.add('highlight');
    } else {
        checkbox.closest('.service-item').classList.remove('highlight');
    }
}
function openTimePicker(id) {
    document.getElementById('time-picker-modal-' + id).classList.remove('hidden');
}
function closeTimePicker(id) {
    document.getElementById('time-picker-modal-' + id).classList.add('hidden');
}
function selectTime(id, value, el) {
    document.getElementById('time-value-' + id).value = value;
    closeTimePicker(id);

    const items = document.querySelectorAll('#time-picker-modal-' + id + ' .service-item');
    items.forEach(item => item.classList.remove('highlight'));
    el.classList.add('highlight');

    const btn = document.querySelector(`#reschedule-${id} .time-picker-btn`) || 
                document.querySelector(`#bookingModal .time-picker-btn[onclick="openTimePicker('quick')"]`);
    if (btn) {
        btn.textContent = `${el.textContent}`;
    }
}

function openDatePicker() {
    const modal = document.getElementById('date-picker-modal-quick');
    modal.classList.remove('hidden');
    const grid = document.getElementById('date-grid-quick');
    grid.innerHTML = '';

    const today = new Date();
    for (let i = 0; i < 8; i++) {
        const d = new Date(today);
        d.setDate(today.getDate() + i);
        const dateStr = d.toISOString().split('T')[0];
        const label = i === 0 ? `Today (${d.getDate()} ${d.toLocaleString('default', { month: 'short' })})`
                              : `${d.getDate()} ${d.toLocaleString('default', { month: 'short' })}`;
        const div = document.createElement('div');
        div.className = 'service-item';
        div.textContent = label;
        div.onclick = function() {
            document.getElementById('date-value-quick').value = dateStr;
            closeDatePicker();
            Array.from(grid.children).forEach(c => c.classList.remove('highlight'));
            div.classList.add('highlight');

            const btn = document.querySelector('#bookingModal .form-row button.time-picker-btn[onclick="openDatePicker()"]');
            if (btn) btn.textContent = label;
        };
        grid.appendChild(div);
    }
}
function closeDatePicker() {
    document.getElementById('date-picker-modal-quick').classList.add('hidden');
}

function validateBookingForm() {
    const checked = document.querySelectorAll('#bookingModal input[name="services"]:checked');
    if (checked.length === 0) {
        document.getElementById('service-error').style.display = 'block';
        return false;
    } else {
        document.getElementById('service-error').style.display = 'none';
    }
    return true;
}
function openDeleteModal(id) {
    document.getElementById('delete-modal-' + id).classList.remove('hidden');
}
function closeDeleteModal(id) {
    document.getElementById('delete-modal-' + id).classList.add('hidden');
}
