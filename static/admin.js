// Admin Dashboard JavaScript

// Login form handler
document.getElementById("login-form").onsubmit = async (e) => {
    e.preventDefault();
    const form = new FormData(e.target);
    const res = await fetch('/admin/login', { method: 'POST', body: form });
    if (res.redirected) {
        window.location = res.url;
    } else {
        loadDashboard();
    }
};

// Tab switching
document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        // Remove active from all tabs
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

        // Add active to clicked tab
        btn.classList.add('active');
        document.getElementById(btn.dataset.tab).classList.add('active');

        // Load data for the tab
        const tab = btn.dataset.tab;
        if (tab === 'categories') loadCategories();
        if (tab === 'officers') loadOfficers();
        if (tab === 'ads') loadAds();
    });
});

// Rebuild AI Index
async function rebuildIndex() {
    const btn = document.getElementById('rebuildIndexBtn');
    btn.disabled = true;
    btn.textContent = '🔄 Building...';

    try {
        const res = await fetch('/api/admin/build_index', { method: 'POST' });
        const data = await res.json();
        alert(`AI Index rebuilt successfully!\n\nIndexed: ${data.count} documents\nFAISS Available: ${data.faiss ? 'Yes' : 'No (using fallback)'}`);
    } catch (err) {
        alert('Error rebuilding index: ' + err.message);
    }

    btn.disabled = false;
    btn.textContent = '🔄 Rebuild AI Index';
}

// Load Dashboard
async function loadDashboard() {
    const dashEl = document.getElementById("dashboard");
    try {
        const r = await fetch('/api/admin/insights');
        if (r.status === 401) {
            document.getElementById("login-box").style.display = "block";
            dashEl.style.display = "none";
            return;
        }
        const data = await r.json();
        document.getElementById("login-box").style.display = "none";
        dashEl.style.display = "block";

        // Age Distribution Chart
        new Chart(document.getElementById("ageChart"), {
            type: 'bar',
            data: {
                labels: Object.keys(data.age_groups),
                datasets: [{
                    label: "Users by Age",
                    data: Object.values(data.age_groups),
                    backgroundColor: 'rgba(59, 130, 246, 0.7)',
                    borderColor: 'rgba(59, 130, 246, 1)',
                    borderWidth: 2
                }]
            },
            options: { responsive: true, plugins: { legend: { display: false } } }
        });

        // Jobs Chart
        new Chart(document.getElementById("jobChart"), {
            type: 'pie',
            data: {
                labels: Object.keys(data.jobs).slice(0, 8),
                datasets: [{
                    label: "Jobs",
                    data: Object.values(data.jobs).slice(0, 8),
                    backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16']
                }]
            },
            options: { responsive: true }
        });

        // Services Chart
        new Chart(document.getElementById("serviceChart"), {
            type: 'doughnut',
            data: {
                labels: Object.keys(data.services).slice(0, 10),
                datasets: [{
                    label: "Services",
                    data: Object.values(data.services).slice(0, 10),
                    backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#06b6d4', '#84cc16', '#f97316', '#14b8a6']
                }]
            },
            options: { responsive: true }
        });

        // Questions Chart
        new Chart(document.getElementById("questionChart"), {
            type: 'bar',
            data: {
                labels: Object.keys(data.questions).slice(0, 10).map(q => q.substring(0, 40) + '...'),
                datasets: [{
                    label: "Top Questions",
                    data: Object.values(data.questions).slice(0, 10),
                    backgroundColor: 'rgba(16, 185, 129, 0.7)',
                    borderColor: 'rgba(16, 185, 129, 1)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                plugins: { legend: { display: false } },
                scales: {
                    x: {
                        ticks: {
                            maxRotation: 45,
                            minRotation: 45
                        }
                    }
                }
            }
        });

        // Premium suggestions
        const pl = document.getElementById("premiumList");
        if (data.premium_suggestions && data.premium_suggestions.length) {
            pl.innerHTML = data.premium_suggestions.map(p =>
                `<div class="premium-item"><strong>User:</strong> ${p.user || 'Anonymous'} | <strong>Question:</strong> ${p.question} | <strong>Count:</strong> ${p.count}</div>`
            ).join("");
        } else {
            pl.innerHTML = "<div style='padding:12px; color:#64748b;'>No premium suggestions yet</div>";
        }

        // Engagements table
        loadEngagements();

    } catch (err) {
        console.error(err);
        alert("Error loading dashboard. Please try again.");
    }
}

// Load Engagements
async function loadEngagements() {
    try {
        const res = await fetch('/api/admin/engagements');
        const items = await res.json();
        const tbody = document.querySelector("#engTable tbody");
        tbody.innerHTML = "";
        items.forEach(it => {
            const row = `<tr>
                <td>${it.age || "-"}</td>
                <td>${it.job || "-"}</td>
                <td>${(it.desires || []).join(", ") || "-"}</td>
                <td>${it.question_clicked || "-"}</td>
                <td>${it.service || "-"}</td>
                <td>${it.ad || "-"}</td>
                <td>${it.timestamp || "-"}</td>
            </tr>`;
            tbody.insertAdjacentHTML('beforeend', row);
        });
    } catch (err) {
        console.error("Error loading engagements:", err);
    }
}

// Categories CRUD
async function loadCategories() {
    try {
        const res = await fetch('/api/admin/categories');
        const items = await res.json();
        const el = document.getElementById('categoriesList');
        if (items.length === 0) {
            el.innerHTML = '<div style="padding:12px; color:#64748b;">No categories found. Add one above.</div>';
        } else {
            el.innerHTML = items.map(c => `
                <div class="manage-item">
                    <div>
                        <div class="manage-item-title">${c.name?.en || c.id}</div>
                        <div class="manage-item-sub">ID: ${c.id} | Ministries: ${(c.ministry_ids || []).join(', ')}</div>
                    </div>
                    <button class="delete-btn" onclick="deleteCategory('${c.id}')">Delete</button>
                </div>
            `).join('');
        }
    } catch (err) {
        console.error("Error loading categories:", err);
    }
}

async function addCategory() {
    const id = document.getElementById('cat_id').value.trim();
    const name_en = document.getElementById('cat_name_en').value.trim();
    const ministry_ids = document.getElementById('cat_ministry_ids').value.split(',').map(s => s.trim()).filter(s => s);

    if (!id || !name_en) {
        alert('Please fill in ID and Name');
        return;
    }

    try {
        await fetch('/api/admin/categories', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, name: { en: name_en }, ministry_ids })
        });
        document.getElementById('cat_id').value = '';
        document.getElementById('cat_name_en').value = '';
        document.getElementById('cat_ministry_ids').value = '';
        loadCategories();
    } catch (err) {
        alert('Error adding category: ' + err.message);
    }
}

async function deleteCategory(id) {
    if (!confirm('Delete this category?')) return;
    try {
        await fetch(`/api/admin/categories?id=${id}`, { method: 'DELETE' });
        loadCategories();
    } catch (err) {
        alert('Error deleting category: ' + err.message);
    }
}

// Officers CRUD
async function loadOfficers() {
    try {
        const res = await fetch('/api/admin/officers');
        const items = await res.json();
        const el = document.getElementById('officersList');
        if (items.length === 0) {
            el.innerHTML = '<div style="padding:12px; color:#64748b;">No officers found. Add one above.</div>';
        } else {
            el.innerHTML = items.map(o => `
                <div class="manage-item">
                    <div>
                        <div class="manage-item-title">${o.name}</div>
                        <div class="manage-item-sub">${o.role} | Ministry: ${o.ministry_id}</div>
                    </div>
                    <button class="delete-btn" onclick="deleteOfficer('${o.id}')">Delete</button>
                </div>
            `).join('');
        }
    } catch (err) {
        console.error("Error loading officers:", err);
    }
}

async function addOfficer() {
    const id = document.getElementById('off_id').value.trim();
    const name = document.getElementById('off_name').value.trim();
    const role = document.getElementById('off_role').value.trim();
    const ministry_id = document.getElementById('off_ministry').value.trim();

    if (!id || !name) {
        alert('Please fill in ID and Name');
        return;
    }

    try {
        await fetch('/api/admin/officers', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, name, role, ministry_id })
        });
        document.getElementById('off_id').value = '';
        document.getElementById('off_name').value = '';
        document.getElementById('off_role').value = '';
        document.getElementById('off_ministry').value = '';
        loadOfficers();
    } catch (err) {
        alert('Error adding officer: ' + err.message);
    }
}

async function deleteOfficer(id) {
    if (!confirm('Delete this officer?')) return;
    try {
        await fetch(`/api/admin/officers?id=${id}`, { method: 'DELETE' });
        loadOfficers();
    } catch (err) {
        alert('Error deleting officer: ' + err.message);
    }
}

// Ads CRUD
async function loadAds() {
    try {
        const res = await fetch('/api/admin/ads');
        const items = await res.json();
        const el = document.getElementById('adsList');
        if (items.length === 0) {
            el.innerHTML = '<div style="padding:12px; color:#64748b;">No ads found. Add one above.</div>';
        } else {
            el.innerHTML = items.map(a => `
                <div class="manage-item">
                    <div>
                        <div class="manage-item-title">${a.title}</div>
                        <div class="manage-item-sub">${a.body?.substring(0, 60) || ''}... | <a href="${a.link}" target="_blank">View Link</a></div>
                    </div>
                    <div style="display:flex; gap:8px; align-items:center;">
                        <span class="status-badge ${a.active !== false ? 'status-active' : 'status-inactive'}">${a.active !== false ? 'Active' : 'Inactive'}</span>
                        <button class="delete-btn" onclick="deleteAd('${a.id}')">Delete</button>
                    </div>
                </div>
            `).join('');
        }
    } catch (err) {
        console.error("Error loading ads:", err);
    }
}

async function addAd() {
    const id = document.getElementById('ad_id').value.trim();
    const title = document.getElementById('ad_title').value.trim();
    const body = document.getElementById('ad_body').value.trim();
    const link = document.getElementById('ad_link').value.trim();

    if (!id || !title) {
        alert('Please fill in ID and Title');
        return;
    }

    try {
        await fetch('/api/admin/ads', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ id, title, body, link, active: true })
        });
        document.getElementById('ad_id').value = '';
        document.getElementById('ad_title').value = '';
        document.getElementById('ad_body').value = '';
        document.getElementById('ad_link').value = '';
        loadAds();
    } catch (err) {
        alert('Error adding ad: ' + err.message);
    }
}

async function deleteAd(id) {
    if (!confirm('Delete this ad?')) return;
    try {
        await fetch(`/api/admin/ads?id=${id}`, { method: 'DELETE' });
        loadAds();
    } catch (err) {
        alert('Error deleting ad: ' + err.message);
    }
}

// Event listeners
document.getElementById("logoutBtn")?.addEventListener('click', async () => {
    await fetch('/api/admin/logout', { method: 'POST' });
    window.location = "/admin";
});

document.getElementById("exportCsv")?.addEventListener('click', () => {
    window.location = '/api/admin/export_csv';
});

// Initial load
window.onload = loadDashboard;
