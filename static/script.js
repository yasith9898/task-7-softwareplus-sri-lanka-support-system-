// Citizen Portal - Frontend Script (Updated with AI chat, autosuggest, progressive profile)
let lang = "en";
let services = [];
let categories = [];
let currentServiceName = "";
let currentSub = null;
let profile_id = null;

// Load categories
async function loadCategories() {
    try {
        const res = await fetch("/api/categories");
        categories = await res.json();
        const el = document.getElementById("category-list");
        el.innerHTML = "";
        categories.forEach(c => {
            const btn = document.createElement("div");
            btn.className = "cat-item";
            btn.textContent = c.name?.[lang] || c.name?.en || c.id;
            btn.onclick = () => loadMinistriesInCategory(c);
            el.appendChild(btn);
        });
        // Load ads
        loadAds();
    } catch (err) {
        console.error("Error loading categories:", err);
        // Fallback to services
        loadServices();
    }
}

// Load ministries within a category
async function loadMinistriesInCategory(cat) {
    document.getElementById("sub-list").innerHTML = "";
    document.getElementById("sub-title").innerText = cat.name?.[lang] || cat.name?.en || cat.id;
    document.getElementById("question-list").innerHTML = "";
    document.getElementById("answer-box").innerHTML = "";

    // If categories document contains ministry_ids show them
    if (cat.ministry_ids && cat.ministry_ids.length) {
        for (let id of cat.ministry_ids) {
            try {
                const r = await fetch(`/api/service/${id}`);
                const s = await r.json();
                if (s && s.subservices) {
                    s.subservices.forEach(sub => {
                        let li = document.createElement("li");
                        li.textContent = sub.name?.[lang] || sub.name?.en || sub.id;
                        li.onclick = () => loadQuestions(s, sub);
                        document.getElementById("sub-list").appendChild(li);
                    });
                }
            } catch (err) {
                console.error("Error loading service:", id, err);
            }
        }
    } else {
        // Fallback: query services and filter by category
        try {
            const svcRes = await fetch("/api/services");
            const all = await svcRes.json();
            all.filter(s => s.category === cat.id).forEach(s => {
                (s.subservices || []).forEach(sub => {
                    let li = document.createElement("li");
                    li.textContent = sub.name?.[lang] || sub.name?.en || sub.id;
                    li.onclick = () => loadQuestions(s, sub);
                    document.getElementById("sub-list").appendChild(li);
                });
            });
        } catch (err) {
            console.error("Error loading services for category:", err);
        }
    }
}

// Fallback: Load services directly (ministries list)
async function loadServices() {
    try {
        const res = await fetch("/api/services");
        services = await res.json();
        const list = document.getElementById("category-list");
        list.innerHTML = "";
        
        services.forEach(s => {
            let div = document.createElement("div");
            div.className = "cat-item";
            div.textContent = s.name?.[lang] || s.name?.en || s.id;
            div.onclick = () => loadSubservices(s);
            list.appendChild(div);
        });
    } catch (error) {
        console.error("Error loading services:", error);
    }
}

function setLang(l) {
    lang = l;
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-lang') === l) {
            btn.classList.add('active');
        }
    });
    loadCategories();
    document.getElementById("sub-list").innerHTML = "";
    document.getElementById("question-list").innerHTML = "";
    document.getElementById("answer-box").innerHTML = "";
}

function loadSubservices(service) {
    currentServiceName = service.name?.[lang] || service.name?.en || service.id;
    const subList = document.getElementById("sub-list");
    subList.innerHTML = "";
    document.getElementById("sub-title").innerText = currentServiceName;
    (service.subservices || []).forEach(sub => {
        let li = document.createElement("li");
        li.textContent = sub.name?.[lang] || sub.name?.en || sub.id;
        li.onclick = () => loadQuestions(service, sub);
        subList.appendChild(li);
    });
}

function loadQuestions(service, sub) {
    currentServiceName = service.name?.[lang] || service.name?.en || service.id;
    currentSub = sub;
    const qList = document.getElementById("question-list");
    qList.innerHTML = "";
    document.getElementById("q-title").innerText = sub.name?.[lang] || sub.name?.en || sub.id;
    (sub.questions || []).forEach(q => {
        let li = document.createElement("li");
        li.textContent = q.q?.[lang] || q.q?.en || q.q;
        li.onclick = () => showAnswer(service, sub, q);
        qList.appendChild(li);
    });
}

function showAnswer(service, sub, q) {
    let html = `<h3>${q.q?.[lang] || q.q?.en || q.q}</h3>`;
    html += `<p>${q.answer?.[lang] || q.answer?.en || q.answer}</p>`;
    if (q.downloads && q.downloads.length) {
        html += `<p><b>📥 Downloads:</b> ${q.downloads.map(d => `<a href="${d}" target="_blank">${d.split("/").pop()}</a>`).join(", ")}</p>`;
    }
    if (q.location) {
        html += `<p><b>📍 Location:</b> <a href="${q.location}" target="_blank">View Map</a></p>`;
    }
    if (q.instructions) {
        html += `<p><b>📋 Instructions:</b> ${q.instructions}</p>`;
    }
    document.getElementById("answer-box").innerHTML = html;

    // Log engagement non-blocking (without prompts)
    fetch("/api/engagement", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            user_id: profile_id,
            age: null,
            job: null,
            desires: [],
            question_clicked: q.q?.[lang] || q.q?.en || q.q,
            service: currentServiceName
        })
    }).catch(err => console.error("Engagement log failed:", err));
}

// Chat UI
function openChat() {
    document.getElementById("chat-panel").classList.add("open");
}

function closeChat() {
    document.getElementById("chat-panel").classList.remove("open");
}

async function sendChat() {
    const input = document.getElementById("chat-text");
    const text = input.value.trim();
    if (!text) return;
    appendChat("user", text);
    input.value = "";

    // Show typing indicator
    const typingId = appendChat("bot", "Thinking...");

    try {
        // Call AI endpoint
        const res = await fetch("/api/ai/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query: text, top_k: 5 })
        });
        const data = await res.json();

        // Remove typing indicator
        removeChat(typingId);

        if (data.error) {
            appendChat("bot", "Sorry, I couldn't process your request. Please try again.");
        } else {
            let reply = data.answer || "No matching content found.";
            // Format the answer nicely
            reply = formatAIResponse(reply, data.sources);
            appendChat("bot", reply, true);
        }

        // Log engagement
        fetch("/api/engagement", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_id: profile_id, question_clicked: text, service: null })
        }).catch(() => {});
    } catch (err) {
        removeChat(typingId);
        appendChat("bot", "Sorry, there was an error connecting to the AI service.");
        console.error("AI search error:", err);
    }
}

function formatAIResponse(answer, sources) {
    // Clean up and format the response
    let parts = answer.split("---").filter(p => p.trim());
    if (parts.length > 1) {
        return parts[0].trim();
    }
    return answer;
}

let chatMsgId = 0;
function appendChat(sender, text, isHtml = false) {
    const body = document.getElementById("chat-body");
    const div = document.createElement("div");
    div.className = "chat-msg " + (sender === "user" ? "user-msg" : "bot-msg");
    div.id = "chat-msg-" + (++chatMsgId);
    if (isHtml) {
        div.innerHTML = `<p>${text}</p>`;
    } else {
        div.innerHTML = `<p>${text}</p>`;
    }
    body.appendChild(div);
    body.scrollTop = body.scrollHeight;
    return div.id;
}

function removeChat(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

// Autosuggest for search input
let suggestTimer = null;
async function autosuggest(q) {
    clearTimeout(suggestTimer);
    if (!q || q.length < 2) {
        document.getElementById("suggestions").innerHTML = "";
        return;
    }
    suggestTimer = setTimeout(async () => {
        try {
            const res = await fetch(`/api/search/autosuggest?q=${encodeURIComponent(q)}`);
            const items = await res.json();
            const el = document.getElementById("suggestions");
            if (items.length === 0) {
                el.innerHTML = '<div class="s-item s-empty">No results. Try the AI Assistant!</div>';
            } else {
                el.innerHTML = items.map(it => 
                    `<div class="s-item" onclick='pickSuggestion(${JSON.stringify(JSON.stringify(it))})'>${it.name?.en || it.name || it.id}</div>`
                ).join("");
            }
        } catch (err) {
            console.error("Autosuggest error:", err);
        }
    }, 250);
}

function pickSuggestion(serialized) {
    const it = JSON.parse(serialized);
    // If the suggestion has subservices open first subservice
    if (it && it.subservices && it.subservices.length) {
        loadSubservices(it);
    }
    document.getElementById("suggestions").innerHTML = "";
    document.getElementById("search-input").value = "";
}

// Profile modal flow
function showProfileModal() {
    document.getElementById("profile-modal").style.display = "flex";
}

function closeProfileModal() {
    document.getElementById("profile-modal").style.display = "none";
}

function updateStepDots(step) {
    for (let i = 1; i <= 3; i++) {
        document.getElementById(`dot-${i}`).classList.remove('active');
        if (i <= step) {
            document.getElementById(`dot-${i}`).classList.add('active');
        }
    }
}

function profileNext(step) {
    document.getElementById(`profile-step-${step}`).style.display = "none";
    document.getElementById(`profile-step-${step + 1}`).style.display = "block";
    updateStepDots(step + 1);
}

function profileBack(step) {
    document.getElementById(`profile-step-${step}`).style.display = "none";
    document.getElementById(`profile-step-${step - 1}`).style.display = "block";
    updateStepDots(step - 1);
}

async function profileSubmit() {
    const data1 = { name: document.getElementById("p_name").value, age: document.getElementById("p_age").value };
    const data2 = { email: document.getElementById("p_email").value, phone: document.getElementById("p_phone").value };
    const data3 = { job: document.getElementById("p_job").value };

    try {
        // Send steps sequentially
        let res = await fetch("/api/profile/step", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ email: data2.email, step: "basic", data: data1 })
        });
        let j = await res.json();
        profile_id = j.profile_id || null;

        await fetch("/api/profile/step", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ profile_id: profile_id, step: "contact", data: data2 })
        });

        await fetch("/api/profile/step", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ profile_id: profile_id, step: "employment", data: data3 })
        });

        closeProfileModal();
        
        // Store profile_id in localStorage
        if (profile_id) {
            localStorage.setItem('profile_id', profile_id);
        }
    } catch (err) {
        console.error("Profile submit error:", err);
        closeProfileModal();
    }
}

// Load ads
async function loadAds() {
    try {
        const res = await fetch("/api/ads");
        const ads = await res.json();
        const el = document.getElementById("ads-area");
        if (ads.length === 0) {
            el.innerHTML = '<div class="ad-card"><p>No announcements at this time.</p></div>';
        } else {
            el.innerHTML = ads.slice(0, 3).map(a => 
                `<div class="ad-card">
                    <a href="${a.link || '#'}" target="_blank">
                        <h4>${a.title}</h4>
                        <p>${a.body || ''}</p>
                    </a>
                </div>`
            ).join("");
        }
    } catch (err) {
        console.error("Error loading ads:", err);
    }
}

// Initial load
window.onload = async () => {
    // Check for stored profile
    profile_id = localStorage.getItem('profile_id') || null;
    
    await loadCategories();
    
    // Load services as backup
    try {
        const svcRes = await fetch("/api/services");
        services = await svcRes.json();
    } catch (err) {
        console.error("Error loading services:", err);
    }

    document.querySelector('.lang-btn[data-lang="en"]')?.classList.add('active');
};
