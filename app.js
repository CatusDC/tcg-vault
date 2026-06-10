document.addEventListener("DOMContentLoaded", () => {

let allCards = [];
let currentGame = "";

// =========================
// LOAD DATA
// =========================
fetch("./collection.json")
.then(r => r.json())
.then(data => {
    allCards = data.cards;
    buildHome();
});

// =========================
// HELPERS
// =========================
function calcPercent(own, max) {
    if (!max || max === 0) return "N/A";
    return ((own / max) * 100).toFixed(2) + "%";
}

function safeRatio(own, max) {
    if (!max || max === 0) return "N/A";
    return `${own} / ${max}`;
}

// =========================
// HOME (GRID RESPONSIVE)
// =========================
function buildHome(){

    const container = document.getElementById("gameCards");
    container.innerHTML = "";

    const games = [...new Set(allCards.map(c => c.game))];

    games.forEach(game => {

        const cards = allCards.filter(c => c.game === game);

        let v1own=0,v1max=0;
        let v2own=0,v2max=0;
        let v3own=0,v3max=0;

        cards.forEach(c => {
            v1own += c.v1own; v1max += c.v1max;
            v2own += c.v2own; v2max += c.v2max;
            v3own += c.v3own; v3max += c.v3max;
        });

        const v1 = calcPercent(v1own, v1max);
        const v2 = calcPercent(v2own, v2max);
        const v3 = calcPercent(v3own, v3max);

        container.innerHTML += `
        <div class="gameCard">
            <h3>${game}</h3>

            <div class="progressBlock">
                <div>V1: ${v1}</div>
                <div>V2: ${v2}</div>
                <div>V3: ${v3}</div>
            </div>

            <button onclick="openGame('${game}')">Apri</button>
        </div>`;
    });
}

// =========================
// OPEN GAME
// =========================
window.openGame = function(game){

    currentGame = game;

    document.getElementById("homePage").classList.add("hidden");
    document.getElementById("collectionPage").classList.remove("hidden");

    document.getElementById("gameTitle").innerText = game;

    buildFilters();
    updateTable();
};

// =========================
// BACK HOME
// =========================
document.getElementById("homeButton").onclick = () => {
    document.getElementById("collectionPage").classList.add("hidden");
    document.getElementById("homePage").classList.remove("hidden");
};

// =========================
// CHIP FILTERS
// =========================
function buildFilters(){

    const cards = allCards.filter(c => c.game === currentGame);

    const rarity = [...new Set(cards.map(c => c.rarity))];
    const sets = [...new Set(cards.map(c => c.set))];

    const rarityDiv = document.getElementById("rarityFilter");
    rarityDiv.innerHTML = createChip("All","rarity","All",true);

    rarity.forEach(r => {
        rarityDiv.innerHTML += createChip(r,"rarity",r,false);
    });

    const setDiv = document.getElementById("setFilter");
    setDiv.innerHTML = createChip("All","set","All",true);

    sets.forEach(s => {
        setDiv.innerHTML += createChip(s,"set",s,false);
    });
}

function createChip(label,type,value,active){
    return `<button class="chip ${active?'active':''}" data-type="${type}" data-value="${value}">
        ${label}
    </button>`;
}

// chip click
document.addEventListener("click", (e) => {
    if(e.target.classList.contains("chip")){
        const type = e.target.dataset.type;
        const value = e.target.dataset.value;

        document.querySelectorAll(`.chip[data-type="${type}"]`)
        .forEach(c => c.classList.remove("active"));

        e.target.classList.add("active");

        updateTable();
    }
});

// =========================
// FILTER INPUTS
// =========================
["searchBox","hideV1","hideV2","hideV3"]
.forEach(id => {
    const el = document.getElementById(id);
    if(el) el.addEventListener("input", updateTable);
});

// =========================
// TABLE
// =========================
function updateTable(){

    let cards = allCards.filter(c => c.game === currentGame);

    const search = document.getElementById("searchBox").value.toLowerCase();

    const rarity = document.querySelector('.chip[data-type="rarity"].active')?.dataset.value || "All";
    const setName = document.querySelector('.chip[data-type="set"].active')?.dataset.value || "All";

    if(search){
        cards = cards.filter(c =>
            c.name.toLowerCase().includes(search) ||
            c.tag.toLowerCase().includes(search)
        );
    }

    if(rarity !== "All")
        cards = cards.filter(c => c.rarity === rarity);

    if(setName !== "All")
        cards = cards.filter(c => c.set === setName);

    if(document.getElementById("hideV1").checked)
        cards = cards.filter(c => !(c.v1max > 0 && c.v1own === c.v1max));

    if(document.getElementById("hideV2").checked)
        cards = cards.filter(c => !(c.v2max > 0 && c.v2own === c.v2max));

    if(document.getElementById("hideV3").checked)
        cards = cards.filter(c => !(c.v3max > 0 && c.v3own === c.v3max));

    let html = `<table>
        <tr>
            <th>Tag</th>
            <th>Name</th>
            <th>Rarity</th>
            <th>V1</th>
            <th>V2</th>
            <th>V3</th>
        </tr>`;

    cards.forEach(c => {
        html += `<tr>
            <td>${c.tag}</td>
            <td>${c.name}</td>
            <td>${c.rarity}</td>
            <td>${safeRatio(c.v1own,c.v1max)}</td>
            <td>${safeRatio(c.v2own,c.v2max)}</td>
            <td>${safeRatio(c.v3own,c.v3max)}</td>
        </tr>`;
    });

    html += "</table>";

    document.getElementById("tableContainer").innerHTML = html;
}

});
