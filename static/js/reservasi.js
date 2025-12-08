document.addEventListener('DOMContentLoaded', () => {
    const submitBtn = document.getElementById('btn-submit-reservation');
    const modal = document.getElementById('confirmationModal');
    const confirmBtn = document.getElementById('confirmBtn');
    const cancelBtn = document.getElementById('cancelBtn');
    const form = document.getElementById('reservationForm');
    const urlParams = new URLSearchParams(window.location.search);
    const preselectId = urlParams.get('preselect');

    function openModal() {
        if (form.checkValidity()) {
            const selectedDoctor = document.querySelector('input[name="jadwal_id"]:checked');
            if (!selectedDoctor) {
                alert("Silakan pilih jadwal dokter terlebih dahulu.");
                return;
            }

            document.documentElement.style.overflow = "hidden";
            
            modal.classList.remove('hidden');
            setTimeout(() => {
                modal.classList.remove('opacity-0');
                modal.querySelector('div').classList.remove('scale-95');
                modal.querySelector('div').classList.add('scale-100');
            }, 10);
        } else {
            document.documentElement.style.overflow = "";
            form.reportValidity();
        }
    }

    function closeModal() {
        document.documentElement.style.overflow = "";
        modal.classList.add('opacity-0');
        modal.querySelector('div').classList.remove('scale-100');
        modal.querySelector('div').classList.add('scale-95');
        
        setTimeout(() => {
            modal.classList.add('hidden');
        }, 300);
    }

    submitBtn.addEventListener('click', openModal);
    
    cancelBtn.addEventListener('click', closeModal);
    
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    confirmBtn.addEventListener('click', () => {
        form.submit();
    });

    const toggle = document.getElementById('autofill-toggle');

    const inputs = [
        document.getElementById('nama'),
        document.getElementById('email'),
        document.getElementById('telepon'),
        document.getElementById('gender'),
        document.getElementById('tgl_lahir')
    ];

    function toggleFormState() {
        if(toggle.checked) {
            document.getElementById('nama').value = userData.nama || '';
            document.getElementById('email').value = userData.email || '';
            document.getElementById('telepon').value = userData.telepon || '';
            document.getElementById('gender').value = userData.gender || '';
            document.getElementById('tgl_lahir').value = userData.tgl_lahir || '';

            inputs.forEach(input => {
                input.setAttribute('readonly', true);
                input.classList.add('bg-gray-50', 'cursor-not-allowed');
                input.classList.remove('bg-white');
            });
        } else {
            
            inputs.forEach(input => {
                input.removeAttribute('readonly');
                input.classList.remove('bg-gray-50', 'cursor-not-allowed');
                input.classList.add('bg-white');
            });
        }
    }

    toggle.checked = true;
    toggleFormState();

    toggle.addEventListener('change', toggleFormState);

    if (preselectId) {
        const targetRadio = document.querySelector(`input[data-listjadwal-id="${preselectId}"]`);
        
        if (targetRadio) {
            targetRadio.checked = true;

            targetRadio.closest('label').scrollIntoView({ 
                behavior: 'smooth', 
                block: 'center' 
            });

            const card = targetRadio.nextElementSibling;
            card.classList.add('ring-2', 'ring-tm-cyan', 'ring-offset-2');
            setTimeout(() => card.classList.remove('ring-2', 'ring-tm-cyan', 'ring-offset-2'), 2000);
        }
    }
});

const applyDateBtn = document.getElementById('btn-apply-date');
const dateInput = document.getElementById('tanggal-pelayanan');

applyDateBtn.addEventListener('click', function() {
    const selectedDate = dateInput.value;
    
    if(selectedDate) {
        const url = new URL(window.location.href);
        url.searchParams.set('tanggal', selectedDate);
        window.location.href = url.toString();
    } else {
        showJsFlash("Silakan pilih tanggal terlebih dahulu.", "warning");
    }
});

function filterPoli(kategori, btn) {
    document.querySelectorAll('.filter-poli-btn').forEach(b => {
        b.classList.remove('bg-blue-600', 'text-white');
        b.classList.add('bg-white', 'text-gray-600');
    });
    btn.classList.remove('bg-white', 'text-gray-600');
    btn.classList.add('bg-blue-600', 'text-white');

    const items = document.querySelectorAll('.filter-item');
    items.forEach(item => {
        const poliName = item.getAttribute('data-poli').toLowerCase();
        if (kategori === 'Semua' || poliName.includes(kategori.toLowerCase())) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}
function showJsFlash(message, category) {
    const container = document.getElementById('flash-container');

    let colorClass = 'bg-yellow-100 text-yellow-700 border border-yellow-200';
    if (category === 'danger') {
        colorClass = 'bg-red-100 text-red-700 border border-red-200';
    } else if (category === 'success') {
        colorClass = 'bg-green-100 text-green-700 border border-green-200';
    }

    const msgDiv = document.createElement('div');
    msgDiv.className = `p-4 rounded-lg flex items-center gap-3 shadow-lg transition-all duration-500 transform opacity-0 -translate-y-2 pointer-events-auto ${colorClass}`;
    msgDiv.innerHTML = `
        <i class="fas fa-info-circle"></i>
        <span>${message}</span>
    `;

    container.appendChild(msgDiv);

    requestAnimationFrame(() => {
        msgDiv.classList.remove('opacity-0', '-translate-y-2');
        msgDiv.classList.add('opacity-100', 'translate-y-0');
    });

    setTimeout(() => {
        msgDiv.classList.remove('opacity-100', 'translate-y-0');
        msgDiv.classList.add('opacity-0', '-translate-y-2');
        setTimeout(() => msgDiv.remove(), 500); 
    }, 3000);
}
var date = new Date();
var tdatemin = date.getDate() + 1;
var tdatemax = date.getDate();
var month = date.getMonth() + 1;
if (tdatemin < 10 || tdatemax < 10) {
    tdatemin = "0" + tdatemin;
    tdatemax = "0" + tdatemax;
}
if (month < 10) {
    month = "0" + month;
}
var year = date.getUTCFullYear();
var minDate = year + "-" + month + "-" + tdatemin;
var maxDate = year + "-" + month + "-" + tdatemax;
document.getElementById("tanggal-pelayanan").setAttribute('min', minDate);
document.getElementById("tgl_lahir").setAttribute('max', maxDate);