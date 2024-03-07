document.addEventListener('DOMContentLoaded', function () {
    const searchField = document.getElementById('coinpair_search');
    const dropdown = document.getElementById('coinpair-dropdown');

    searchField.addEventListener('input', function (e) {
        const query = e.target.value;
        if (query.length >= 2) {
            // Zeigen Sie das Dropdown an
            dropdown.style.display = 'block';
            fetch(`/api/search_coinpairs?query=${query}`)
                .then(response => response.json())
                .then(data => {
                    dropdown.innerHTML = ''; // Dropdown-Inhalt leeren
                    if (data.coinpairs && data.coinpairs.length) {
                        data.coinpairs.forEach(pair => {
                            const div = document.createElement('div');
                            div.textContent = pair.name;
                            div.className = 'dropdown-item';
                            div.onclick = function() {
                                searchField.value = pair.name;
                                dropdown.style.display = 'none'; // Verbergen Sie das Dropdown
                            };
                            dropdown.appendChild(div);
                        });
                    } else {
                        const noPairDiv = document.createElement('div');
                        noPairDiv.textContent = 'Keine Paare gefunden';
                        dropdown.appendChild(noPairDiv);
                    }
                })
                .catch(error => console.error('Error fetching coin pairs:', error));
        } else {
            dropdown.style.display = 'none';
        }
    });

    // Verbergen Sie das Dropdown, wenn das Suchfeld den Fokus verliert und kein Element ausgewählt ist.
    document.addEventListener('click', function (event) {
        if (!searchField.contains(event.target) && !dropdown.contains(event.target)) {
            dropdown.style.display = 'none';
        }
    });
});
