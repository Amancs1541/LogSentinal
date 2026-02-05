console.log("main.js loaded");

let chartInstances = {};

function createOrUpdateChart(chartId, config) {
    const canvas = document.getElementById(chartId);
    if (!canvas) return;

    if (chartInstances[chartId]) {
        chartInstances[chartId].destroy();
    }
    const ctx = canvas.getContext("2d");
    chartInstances[chartId] = new Chart(ctx, config);
}

document.addEventListener("DOMContentLoaded", () => {
    loadDashboard();
    renderLogDetailCharts();
    enableSearch();
    loadGeoLocations();
});


/* -------------------------
   DASHBOARD
------------------------- */
async function loadDashboard() {
    const loginCanvas = document.getElementById("loginChart");
    if (!loginCanvas) return;

    const res = await fetch("/anomalies/api/stats");
    const data = await res.json();

    document.getElementById("totalLogs").innerText = data.total_logs;
    document.getElementById("totalEntries").innerText = data.total_entries;
    document.getElementById("totalAnomalies").innerText = data.total_anomalies;

    createOrUpdateChart("loginChart", {
        type: "line",
        data: {
            labels: data.days,
            datasets: [
                {
                    label: "Success",
                    data: data.success_counts,
                    borderColor: "#2563eb",
                    backgroundColor: "rgba(37,99,235,0.2)",
                    fill: true,
                    tension: 0.3
                },
                {
                    label: "Fail",
                    data: data.fail_counts,
                    borderColor: "#ef4444",
                    backgroundColor: "rgba(239,68,68,0.2)",
                    fill: true,
                    tension: 0.3
                }
            ]
        }
    });

    createOrUpdateChart("ipChart", {
        type: "bar",
        data: {
            labels: data.ips,
            datasets: [{
                label: "Requests",
                data: data.ip_counts,
                backgroundColor: "#60a5fa"
            }]
        }
    });

    renderRecentLogs(data.recent_logs);
}

function renderRecentLogs(logs) {
    const tbody = document.getElementById("recentLogsTable");
    if (!tbody) return;

    tbody.innerHTML = "";
    logs.forEach(log => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${log.filename}</td>
            <td>${log.uploaded_at}</td>
            <td>${log.entries}</td>
            <td>
                <a href="/logs/${log.id}" class="btn btn-sm btn-primary">View</a>

                <form action="/logs/delete/${log.id}" method="post" style="display:inline;">
                    <button class="btn btn-sm btn-danger"
                        onclick="return confirm('Are you sure you want to delete this log?')">
                        Delete
                    </button>
                </form>
            </td>
        `;
        tbody.appendChild(tr);
    });
}



/* -------------------------
   LOG DETAIL CHARTS
------------------------- */
function renderLogDetailCharts() {
    if (typeof sfData === "undefined") return;

    createOrUpdateChart("sfChart", {
        type: "doughnut",
        data: {
            labels: ["Success", "Fail"],
            datasets: [{
                data: [sfData.success, sfData.fail],
                backgroundColor: ["#22c55e", "#ef4444"]
            }]
        }
    });

    createOrUpdateChart("logIpChart", {
        type: "bar",
        data: {
            labels: ipLabels,
            datasets: [{
                label: "Events",
                data: ipCounts,
                backgroundColor: "#3b82f6"
            }]
        }
    });
}


/* -------------------------
   SEARCH / FILTER
------------------------- */
function enableSearch() {
    const box = document.getElementById("searchBox");
    if (!box) return;

    box.addEventListener("input", async () => {
        const q = box.value;
        const res = await fetch(`/logs/search/${logId}?q=${q}`);
        const data = await res.json();

        const tbody = document.getElementById("entriesTable");
        tbody.innerHTML = "";

        data.forEach(e => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${e.timestamp}</td>
                <td>${e.user}</td>
                <td>${e.ip}</td>
                <td class="geo" data-ip="${e.ip}">Loading...</td>
                <td>${e.status}</td>
                <td>${e.raw}</td>
            `;
            tbody.appendChild(tr);
        });

        loadGeoLocations();
    });
}


/* -------------------------
   IP GEOLOCATION
------------------------- */
async function loadGeoLocations() {
    const cells = document.querySelectorAll(".geo");

    cells.forEach(async cell => {
        const ip = cell.dataset.ip;
        if (!ip) return;

        try {
            const res = await fetch(`/api/geo/${ip}`);
            const data = await res.json();

            if (data.country === "Private Network") {
                cell.innerText = "Private Network";
            } else if (data.country) {
                cell.innerText = `${data.city || ""}, ${data.country}`;
            } else {
                cell.innerText = "Unknown";
            }
        } catch {
            cell.innerText = "Error";
        }
    });
}
