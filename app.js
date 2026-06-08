document.addEventListener("DOMContentLoaded", () => {

let allCards = [];
let currentGame = "";

fetch("https://catusdc.github.io/tcg_vault/collection.json")
.then(r => r.json())
.then(data => {

    allCards = data.cards;
    buildHome();

});

function buildHome(){
    const container = document.getElementById("gameCards");
    container.innerHTML = "";

    const games = [...new Set(allCards.map(c => c.game))];

    games.forEach(game => {

        const cards = allCards.filter(c => c.game === game);

        let own = 0;
        let max = 0;

        cards.forEach(c => {
            own += c.v1own + c.v2own + c.v3own;
            max += c.v1max + c.v2max + c.v3max;
        });

        const percent = max ? (100 * own / max).toFixed(2) : 0;

        container.innerHTML += `
        <div class="gameCard">
            <h3>${game}</h3>

            <div class="progressBar">
                <div class="progressFill" style="width:${percent}%"></div>
            </div>

            <p>${percent}%</p>

            <button onclick="openGame('${game}')">Apri</button>
        </div>`;
    });
}

window.openGame = function(game){
    currentGame = game;

    document.getElementById("homePage").classList.add("hidden");
    document.getElementById("collectionPage").classList.remove("hidden");

    document.getElementById("gameTitle").innerText = game;

    buildFilters();
    updateTable();
};

document.getElementById("homeButton").onclick = () => {
    document.getElementById("collectionPage").classList.add("hidden");
    document.getElementById("homePage").classList.remove("hidden");
};

function buildFilters(){
    const cards = allCards.filter(c => c.game === currentGame);

    const rarity = [...new Set(cards.map(c => c.rarity))];
    const sets = [...new Set(cards.map(c => c.set))];

    const raritySelect = document.getElementById("rarityFilter");
    raritySelect.innerHTML = `<option value="All">All</option>`;
    rarity.forEach(r => raritySelect.innerHTML += `<option>${r}</option>`);

    const setSelect = document.getElementById("setFilter");
    setSelect.innerHTML = `<option value="All">All</option>`;
    sets.forEach(s => setSelect.innerHTML += `<option>${s}</option>`);
}

["searchBox","rarityFilter","setFilter","hideV1","hideV2","hideV3"]
.forEach(id => {
    const el = document.getElementById(id);
    if (el) el.addEventListener("input", updateTable);
});

function updateTable(){

    let cards = allCards.filter(c => c.game === currentGame);

    const search = document.getElementById("searchBox").value.toLowerCase();
    const rarity = document.getElementById("rarityFilter").value;
    const setName = document.getElementById("setFilter").value;

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
            <th>Tag</th><th>Name</th><th>Rarity</th><th>V1</th><th>V2</th><th>V3</th>
        </tr>`;

    cards.forEach(c => {
        html += `<tr>
            <td>${c.tag}</td>
            <td>${c.name}</td>
            <td>${c.rarity}</td>
            <td>${c.v1own} / ${c.v1max}</td>
            <td>${c.v2own} / ${c.v2max}</td>
            <td>${c.v3own} / ${c.v3max}</td>
        </tr>`;
    });

    html += "</table>";

    document.getElementById("tableContainer").innerHTML = html;
}

});
