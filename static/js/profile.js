const cancelModal = document.getElementById('cancelReservationModal');
const modalForm = document.getElementById('cancelReservationForm');
var date = new Date();
var tdate = date.getDate();
var month = date.getMonth() + 1;
if (tdate < 10) {
    tdate = "0" + tdate;
}
if (month < 10) {
    month = "0" + month;
}
var year = date.getUTCFullYear();
var maxDate = year + "-" + month + "-" + tdate;
document.getElementById("input-dob").setAttribute('max', maxDate);


function triggerCancelModal(actionUrl) {
    if (!actionUrl) { console.error("URL Pembatalan tidak valid"); return; }
    modalForm.action = actionUrl;
    
    cancelModal.classList.remove('hidden');
    setTimeout(() => {
        cancelModal.classList.remove('opacity-0');
        cancelModal.querySelector('div.relative').classList.remove('scale-95');
        cancelModal.querySelector('div.relative').classList.add('scale-100');
    }, 10);
}

function closeCancelModal() {
    cancelModal.classList.add('opacity-0');
    cancelModal.querySelector('div.relative').classList.remove('scale-100');
    cancelModal.querySelector('div.relative').classList.add('scale-95');
    setTimeout(() => { cancelModal.classList.add('hidden'); }, 300);
}

window.addEventListener('click', (e) => {
    if (e.target === cancelModal) closeCancelModal();
});


function switchTab(tabName) {
    const tabs = {
        'profile': document.getElementById('tab-profile'),
        'tickets': document.getElementById('tab-tickets'),
        'password': document.getElementById('tab-password')
    };
    const sections = {
        'profile': document.getElementById('section-profile'),
        'tickets': document.getElementById('section-tickets'),
        'password': document.getElementById('section-password')
    };

    const inactiveStyle = "nav-stable pb-3 text-lg font-medium text-gray-500 border-b-2 border-transparent hover:text-tm-red transition-colors duration-200 outline-none focus:outline-none focus:ring-0";
    const activeStyle = "nav-stable pb-3 text-lg font-bold text-tm-red border-b-2 border-tm-red transition-colors duration-200 outline-none focus:outline-none focus:ring-0";
    
    for (const key in tabs) { if (tabs[key]) tabs[key].className = inactiveStyle; }
    if (tabs[tabName]) tabs[tabName].className = activeStyle;

    for (const key in sections) {
        if (sections[key]) {
            sections[key].classList.add('hidden');
            sections[key].classList.remove('flex'); 
            sections[key].classList.remove('animate-fade'); 
        }
    }

    const target = sections[tabName];
    if (target) {
        target.classList.remove('hidden');
        void target.offsetWidth; 
        target.classList.add('animate-fade');

        if (tabName === 'tickets') {
            target.classList.add('flex'); 
            const vUpcoming = document.getElementById('view-upcoming');
            const vHistory = document.getElementById('view-history');
            if (vUpcoming && vHistory && vUpcoming.classList.contains('hidden') && vHistory.classList.contains('hidden')) {
                switchTicketTab('upcoming');
            }
        } else if (tabName === 'password') {
            target.classList.add('flex');
        }
        
        if (tabName !== 'profile' && typeof isEditing !== 'undefined' && isEditing) {
            toggleEditMode();
        }
    }
}

function switchTicketTab(subTabName) {
    const btnUpcoming = document.getElementById('subtab-upcoming');
    const btnHistory = document.getElementById('subtab-history');
    const viewUpcoming = document.getElementById('view-upcoming');
    const viewHistory = document.getElementById('view-history');

    if (!btnUpcoming || !btnHistory) return;

    if (subTabName === 'upcoming') {
        btnUpcoming.className = "w-1/2 py-2 rounded-full text-sm font-bold transition-all shadow-sm bg-white text-tm-red outline-none focus:outline-none";
        btnHistory.className = "w-1/2 py-2 rounded-full text-sm font-medium transition-all text-gray-500 hover:text-gray-700 outline-none focus:outline-none";
        viewUpcoming.classList.remove('hidden');
        viewHistory.classList.add('hidden');
    } else {
        btnUpcoming.className = "w-1/2 py-2 rounded-full text-sm font-medium transition-all text-gray-500 hover:text-gray-700 outline-none focus:outline-none";
        btnHistory.className = "w-1/2 py-2 rounded-full text-sm font-bold transition-all shadow-sm bg-white text-tm-red outline-none focus:outline-none";
        viewUpcoming.classList.add('hidden');
        viewHistory.classList.remove('hidden');
    }
    
    const activeView = subTabName === 'upcoming' ? viewUpcoming : viewHistory;
    activeView.classList.remove('animate-fade');
    void activeView.offsetWidth; 
    activeView.classList.add('animate-fade');
}

let isEditing = false;
function toggleEditMode() {
    const inputs = document.querySelectorAll('.profile-input');
    const selectGender = document.getElementById('input-gender');
    const iconMode = document.getElementById('icon-mode');
    const actionButtons = document.getElementById('action-buttons');

    isEditing = !isEditing;

    if (isEditing) {
        iconMode.classList.remove('fa-pen');
        iconMode.classList.add('fa-times');
        inputs.forEach(input => {
            input.removeAttribute('readonly');
            input.classList.remove('bg-transparent', 'border-gray-400');
            input.classList.add('bg-white', 'border-tm-cyan', 'ring-1', 'ring-tm-cyan');
        });
        selectGender.removeAttribute('disabled');
        selectGender.classList.remove('bg-transparent', 'cursor-default');
        selectGender.classList.add('bg-white', 'cursor-pointer', 'border-tm-cyan');
        
        actionButtons.classList.remove('hidden');
    } else {
        iconMode.classList.remove('fa-times');
        iconMode.classList.add('fa-pen');
        inputs.forEach(input => {
            input.setAttribute('readonly', true);
            input.classList.add('bg-transparent', 'border-gray-400');
            input.classList.remove('bg-white', 'border-tm-cyan', 'ring-1', 'ring-tm-cyan');
        });
        selectGender.setAttribute('disabled', true);
        selectGender.classList.add('bg-transparent', 'cursor-default');
        selectGender.classList.remove('bg-white', 'cursor-pointer', 'border-tm-cyan');
        
        actionButtons.classList.add('hidden');
    }
}

function togglePassword(inputId, btn) {
    const input = document.getElementById(inputId);
    const icon = btn.querySelector('i');
    if (input.type === 'password') {
        input.type = 'text';
        icon.classList.remove('fa-eye-slash');
        icon.classList.add('fa-eye');
    } else {
        input.type = 'password';
        icon.classList.remove('fa-eye');
        icon.classList.add('fa-eye-slash');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const tab = urlParams.get('tab');
    
    if (tab === 'tickets') {
        switchTab('tickets');
    } else if (tab === 'password') {
        switchTab('password');
    } else if (tab === 'edit') {
        switchTab('profile');
        toggleEditMode();
    } else {
        switchTab('profile');
    }
});