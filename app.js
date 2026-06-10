document.addEventListener("DOMContentLoaded", () => {

let allCards = [];
let currentGame = "";

// =========================
// LOAD JSON
// =========================
fetch("./collection.json")
.then(r => r.json())
.then(data => {
    allCards = data.cards || [];
    buildHome();
});

// =========================
// HOME
// =========================
function buildHome(){

    const container = document.getElementById("gameCards");
    container.innerHTML = "";

    const games = [...new Set(allCards.map(c => c.game))];

    games.forEach(game => {

        const cards = allCards.filter(c => c.game === game);

        let v1o=0,v1m=0,v2o=0,v2m=0,v3o=0,v3m=0;

        cards.forEach(c => {
            v1o += c.v1own; v1m += c.v1max;
            v2o += c.v2own; v2m += c.v2max;
            v3o += c.v3own; v3m += c.v3max;
        });

        const p1 = percent(v1o,v1m);
        const p2 = percent(v2o,v2m);
        const p3 = percent(v3o,v3m);

        container.innerHTML += `
        <div class="gameCard">
            <h3>${game}</h3>

            <div class="progressBlock">
                <div>V1: ${p1}</div>
                <div>V2: ${p2}</div>
                <div>V3: ${p3}</div>
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
// HOME BUTTON
// =========================
document.getElementById("homeButton").onclick = () => {
    document.getElementById("collectionPage").classList.add("hidden");
    document.getElementById("homePage").classList.remove("hidden");
};

// =========================
// FILTERS
// =========================
function buildFilters(){

    const cards = allCards.filter(c => c.game === currentGame);

    const rarity = [...new Set(cards.map(c => c.rarity))];
    const sets = [...new Set(cards.map(c => c.set))];

    const rarityDiv = document.getElementById("rarityFilter");
    const setDiv = document.getElementById("setFilter");

    rarityDiv.innerHTML = "";
    setDiv.innerHTML = "";

    rarityDiv.appendChild(makeChip("All","rarity","All",true));
    rarity.forEach(r => rarityDiv.appendChild(makeChip(r,"rarity",r,false)));

    setDiv.appendChild(makeChip("All","set","All",true));
    sets.forEach(s => setDiv.appendChild(makeChip(s,"set",s,false)));
}

// =========================
// CHIP FACTORY
// =========================
function makeChip(label,type,value,active){

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

// =========================
// INPUT EVENTS
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
    const set = document.querySelector('.chip[data-type="set"].active')?.dataset.value || "All";

    if(search){
        cards = cards.filter(c =>
            c.name.toLowerCase().includes(search) ||
            c.tag.toLowerCase().includes(search)
        );
    }

    if(rarity !== "All")
        cards = cards.filter(c => c.rarity === rarity);

    if(set !== "All")
        cards = cards.filter(c => c.set === set);

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
        html += `
        <tr>
            <td>${c.tag}</td>
            <td>${c.name}</td>
            <td>${c.rarity}</td>
            <td>${ratio(c.v1own,c.v1max)}</td>
            <td>${ratio(c.v2own,c.v2max)}</td>
            <td>${ratio(c.v3own,c.v3max)}</td>
        </tr>`;
    });

    html += "</table>";

    document.getElementById("tableContainer").innerHTML = html;
}

// =========================
// HELPERS
// =========================
function percent(o,m){
    if(!m || m===0) return "N/A";
    return ((o/m)*100).toFixed(2) + "%";
}

function ratio(o,m){
    if(!m || m===0) return "N/A";
    return `${o} / ${m}`;
}

});
