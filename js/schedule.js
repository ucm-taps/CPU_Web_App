const weekdays = ["sunday", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday"];
const weekdayNames = weekdays.map(day => day[0].toUpperCase() + day.slice(1));

function parseCsv(text) {
    const rows = [];
    let row = [];
    let field = "";
    let quoted = false;

    for (let index = 0; index < text.length; index += 1) {
        const character = text[index];

        if (quoted) {
            if (character === '"' && text[index + 1] === '"') {
                field += '"';
                index += 1;
            } else if (character === '"') {
                quoted = false;
            } else {
                field += character;
            }
        } else if (character === '"') {
            quoted = true;
        } else if (character === ",") {
            row.push(field);
            field = "";
        } else if (character === "\n" || character === "\r") {
            if (character === "\r" && text[index + 1] === "\n") index += 1;
            row.push(field);
            rows.push(row);
            row = [];
            field = "";
        } else {
            field += character;
        }
    }

    if (field || row.length) {
        row.push(field);
        rows.push(row);
    }

    return rows;
}

function getScheduleItems(rows, day) {
    const dayName = day[0].toUpperCase() + day.slice(1);
    let headers = null;
    let timeColumn = -1;
    const items = [];

    rows.forEach(row => {
        const dayHeaderIndex = row.findIndex(value => value.trim().toLowerCase() === day);
        const isSectionHeader = row.some(value => value.trim().toLowerCase() === "participant") &&
            row.some(value => weekdays.includes(value.trim().toLowerCase()));
        if (isSectionHeader) {
            headers = dayHeaderIndex === -1 ? null : row.map(value => value.trim());
            timeColumn = dayHeaderIndex;
            return;
        }

        if (!headers || !row.some(value => value.trim())) return;

        const item = {};
        headers.forEach((header, index) => {
            if (header) item[header.toLowerCase()] = (row[index] || "").trim();
        });
        item.time = (row[timeColumn] || "").trim();

        if (Object.values(item).some(value => value)) {
            items.push(item);
        }
    });

    return { dayName, items };
}

function addDetail(card, label, value) {
    if (!value) return;

    const detail = document.createElement("p");
    const name = document.createElement("strong");
    name.textContent = `${label}: `;
    detail.append(name, document.createTextNode(value));
    card.appendChild(detail);
}

function renderItems(container, items, dayName) {
    container.replaceChildren();

    if (items.length === 0) {
        const emptyState = document.createElement("p");
        emptyState.className = "empty-state";
        emptyState.textContent = `No schedule entries for ${dayName}.`;
        container.appendChild(emptyState);
        return;
    }

    items.forEach(item => {
        const card = document.createElement("article");
        card.className = "schedule-item";

        const heading = document.createElement("h2");
        heading.textContent = item.time || "Scheduled item";
        card.appendChild(heading);

        addDetail(card, "Participant", item.participant);
        addDetail(card, "Status", item.status);
        addDetail(card, "TAPS Ambassador", item["taps ambassador"]);

        const route = [item.pickup, item.dropoff].filter(Boolean).join(" to ");
        addDetail(card, "Route", route);
        addDetail(card, "Comments", item.comments);

        container.appendChild(card);
    });
}

async function loadSchedule() {
    const params = new URLSearchParams(window.location.search);
    const fixedDay = document.body.dataset.day;
    const requestedDay = params.get("day")?.toLowerCase();
    const currentDay = weekdays[new Date().getDay()];
    const day = fixedDay || (weekdays.includes(requestedDay) ? requestedDay : currentDay);
    const dayName = weekdayNames[weekdays.indexOf(day)];
    const title = document.getElementById("schedule-title");
    const note = document.getElementById("schedule-note");
    const container = document.getElementById("schedule-items");

    title.textContent = `${dayName} Schedule`;
    if (!requestedDay && !fixedDay) {
        note.textContent = new Date().toLocaleDateString(undefined, {
            weekday: "long",
            year: "numeric",
            month: "long",
            day: "numeric"
        });
    } else {
        note.textContent = `Showing schedule items for ${dayName}.`;
    }

    document.querySelectorAll("[data-day-link]").forEach(link => {
        if (link.dataset.dayLink === day) {
            link.setAttribute("aria-current", "page");
        }
    });

    try {
        const response = await fetch("../data/cpu_agenda.csv");
        if (!response.ok) {
            throw new Error(`Could not load schedule data (${response.status}).`);
        }

        const rows = parseCsv((await response.text()).replace(/^\uFEFF/, ""));
        const schedule = getScheduleItems(rows, day);
        renderItems(container, schedule.items, schedule.dayName);
    } catch (error) {
        console.error("Schedule loading failed:", error);
        note.textContent = "The schedule could not be loaded. Please try again later.";
    }
}

loadSchedule();
