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
    // DELEGAZIONE DEGLI EVENTI SUI GIOCHI
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

    // ==========================================
    // APRI DETTAGLIO GIOCO
    // ==========================================
    function openGame(game) {
        currentGame = game;
        
        homePage.classList.add("hidden");
        collectionPage.classList.remove("hidden");
        gameTitle.innerText = game;

        document.getElementById("searchBox").value = "";
        ["hideV1", "hideV2", "hideV3"].forEach(id => {
            const cb = document.getElementById(id);
            if (cb) cb.checked = false;
        });

        buildFilters();
        updateTable();
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

    // ==========================================
    // FABBRICA DEI CHIP (BOTTONI FILTRO)
    // ==========================================
    function makeChip(label, type, value, active) {
        const b = document.createElement("button");
        b.className = "chip" + (active ? " active" : "");
        b.dataset.type = type;
        b.dataset.value = value;
        b.innerText = label;

        b.onclick = () => {
            document.querySelectorAll(`.chip[data-type="${type}"]`)
                .forEach(x => x.classList.remove("active"));
            b.classList.add("active");
            updateTable();
        };
        return b;
    }

    // ==========================================
    // ASCOLTA EVENTI DI INPUT & FILTRO
    // ==========================================
    ["searchBox", "hideV1", "hideV2", "hideV3"].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.addEventListener("input", updateTable);
    });

    // ==========================================
    // AGGIORNAMENTO DELLA TABELLA DATI
    // ==========================================
    function updateTable() {
        if (!tableContainer) return;

        let cards = allCards.filter(c => c.game === currentGame);
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

        if (rarity !== "All") {
            cards = cards.filter(c => c.rarity === rarity);
        }
        if (set !== "All") {
            cards = cards.filter(c => c.set === set);
        }

        // --- MODIFICA #1 INIZIA QUI ---
        // Filtro Checkbox di completamento (Se attivo, nasconde gli elementi completi O non applicabili)
        if (document.getElementById("hideV1").checked) {
            cards = cards.filter(c => !( (c.v1max > 0 && c.v1own === c.v1max) || (c.v1max === 0) ));
        }
        if (document.getElementById("hideV2").checked) {
            cards = cards.filter(c => !( (c.v2max > 0 && c.v2own === c.v2max) || (c.v2max === 0) ));
        }
        if (document.getElementById("hideV3").checked) {
            cards = cards.filter(c => !( (c.v3max > 0 && c.v3own === c.v3max) || (c.v3max === 0) ));
        }
        // --- MODIFICA #1 FINISCE QUI ---

        if (cards.length === 0) {
            tableContainer.innerHTML = `
                <div style="text-align: center; padding: 40px; opacity: 0.7;">
                    Nessuna carta corrisponde ai filtri selezionati.
                </div>`;
            return;
        }

        let htmlTable = `
        <table>
            <thead>
                <tr>
                    <th>Tag</th>
                    <th>Nome</th>
                    <th>Rarità</th>
                    <th>V1</th>
                    <th>V2</th>
                    <th>V3</th>
                </tr>
            </thead>
            <tbody>`;

        cards.forEach(c => {
            htmlTable += `
            <tr>
                <td><strong>${c.tag || '-'}</strong></td>
                <td>${c.name || '-'}</td>
                <td>${c.rarity || '-'}</td>
                <td>${ratio(c.v1own, c.v1max)}</td>
                <td>${ratio(c.v2own, c.v2max)}</td>
                <td>${ratio(c.v3own, c.v3max)}</td>
            </tr>`;
        });

        htmlTable += `
            </tbody>
        </table>`;

        tableContainer.innerHTML = htmlTable;
    }

    // ==========================================
    // METODI UTILITY / HELPERS
    // ==========================================
    function percent(own, max) {
        if (!max || max === 0) return "0.00%";
        return ((own / max) * 100).toFixed(2) + "%";
    }

    // --- MODIFICA #2 INIZIA QUI ---
    function ratio(own, max) {
        // Se max non è definito o è zero, mostra un trattino
        if (!max || max === 0) return "-";
        return `${own} / ${max}`;
    }
    // --- MODIFICA #2 FINISCE QUI ---
});
