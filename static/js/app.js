/**
 * CIVIC-PREDICT AI — Main JavaScript Application
 * Interactive Dashboard for Civic Issue Risk Prediction
 *
 * Features:
 *   1. Sidebar toggle (mobile responsive)
 *   2. Chart.js chart initialization (blue-first palette)
 *   3. Leaflet.js risk map with color-coded circle markers
 *   4. AI chat interface (POST /api/ai-chat)
 *   5. Table sorting & filtering
 *   6. Toast notifications
 *   7. Live clock in top bar
 *   8. KPI counter animation
 *
 * Vanilla JS — no jQuery required.
 */

'use strict';

/* ============================================================
   COLOR CONSTANTS
   ============================================================ */
var COLORS = {
    primary:   '#1769E0',
    light:     '#2F80ED',
    sky:       '#60A5FA',
    pale:      '#93C5FD',
    critical:  '#DC2626',
    high:      '#EA580C',
    medium:    '#D97706',
    low:       '#16A34A',
    bg:        '#f0f2f5',
    surface:   '#ffffff',
    text:      '#1a1a2e',
    muted:     '#64748b',
    border:    '#e2e8f0'
};

var RISK_COLORS = [COLORS.critical, COLORS.high, COLORS.medium, COLORS.low];

/* ============================================================
   1. SIDEBAR TOGGLE
   ============================================================ */
function toggleSidebar() {
    var sidebar = document.getElementById('sidebar');
    var overlay = document.getElementById('sidebarOverlay');
    if (!sidebar) return;

    sidebar.classList.toggle('open');
    if (overlay) overlay.classList.toggle('active');
    document.body.classList.toggle('sidebar-open');
}

function closeSidebar() {
    var sidebar = document.getElementById('sidebar');
    var overlay = document.getElementById('sidebarOverlay');
    if (sidebar) sidebar.classList.remove('open');
    if (overlay) overlay.classList.remove('active');
    document.body.classList.remove('sidebar-open');
}

// Close sidebar on Escape key
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeSidebar();
});

/* ============================================================
   2. CHART.JS INITIALIZATION
   ============================================================ */
var CIVIC_CHARTS = {};

/**
 * Set global Chart.js defaults for the blue-first design system
 */
function initChartDefaults() {
    if (typeof Chart === 'undefined') return;

    Chart.defaults.color = COLORS.muted;
    Chart.defaults.borderColor = 'rgba(0,0,0,0.05)';
    Chart.defaults.font.family = "'Inter', 'Segoe UI', sans-serif";
    Chart.defaults.font.size = 12;
    Chart.defaults.plugins.legend.labels.usePointStyle = true;
    Chart.defaults.plugins.legend.labels.padding = 14;
    Chart.defaults.plugins.tooltip.backgroundColor = '#1e293b';
    Chart.defaults.plugins.tooltip.titleColor = '#f8fafc';
    Chart.defaults.plugins.tooltip.bodyColor = '#cbd5e1';
    Chart.defaults.plugins.tooltip.padding = 10;
    Chart.defaults.plugins.tooltip.cornerRadius = 8;
    Chart.defaults.plugins.tooltip.borderColor = '#334155';
    Chart.defaults.plugins.tooltip.borderWidth = 1;
}

/**
 * Destroy a chart instance by canvas ID if it exists
 */
function destroyChart(canvasId) {
    if (CIVIC_CHARTS[canvasId]) {
        CIVIC_CHARTS[canvasId].destroy();
        delete CIVIC_CHARTS[canvasId];
    }
}

/**
 * Initialize a Category Pie chart
 */
function initCategoryPieChart(canvasId, labels, data) {
    destroyChart(canvasId);
    var ctx = document.getElementById(canvasId);
    if (!ctx) return;

    var palette = [COLORS.primary, COLORS.light, COLORS.sky, COLORS.critical, COLORS.high, COLORS.medium, COLORS.low, '#8b5cf6', '#06b6d4', '#14b8a6'];

    CIVIC_CHARTS[canvasId] = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: palette.slice(0, labels.length),
                borderWidth: 0,
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'right', labels: { font: { family: "'Inter', sans-serif" } } }
            }
        }
    });
}

/**
 * Initialize a Department horizontal bar chart
 */
function initDepartmentBarChart(canvasId, labels, data) {
    destroyChart(canvasId);
    var ctx = document.getElementById(canvasId);
    if (!ctx) return;

    var palette = [COLORS.primary, COLORS.high, COLORS.low, '#8b5cf6'];

    CIVIC_CHARTS[canvasId] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Issues',
                data: data,
                backgroundColor: palette.slice(0, labels.length),
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: { legend: { display: false } },
            scales: {
                x: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.05)' } },
                y: { grid: { display: false } }
            }
        }
    });
}

/**
 * Initialize a City doughnut chart
 */
function initCityDoughnutChart(canvasId, labels, data) {
    destroyChart(canvasId);
    var ctx = document.getElementById(canvasId);
    if (!ctx) return;

    var palette = [COLORS.primary, COLORS.critical, COLORS.sky, COLORS.medium, '#8b5cf6'];

    CIVIC_CHARTS[canvasId] = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: palette.slice(0, labels.length),
                borderWidth: 0,
                hoverOffset: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '65%',
            plugins: { legend: { position: 'right' } }
        }
    });
}

/**
 * Initialize a Monthly Trend line chart
 */
function initMonthlyTrendChart(canvasId, labels, datasets) {
    destroyChart(canvasId);
    var ctx = document.getElementById(canvasId);
    if (!ctx) return;

    var styledDatasets = datasets.map(function(ds, i) {
        return {
            label: ds.label || ('Series ' + (i + 1)),
            data: ds.data,
            borderColor: ds.borderColor || COLORS.primary,
            backgroundColor: ds.backgroundColor || 'rgba(23,105,224,0.1)',
            fill: ds.fill !== undefined ? ds.fill : true,
            tension: 0.4,
            pointRadius: 4,
            pointHoverRadius: 6,
            borderWidth: 2.5
        };
    });

    CIVIC_CHARTS[canvasId] = new Chart(ctx, {
        type: 'line',
        data: { labels: labels, datasets: styledDatasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: { mode: 'index', intersect: false },
            plugins: { legend: { position: 'top' } },
            scales: {
                y: { beginAtZero: true, grid: { color: 'rgba(0,0,0,0.05)' } },
                x: { grid: { display: false } }
            }
        }
    });
}

/**
 * Initialize a Status doughnut chart
 */
function initStatusChart(canvasId, labels, data) {
    destroyChart(canvasId);
    var ctx = document.getElementById(canvasId);
    if (!ctx) return;

    CIVIC_CHARTS[canvasId] = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [COLORS.critical, COLORS.high, COLORS.low, COLORS.primary],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '60%',
            plugins: { legend: { position: 'bottom' } }
        }
    });
}

/**
 * Initialize a Severity doughnut chart
 */
function initSeverityChart(canvasId, data) {
    destroyChart(canvasId);
    var ctx = document.getElementById(canvasId);
    if (!ctx) return;

    CIVIC_CHARTS[canvasId] = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Critical', 'High', 'Medium', 'Low'],
            datasets: [{
                data: data,
                backgroundColor: RISK_COLORS,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            cutout: '60%',
            plugins: { legend: { position: 'bottom' } }
        }
    });
}

/**
 * Initialize a Resolution Rate line chart
 */
function initResolutionChart(canvasId, labels, data) {
    destroyChart(canvasId);
    var ctx = document.getElementById(canvasId);
    if (!ctx) return;

    CIVIC_CHARTS[canvasId] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Resolution Rate %',
                data: data,
                borderColor: COLORS.low,
                backgroundColor: 'rgba(22,163,74,0.2)',
                fill: true,
                tension: 0.4,
                borderWidth: 2.5,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { min: 0, max: 100, grid: { color: 'rgba(0,0,0,0.05)' } },
                x: { grid: { display: false } }
            }
        }
    });
}

/* ============================================================
   3. LEAFLET MAP
   ============================================================ */
var civicMap = null;
var civicMarkerLayer = null;

var MAP_DEFAULTS = {
    center: [-6.23, 106.90], // Greater Jakarta
    zoom: 11
};

/**
 * Get a color for a given risk severity
 */
function riskColor(severity) {
    var s = (severity || '').toLowerCase();
    if (s === 'critical') return COLORS.critical;
    if (s === 'high') return COLORS.high;
    if (s === 'medium') return COLORS.medium;
    return COLORS.low;
}

/**
 * Get severity label from risk score
 */
function severityFromScore(score) {
    if (score >= 75) return 'critical';
    if (score >= 50) return 'high';
    if (score >= 25) return 'medium';
    return 'low';
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(str) {
    if (!str) return '';
    var div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

/**
 * Build popup HTML for a map marker
 */
function buildPopup(issue) {
    var severity = issue.severity || severityFromScore(issue.risk_score);
    var color = riskColor(severity);
    var label = severity.toUpperCase();

    return '<div style="min-width:220px;font-family:Inter,sans-serif;">' +
        '<div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;">' +
            '<span style="width:10px;height:10px;border-radius:50%;background:' + color + ';display:inline-block;"></span>' +
            '<strong style="font-size:14px;">' + escapeHtml(issue.title) + '</strong>' +
        '</div>' +
        '<div style="font-size:12px;color:#64748b;margin-bottom:4px;">' +
            '<b>Risk Score:</b> ' + issue.risk_score + '/100 &mdash; <span style="color:' + color + ';">' + label + '</span>' +
        '</div>' +
        '<div style="font-size:12px;color:#64748b;margin-bottom:4px;">' +
            '<b>Category:</b> ' + escapeHtml(issue.category || '—') +
        '</div>' +
        '<div style="font-size:12px;color:#64748b;margin-bottom:4px;">' +
            '<b>Location:</b> ' + escapeHtml(issue.location_name || issue.city || '—') +
        '</div>' +
        '<div style="font-size:12px;color:#64748b;margin-bottom:8px;">' +
            '<b>Status:</b> ' + escapeHtml(issue.status || '—') +
        '</div>' +
        '<a href="/issues/' + issue.id + '" style="' +
            'display:inline-block;padding:5px 12px;' +
            'background:#1769E0;color:#fff;border-radius:6px;' +
            'font-size:12px;text-decoration:none;' +
        '">View Details &rarr;</a>' +
    '</div>';
}

/**
 * Initialize a Leaflet risk map
 * @param {string} containerId — DOM element ID for the map
 * @param {Array} issues — [{ id, title, lat, lng, risk_score, severity, category, location_name, city, status }]
 */
function initRiskMap(containerId, issues) {
    if (typeof L === 'undefined') {
        console.warn('CIVIC: Leaflet.js not loaded. Skipping map init.');
        return null;
    }

    var container = document.getElementById(containerId);
    if (!container) return null;

    // Destroy existing map
    if (civicMap) {
        civicMap.remove();
        civicMap = null;
    }

    civicMap = L.map(containerId, {
        center: MAP_DEFAULTS.center,
        zoom: MAP_DEFAULTS.zoom,
        zoomControl: true,
        scrollWheelZoom: true
    });

    // OpenStreetMap tiles are free and do not require a Carto API key.
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19,
        subdomains: ['a', 'b', 'c']
    }).addTo(civicMap);

    civicMarkerLayer = L.layerGroup().addTo(civicMap);

    // Add circle markers
    issues.forEach(function(issue) {
        if (issue.lat == null || issue.lng == null) return;

        var severity = issue.severity || severityFromScore(issue.risk_score);
        var color = riskColor(severity);
        var radius = Math.max(6, Math.min(20, issue.risk_score / 4));

        var marker = L.circleMarker([issue.lat, issue.lng], {
            radius: radius,
            fillColor: color,
            color: '#ffffff',
            weight: 2,
            opacity: 1,
            fillOpacity: 0.85
        }).bindPopup(buildPopup(issue), { maxWidth: 280 });

        marker.addTo(civicMarkerLayer);
    });

    // Fit bounds if markers exist
    var coords = issues
        .filter(function(i) { return i.lat != null && i.lng != null; })
        .map(function(i) { return [i.lat, i.lng]; });
    if (coords.length > 0) {
        civicMap.fitBounds(coords, { padding: [40, 40] });
    }

    return civicMap;
}

/* ============================================================
   4. AI CHAT
   ============================================================ */
function sendMessage() {
    var input = document.getElementById('aiInput');
    if (!input) return;

    var msg = input.value.trim();
    if (!msg) return;

    var container = document.getElementById('chatContainer');
    var suggestions = document.getElementById('aiSuggestions');
    if (!container) return;

    // Hide suggestions after first message
    if (suggestions) suggestions.style.display = 'none';

    // Add user message
    var userDiv = document.createElement('div');
    userDiv.className = 'chat-msg user';
    userDiv.innerHTML =
        '<div class="chat-bubble user">' +
            '<p>' + escapeHtml(msg) + '</p>' +
        '</div>' +
        '<div class="chat-avatar user">' +
            '<i class="fas fa-user"></i>' +
        '</div>';
    container.appendChild(userDiv);

    input.value = '';

    // Typing indicator
    var typingId = 'typing-' + Date.now();
    var typingDiv = document.createElement('div');
    typingDiv.className = 'chat-msg ai';
    typingDiv.id = typingId;
    typingDiv.innerHTML =
        '<div class="chat-avatar ai"><i class="fas fa-brain"></i></div>' +
        '<div class="chat-bubble ai" style="padding:12px 16px;">' +
            '<span class="typing-dot"></span>' +
            '<span class="typing-dot"></span>' +
            '<span class="typing-dot"></span>' +
        '</div>';
    container.appendChild(typingDiv);
    container.scrollTop = container.scrollHeight;

    // POST to API
    fetch('/api/ai-chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: msg })
    })
    .then(function(r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
    })
    .then(function(data) {
        var typingNode = document.getElementById(typingId);
        if (typingNode) typingNode.remove();

        var aiDiv = document.createElement('div');
        aiDiv.className = 'chat-msg ai';
        aiDiv.innerHTML =
            '<div class="chat-avatar ai"><i class="fas fa-brain"></i></div>' +
            '<div class="chat-bubble ai">' +
                '<p>' + (data.response || 'I could not generate a response.') + '</p>' +
            '</div>';
        container.appendChild(aiDiv);
        container.scrollTop = container.scrollHeight;
    })
    .catch(function() {
        var typingNode = document.getElementById(typingId);
        if (typingNode) typingNode.remove();

        var errDiv = document.createElement('div');
        errDiv.className = 'chat-msg ai';
        errDiv.innerHTML =
            '<div class="chat-avatar ai"><i class="fas fa-brain"></i></div>' +
            '<div class="chat-bubble ai">' +
                '<p>I apologize, but I encountered an error processing your request. Please try again.</p>' +
            '</div>';
        container.appendChild(errDiv);
        container.scrollTop = container.scrollHeight;
    });
}

function askQuestion(q) {
    var input = document.getElementById('aiInput');
    if (input) {
        input.value = q;
        sendMessage();
    }
}

/* ============================================================
   5. TABLE FEATURES
   ============================================================ */

/**
 * Filter table rows by search query
 * @param {string} tableId — the table element's ID
 */
function filterTable(tableId) {
    var input = document.getElementById(tableId + '-search');
    var table = document.getElementById(tableId);
    if (!input || !table) return;

    var query = input.value.toLowerCase();
    var tbody = table.querySelector('tbody');
    if (!tbody) return;

    var rows = tbody.querySelectorAll('tr');
    rows.forEach(function(row) {
        var text = row.textContent.toLowerCase();
        row.style.display = text.indexOf(query) !== -1 ? '' : 'none';
    });
}

/**
 * Sort table by column index
 * @param {string} tableId — the table element's ID
 * @param {number} colIndex — column index to sort by
 */
function sortTable(tableId, colIndex) {
    var table = document.getElementById(tableId);
    if (!table) return;

    var tbody = table.querySelector('tbody');
    if (!tbody) return;

    var rows = Array.from(tbody.querySelectorAll('tr'));
    var th = table.querySelectorAll('thead th')[colIndex];
    if (!th) return;

    // Toggle direction
    var asc = th.getAttribute('data-sort') !== 'asc';
    th.setAttribute('data-sort', asc ? 'asc' : 'desc');

    rows.sort(function(a, b) {
        var aVal = (a.children[colIndex] ? a.children[colIndex].textContent.trim() : '').toLowerCase();
        var bVal = (b.children[colIndex] ? b.children[colIndex].textContent.trim() : '').toLowerCase();

        // Try numeric sort
        var aNum = parseFloat(aVal.replace(/[^\d.\-]/g, ''));
        var bNum = parseFloat(bVal.replace(/[^\d.\-]/g, ''));
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return asc ? aNum - bNum : bNum - aNum;
        }

        return asc ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
    });

    rows.forEach(function(row) { tbody.appendChild(row); });

    // Update sort indicators
    var allTh = table.querySelectorAll('thead th');
    allTh.forEach(function(h) { h.classList.remove('sort-asc', 'sort-desc'); });
    th.classList.add(asc ? 'sort-asc' : 'sort-desc');
}

/* ============================================================
   6. TOAST NOTIFICATIONS
   ============================================================ */
function showToast(message, type) {
    type = type || 'info';

    // Ensure container exists
    var container = document.getElementById('toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'toast-container';
        container.setAttribute('aria-live', 'polite');
        container.style.cssText = 'position:fixed;top:24px;right:24px;z-index:10000;display:flex;flex-direction:column;gap:10px;';
        document.body.appendChild(container);
    }

    var icons = { success: 'fa-check-circle', error: 'fa-times-circle', warning: 'fa-exclamation-triangle', info: 'fa-info-circle' };
    var bgColors = { success: COLORS.low, error: COLORS.critical, warning: COLORS.medium, info: COLORS.primary };

    var toast = document.createElement('div');
    toast.style.cssText =
        'display:flex;align-items:center;gap:10px;padding:14px 20px;' +
        'background:' + (bgColors[type] || bgColors.info) + ';' +
        'color:#fff;border-radius:10px;box-shadow:0 4px 24px rgba(0,0,0,0.15);' +
        'font-size:0.875rem;font-family:Inter,sans-serif;min-width:280px;' +
        'opacity:0;transform:translateX(100%);transition:all 0.3s ease;';

    toast.innerHTML =
        '<i class="fas ' + (icons[type] || icons.info) + '" style="font-size:1.1rem;"></i>' +
        '<span style="flex:1;">' + message + '</span>' +
        '<button style="background:none;border:none;color:#fff;cursor:pointer;font-size:1.2rem;padding:0;line-height:1;" onclick="this.parentElement.remove()">&times;</button>';

    container.appendChild(toast);

    // Trigger animation
    requestAnimationFrame(function() {
        toast.style.opacity = '1';
        toast.style.transform = 'translateX(0)';
    });

    // Auto-dismiss after 3 seconds
    setTimeout(function() {
        toast.style.opacity = '0';
        toast.style.transform = 'translateX(100%)';
        setTimeout(function() { if (toast.parentNode) toast.remove(); }, 300);
    }, 3000);
}

/* ============================================================
   7. TIME DISPLAY
   ============================================================ */
function updateClock() {
    var el = document.getElementById('currentTime');
    if (!el) return;

    var now = new Date();
    var hours = now.getHours().toString().padStart(2, '0');
    var minutes = now.getMinutes().toString().padStart(2, '0');
    var seconds = now.getSeconds().toString().padStart(2, '0');
    el.textContent = hours + ':' + minutes + ':' + seconds;
}

/* ============================================================
   8. COUNTER ANIMATION
   ============================================================ */
function animateCounters() {
    var counters = document.querySelectorAll('.kpi-value[data-target]');
    if (!counters.length) return;

    var observer = new IntersectionObserver(function(entries) {
        entries.forEach(function(entry) {
            if (entry.isIntersecting) {
                var el = entry.target;
                var target = parseFloat(el.getAttribute('data-target'));
                if (isNaN(target)) return;

                var isFloat = String(target).indexOf('.') !== -1;
                var duration = 1200;
                var start = performance.now();
                var initialText = el.textContent.trim();
                var prefix = (initialText.match(/^[^\d]*/) || [''])[0];
                var suffix = (initialText.match(/[^\d]*$/) || [''])[0];

                function step(now) {
                    var elapsed = now - start;
                    var progress = Math.min(elapsed / duration, 1);
                    var ease = 1 - Math.pow(1 - progress, 3);
                    var current = target * ease;

                    el.textContent = prefix + (isFloat ? current.toFixed(1) : Math.floor(current).toLocaleString()) + suffix;

                    if (progress < 1) {
                        requestAnimationFrame(step);
                    }
                }

                requestAnimationFrame(step);
                observer.unobserve(el);
            }
        });
    }, { threshold: 0.5 });

    counters.forEach(function(el) { observer.observe(el); });
}

/* ============================================================
   INITIALIZATION
   ============================================================ */
document.addEventListener('DOMContentLoaded', function() {
    // Initialize Chart.js defaults
    initChartDefaults();

    // Start the clock
    updateClock();
    setInterval(updateClock, 1000);

    // Animate KPI counters
    animateCounters();

    // Log successful load
    console.log('%c CIVIC-PREDICT AI %c Loaded successfully ',
        'background:#1769E0;color:#fff;padding:4px 8px;border-radius:4px 0 0 4px;font-weight:bold;',
        'background:#1e293b;color:#94a3b8;padding:4px 8px;border-radius:0 4px 4px 0;'
    );
});
