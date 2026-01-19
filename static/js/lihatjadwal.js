document.addEventListener('DOMContentLoaded', () => {
  const searchInput = document.getElementById('search_dokter');
  const searchClose = document.getElementById('search_close');
  const timeFilter = document.getElementById('time_filter');

  function applyFilters() {
      const activePoliBtn = document.querySelector('.filter-poli-btn.bg-tm-red');
      const poliCategory = activePoliBtn ? activePoliBtn.getAttribute('data-value') : 'Semua';
 
      const activeHariBtn = document.querySelector('.filter-hari-btn.bg-tm-red');
      const hariCategory = activeHariBtn ? activeHariBtn.getAttribute('data-value') : 'Semua';

      const searchTerm = searchInput.value.toLowerCase();
      const selectedTime = timeFilter.value; 

      const cards = document.querySelectorAll('.doctor-card');

      cards.forEach(card => {
            const poli = card.getAttribute('data-spesialis');
            const hari = card.getAttribute('data-hari');
            const name = card.querySelector('.doctor-name').innerText.toLowerCase();
            const jamMulaiStr = card.getAttribute('data-jam'); 

            let matchPoli = (poliCategory === 'Semua');
            if (!matchPoli && poli) {
                if (poli.toLowerCase().includes(poliCategory.toLowerCase())) {
                    matchPoli = true;
                }
            }

            let matchHari = (hariCategory === 'Semua');
            if (!matchHari && hari) {
                if (hari === hariCategory) {
                    matchHari = true;
                }
            }

            const matchSearch = name.includes(searchTerm);

            let matchTime = true;
            if (selectedTime !== 'all' && jamMulaiStr) {
                const jam = parseInt(jamMulaiStr.split(':')[0]);
                if (selectedTime === 'pagi') {
                    matchTime = (jam < 12); 
                } else if (selectedTime === 'siang') {
                    matchTime = (jam >= 12);
                }
            }

            if (matchPoli && matchHari && matchSearch && matchTime) {
                card.style.display = 'flex';
            } else {
                card.style.display = 'none';
            }
      });
  }

  window.filterPoli = function(kategori, btn) {
      document.querySelectorAll('.filter-poli-btn').forEach(b => {
          b.classList.remove('bg-tm-red', 'text-white', 'border-transparent');
          b.classList.add('bg-white', 'text-gray-600', 'border-gray-300');
      });
      btn.classList.remove('bg-white', 'text-gray-600', 'border-gray-300');
      btn.classList.add('bg-tm-red', 'text-white', 'border-transparent');

      applyFilters();
  }

  window.filterHari = function(hari, btn) {
        document.querySelectorAll('.filter-hari-btn').forEach(b => {
            b.classList.remove('bg-tm-red', 'text-white', 'border-transparent'); 
            b.classList.add('bg-white', 'text-gray-600', 'border-gray-300');  
        });
  
        btn.classList.remove('bg-white', 'text-gray-600', 'border-gray-300');
        btn.classList.add('bg-tm-red', 'text-white', 'border-transparent');

        applyFilters();
    }

  searchInput.addEventListener('input', () => {
      if (searchInput.value.length > 0) {
          searchClose.classList.remove('hidden');
      } else {
          searchClose.classList.add('hidden');
      }
      applyFilters();
  });

  searchClose.addEventListener('click', () => {
      searchInput.value = '';
      searchClose.classList.add('hidden');
      applyFilters();
  });

  timeFilter.addEventListener('change', applyFilters);
});