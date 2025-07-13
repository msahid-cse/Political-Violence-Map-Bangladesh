document.addEventListener('DOMContentLoaded', () => {
    // --- Global Variables & References ---
    const API_URL = 'http://127.0.0.1:5000/api/incidents'; // ডেপ্লয়মেন্টের সময় আপনার আসল URL দিন
    let allIncidents = [];
    
    const map = L.map('map').setView([23.8, 90.35], 7);
    const markersLayer = L.layerGroup().addTo(map);

    const searchInput = document.getElementById('search-input');
    const dateFilter = document.getElementById('date-filter');
    const themeToggleBtn = document.getElementById('theme-toggle');

    // --- Tile Layers for Themes ---
    const lightTile = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap'
    });
    const darkTile = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap &copy; CARTO'
    });

    // --- Theme Management ---
    function applyTheme(theme) {
        if (theme === 'dark') {
            document.body.classList.add('dark-theme');
            themeToggleBtn.innerHTML = '<i class="fa-solid fa-sun"></i>';
            if (map.hasLayer(lightTile)) map.removeLayer(lightTile);
            darkTile.addTo(map);
        } else {
            document.body.classList.remove('dark-theme');
            themeToggleBtn.innerHTML = '<i class="fa-solid fa-moon"></i>';
            if (map.hasLayer(darkTile)) map.removeLayer(darkTile);
            lightTile.addTo(map);
        }
    }

    themeToggleBtn.addEventListener('click', () => {
        const newTheme = document.body.classList.contains('dark-theme') ? 'light' : 'dark';
        applyTheme(newTheme);
        localStorage.setItem('theme', newTheme);
    });

    // --- Map Rendering ---
    function renderMap(incidents) {
        markersLayer.clearLayers();
        
        incidents.forEach(incident => {
            const { latitude, longitude, news_title, location_name, fatalities, injuries, news_url, political_parties } = incident;

            const popupContent = `
                <b class="title">${news_title}</b>
                <b>স্থান:</b> ${location_name}<br>
                <b>নিহত:</b> ${fatalities} | <b>আহত:</b> ${injuries}<br>
                <b>জড়িত দল:</b> ${political_parties}<br>
                <a href="${news_url}" target="_blank">বিস্তারিত পড়ুন</a>
            `;
            
            L.marker([latitude, longitude]).addTo(markersLayer).bindPopup(popupContent);
        });
    }

    // --- Filtering Logic ---
    function filterAndRender() {
        let filteredData = [...allIncidents];

        const searchTerm = searchInput.value.toLowerCase();
        if (searchTerm) {
            filteredData = filteredData.filter(incident => 
                incident.news_title.toLowerCase().includes(searchTerm) ||
                (incident.political_parties && incident.political_parties.toLowerCase().includes(searchTerm))
            );
        }

        const days = parseInt(dateFilter.value);
        if (!isNaN(days)) {
            const cutoffDate = new Date();
            cutoffDate.setDate(cutoffDate.getDate() - days);
            filteredData = filteredData.filter(incident => {
                if (!incident.incident_date) return false;
                const incidentDate = new Date(incident.incident_date);
                return incidentDate >= cutoffDate;
            });
        }
        
        renderMap(filteredData);
    }

    searchInput.addEventListener('input', filterAndRender);
    dateFilter.addEventListener('change', filterAndRender);
    
    // --- Initial Data Fetch and Load ---
    function initialize() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        applyTheme(savedTheme);

        fetch(API_URL)
            .then(response => {
                if (!response.ok) throw new Error('Network response was not ok');
                return response.json();
            })
            .then(data => {
                allIncidents = data;
                renderMap(allIncidents);
            })
            .catch(error => {
                console.error('Error fetching data:', error);
                alert('ডেটা লোড করতে সমস্যা হয়েছে। অনুগ্রহ করে কিছুক্ষণ পর আবার চেষ্টা করুন।');
            });
    }

    initialize();
});
