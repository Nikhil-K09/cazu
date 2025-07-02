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

function showErrorModal(message) {
  document.getElementById('error-message').textContent = message;
  document.getElementById('error-modal').classList.remove('hidden');
}

function closeErrorModal() {
  document.getElementById('error-modal').classList.add('hidden');
}

function selectDate(id, value, el) {
    document.getElementById('date-value-' + id).value = value;
    closeDatePicker(id);

    const items = document.querySelectorAll('#date-picker-modal-' + id + ' .service-item');
    items.forEach(item => item.classList.remove('highlight'));
    el.classList.add('highlight');

    const btn = document.querySelector(`#reschedule-${id} .date-picker-btn`);
    if (btn) {
        btn.textContent = el.textContent;
    }
}
function validateBookingForm() {
  document.getElementById('service-error').style.display = 'none';
  document.getElementById('datetime-error').style.display = 'none';
  document.getElementById('past-error').style.display = 'none';

  const services = document.querySelectorAll('input[name="services"]:checked');
  const date = document.getElementById('date-value-quick').value;
  const time = document.getElementById('time-value-quick').value;

  if (services.length === 0) {
    document.getElementById('service-error').style.display = 'block';
    return false;
  }

  if (!date || !time) {
    document.getElementById('datetime-error').style.display = 'block';
    return false;
  }

  const bookingDateTime = new Date(`${date}T${time}`);
  if (bookingDateTime < new Date()) {
    document.getElementById('past-error').style.display = 'block';
    return false;
  }

  return true; // allow submit
}