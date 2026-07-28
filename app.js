document.addEventListener("DOMContentLoaded", () => {
    let allCards = [];
    let currentGame = "";

    // Elementi del DOM riutilizzabili
    const homePage = document.getElementById("homePage");
    const collectionPage = document.getElementById("collectionPage");
    const gameCardsContainer = document.getElementById("gameCards");
    const gameTitle = document.getElementById("gameTitle");
    const homeButton = document.getElementById("homeButton");
    const tableContainer = document.getElementById("tableContainer");

    // Elementi Modale per Ingrandimento Immagini
    const imageModal = document.getElementById("imageModal");
    const modalImg = document.getElementById("modalImg");
    const modalClose = document.querySelector(".modal-close");

    // Elementi Dashboard Statistiche
    const statCount = document.getElementById("statCount");
    const statV1 = document.getElementById("statV1");
    const statV2 = document.getElementById("statV2");
    const statV3 = document.getElementById("statV3");
    const barV1 = document.getElementById("barV1");
    const barV2 = document.getElementById("barV2");
    const barV3 = document.getElementById("barV3");

    // ==========================================
    // CARICAMENTO DATI (JSON)
    // ==========================================
    fetch("./collection.json")
        .then(response => {
            if (!response.ok) {
                throw new Error(`Errore di rete o file non trovato: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            allCards = data.cards || [];
            buildHome();
        })
        .catch(error => {
            console.error("Errore durante il caricamento del file JSON:", error);
            if (gameCardsContainer) {
                gameCardsContainer.innerHTML = `
                    <div style="grid-column: 1/-1; text-align: center; padding: 20px;">
                        <p style="color: #ff6b6b; font-weight: bold;">⚠️ Impossibile caricare la collezione.</p>
                        <p style="font-size: 14px; opacity: 0.8;">Verifica che il file 'collection.json' sia presente e ben formattato.</p>
                    </div>`;
            }
        });

    // ==========================================
    // COSTRUZIONE HOME PAGE
    // ==========================================
    function buildHome() {
        if (!gameCardsContainer) return;
        
        const games = [...new Set(allCards.map(c => c.game))];
        let htmlBuffer = "";

        games.forEach(game => {
            const cards = allCards.filter(c => c.game === game);
            let v1o = 0, v1m = 0, v2o = 0, v2m = 0, v3o = 0, v3m = 0;
            
            cards.forEach(c => {
                v1o += c.v1own || 0; v1m += c.v1max || 0;
                v2o += c.v2own || 0; v2m += c.v2max || 0;
                v3o += c.v3own || 0; v3m += c.v3max || 0;
            });

            const p1 = percent(v1o, v1m);
            const p2 = percent(v2o, v2m);
            const p3 = percent(v3o, v3m);

            htmlBuffer += `
            <div class="gameCard">
                <h3>${game}</h3>
                <div class="progressBlock">
                    <div>V1: ${p1}</div>
                    <div>V2: ${p2}</div>
                    <div>V3: ${p3}</div>
                </div>
                <button class="open-game-btn" data-game="${game}">Apri</button>
            </div>`;
        });
        gameCardsContainer.innerHTML = htmlBuffer;
    }

    // ==========================================
    // DELEGAZIONE DEGLI EVENTI
    // ==========================================
    if (gameCardsContainer) {
        gameCardsContainer.addEventListener("click", (event) => {
            const targetButton = event.target.closest(".open-game-btn");
            if (targetButton) {
                const gameName = targetButton.getAttribute("data-game");
                if (gameName) {
                    openGame(gameName);
                }
            }
        });
    }

    // Gestione click sulla tabella per lo Zoom On-Demand
    if (tableContainer) {
        tableContainer.addEventListener("click", (event) => {
            const targetThumb = event.target.closest(".card-thumb-placeholder");
            if (targetThumb && imageModal && modalImg) {
                const realImgUrl = targetThumb.dataset.fullSrc;
                if (realImgUrl) {
                    modalImg.src = ""; 
                    modalImg.alt = "Caricamento carta...";
                    imageModal.classList.remove("hidden");
                    modalImg.src = realImgUrl;
                }
            }
        });
    }

    if (modalClose && imageModal) {
        modalClose.addEventListener("click", () => imageModal.classList.add("hidden"));
        imageModal.addEventListener("click", (e) => {
            if (e.target === imageModal || e.target === modalClose) {
                imageModal.classList.add("hidden");
            }
        });
    }

    // ==========================================
    // APRI DETTAGLIO GIOCO
    // ==========================================
    function openGame(game) {
        currentGame = game;
        
        homePage.classList.add("hidden");
        collectionPage.classList.remove("hidden");
        gameTitle.innerText = game;

        // Reset del testo dei filtri
        document.getElementById("searchBox").value = "";
        ["hideV1", "hideV2", "hideV3"].forEach(id => {
            const cb = document.getElementById(id);
            if (cb) cb.checked = false;
        });

        requestAnimationFrame(() => {
            setTimeout(() => {
                buildFilters();
                updateTable();
            }, 0);
        });
    }

    if (homeButton) {
        homeButton.addEventListener("click", () => {
            collectionPage.classList.add("hidden");
            homePage.classList.remove("hidden");
        });
    }

    // ==========================================
    // CREAZIONE FILTRI (SET & RARITÀ)
    // ==========================================
    function buildFilters() {
        const cards = allCards.filter(c => c.game === currentGame);
        const rarity = [...new Set(cards.map(c => c.rarity))].filter(Boolean);
        const sets = [...new Set(cards.map(c => c.set))].filter(Boolean);

        const rarityDiv = document.getElementById("rarityFilter");
        const setDiv = document.getElementById("setFilter");
        if (!rarityDiv || !setDiv) return;

        rarityDiv.innerHTML = "";
        setDiv.innerHTML = "";

        rarityDiv.appendChild(makeChip("All", "rarity", "All", true));
        rarity.forEach(r => rarityDiv.appendChild(makeChip(r, "rarity", r, false)));

        setDiv.appendChild(makeChip("All", "set", "All", true));
        sets.forEach(s => setDiv.appendChild(makeChip(s, "set", s, false)));
    }

    function makeChip(label, type, value, active) {
        const b = document.createElement("button");
        b.className = "chip" + (active ? " active" : "");
        b.dataset.type = type;
        b.dataset.value = value;
        b.innerText = label;

        b.addEventListener("click", () => {
            document.querySelectorAll(`.chip[data-type="${type}"]`)
                .forEach(x => x.classList.remove("active"));
            b.classList.add("active");
            
            requestAnimationFrame(() => {
                updateTable();
            });
        });

        return b;
    }

    ["searchBox", "hideV1", "hideV2", "hideV3"].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener("input", updateTable);
    });

    // ==========================================
    // CALCOLO STATISTICHE DINAMICHE
    // ==========================================
    function updateStatistics(filteredCards, totalGameCardsCount) {
        if (!statCount) return;
        statCount.innerText = `${filteredCards.length} / ${totalGameCardsCount}`;

        let v1o = 0, v1m = 0, v2o = 0, v2m = 0, v3o = 0, v3m = 0;
        filteredCards.forEach(c => {
            v1o += c.v1own || 0; v1m += c.v1max || 0;
            v2o += c.v2own || 0; v2m += c.v2max || 0;
            v3o += c.v3own || 0; v3m += c.v3max || 0;
        });

        const p1 = percent(v1o, v1m);
        const p2 = percent(v2o, v2m);
        const p3 = percent(v3o, v3m);

        statV1.innerText = `${p1} (${v1o}/${v1m})`;
        statV2.innerText = `${p2} (${v2o}/${v2m})`;
        statV3.innerText = `${p3} (${v3o}/${v3m})`;

        barV1.style.width = v1m > 0 ? `${(v1o / v1m) * 100}%` : '0%';
        barV2.style.width = v2m > 0 ? `${(v2o / v2m) * 100}%` : '0%';
        barV3.style.width = v3m > 0 ? `${(v3o / v3m) * 100}%` : '0%';
    }

    // ==========================================
    // AGGIORNAMENTO DELLA TABELLA DATI
    // ==========================================
    function updateTable() {
        if (!tableContainer) return;
        const allGameCards = allCards.filter(c => c.game === currentGame);
        let cards = [...allGameCards];
        const search = document.getElementById("searchBox").value.trim().toLowerCase();
        
        const rarityActive = document.querySelector('.chip[data-type="rarity"].active');
        const rarity = rarityActive ? rarityActive.dataset.value : "All";
        
        const setActive = document.querySelector('.chip[data-type="set"].active');
        const set = setActive ? setActive.dataset.value : "All";

        if (search) {
            cards = cards.filter(c =>
                (c.name && c.name.toLowerCase().includes(search)) ||
                (c.tag && c.tag.toLowerCase().includes(search))
            );
        }

        if (rarity !== "All") cards = cards.filter(c => c.rarity === rarity);
        if (set !== "All") cards = cards.filter(c => c.set === set);

        if (document.getElementById("hideV1").checked) {
            cards = cards.filter(c => !( (c.v1max > 0 && c.v1own === c.v1max) || (c.v1max === 0) ));
        }
        if (document.getElementById("hideV2").checked) {
            cards = cards.filter(c => !( (c.v2max > 0 && c.v2own === c.v2max) || (c.v2max === 0) ));
        }
        if (document.getElementById("hideV3").checked) {
            cards = cards.filter(c => !( (c.v3max > 0 && c.v3own === c.v3max) || (c.v3max === 0) ));
        }

        updateStatistics(cards, allGameCards.length);

        if (cards.length === 0) {
            tableContainer.innerHTML = `
                <div style="text-align: center; padding: 40px; opacity: 0.7;">
                    Nessuna carta corrisponde ai filtri selezionati.
                </div>`;
            return;
        }

        let rowsHtml = "";
        cards.forEach(c => {
            let imgHTML = `<span class="placeholder-icon">❌</span>`;
            if (c.img) {
                imgHTML = `
                <div class="img-preview-container">
                    <div class="card-thumb-placeholder" 
                         data-full-src="${c.img}" 
                         title="Clicca per caricare l'immagine">
                         🎴
                    </div>
                </div>`;
            }

            rowsHtml += `
            <tr>
                <td>${imgHTML}</td>
                <td><strong>${c.tag || '-'}</strong></td>
                <td>${c.name || '-'}</td>
                <td>${c.rarity || '-'}</td>
                <td>${ratio(c.v1own, c.v1max)}</td>
                <td>${ratio(c.v2own, c.v2max)}</td>
                <td>${ratio(c.v3own, c.v3max)}</td>
            </tr>`;
        });

        tableContainer.innerHTML = `
        <table>
            <thead>
                <tr>
                    <th style="width: 70px;">Img</th>
                    <th>Tag</th>
                    <th>Nome</th>
                    <th>Rarità</th>
                    <th>V1</th>
                    <th>V2</th>
                    <th>V3</th>
                </tr>
            </thead>
            <tbody>
                ${rowsHtml}
            </tbody>
        </table>`;
    }

    // ==========================================
    // METODI UTILITY / HELPERS
    // ==========================================
    function percent(own, max) {
        if (!max || max === 0) return "0.00%";
        return ((own / max) * 100).toFixed(2) + "%";
    }

    function ratio(own, max) {
        if (!max || max === 0) return "-";
        return `${own} / ${max}`;
    }
});
