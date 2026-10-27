/**
 * VibeRadar Dashboard Client Script
 */

let currentData = null;
let currentIdeas = [];

// DOM Elements
const lastUpdatedEl = document.getElementById("lastUpdated");
const btnScan = document.getElementById("btnScan");
const btnDice = document.getElementById("btnDice");
const btnAddIdea = document.getElementById("btnAddIdea");
const btnCopyReport = document.getElementById("btnCopyReport");

const statSparks = document.getElementById("statSparks");
const statGitHub = document.getElementById("statGitHub");
const statHN = document.getElementById("statHN");
const statHF = document.getElementById("statHF");
const userIdeaCount = document.getElementById("userIdeaCount");
const keywordsList = document.getElementById("keywordsList");

const sparksGrid = document.getElementById("sparksGrid");
const githubGrid = document.getElementById("githubGrid");
const hnGrid = document.getElementById("hnGrid");
const hfGrid = document.getElementById("hfGrid");
const userIdeasList = document.getElementById("userIdeasList");
const reportViewer = document.getElementById("reportViewer");
const toastEl = document.getElementById("toast");

// Tab Switching
document.querySelectorAll(".tab-btn").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));
        document.querySelectorAll(".tab-content").forEach(c => c.classList.remove("active"));

        btn.classList.add("active");
        const tabId = btn.getAttribute("data-tab");
        const targetTab = document.getElementById(`tab-${tabId}`);
        if (targetTab) targetTab.classList.add("active");

        if (tabId === "report") loadReport();
    });
});

document.querySelectorAll(".stat-card").forEach(card => {
    card.addEventListener("click", () => {
        const tab = card.getAttribute("data-tab");
        const tabBtn = document.querySelector(`.tab-btn[data-tab="${tab}"]`);
        if (tabBtn) tabBtn.click();
    });
});

// Toast Notification
function showToast(msg) {
    toastEl.textContent = msg;
    toastEl.classList.add("show");
    setTimeout(() => toastEl.classList.remove("show"), 3200);
}

// Fetch Trends
async function loadTrends() {
    try {
        lastUpdatedEl.textContent = "Đang tải dữ liệu...";
        const res = await fetch("/api/trends");
        if (!res.ok) throw new Error("Network response was not ok");
        currentData = await res.json();
        renderAll(currentData);
    } catch (e) {
        lastUpdatedEl.textContent = "Lỗi kết nối";
        showToast("❌ Không thể tải dữ liệu xu hướng!");
    }
}

// Trigger Full Scan
async function triggerScan() {
    btnScan.disabled = true;
    btnScan.innerHTML = "<span>⏳</span> Đang quét toàn cầu...";
    showToast("🚀 Bắt đầu quét GitHub, Hacker News, Hugging Face, Dev.to...");

    try {
        const res = await fetch("/api/scan", { method: "POST" });
        if (!res.ok) throw new Error("Scan failed");
        currentData = await res.json();
        renderAll(currentData);
        showToast("✔ Đã cập nhật xu hướng và phát sinh ý tưởng mới!");
    } catch (e) {
        showToast("❌ Quét thất bại, vui lòng kiểm tra kết nối mạng.");
    } finally {
        btnScan.disabled = false;
        btnScan.innerHTML = '<span class="btn-icon">⚡</span> Quét Lại Ngay';
    }
}

// Regenerate Sparks
async function regenerateSparks() {
    btnDice.disabled = true;
    btnDice.innerHTML = "<span>🎲</span> Đang gieo quẻ...";
    try {
        const res = await fetch("/api/sparks/regenerate");
        const data = await res.json();
        if (currentData) {
            currentData.sparks = data.sparks;
            renderSparks(data.sparks);
            statSparks.textContent = data.sparks.length;
        }
        showToast("🎲 Đã phát sinh bộ ý tưởng mới nảy ra!");
    } catch (e) {
        showToast("❌ Không thể sinh ý tưởng mới.");
    } finally {
        btnDice.disabled = false;
        btnDice.innerHTML = "<span>🎲</span> Nảy Ý Tưởng Mới";
    }
}

// Render Data
function renderAll(data) {
    if (!data) return;

    lastUpdatedEl.textContent = `Cập nhật: ${data.timestamp || 'Vừa xong'}`;

    // Keywords
    keywordsList.innerHTML = "";
    (data.keywords || []).slice(0, 10).forEach(kw => {
        const span = document.createElement("span");
        span.className = "kw-tag";
        span.textContent = `#${kw}`;
        keywordsList.appendChild(span);
    });

    // Counts
    const items = data.items || [];
    const ghItems = items.filter(i => i.source.includes("GitHub"));
    const hnItems = items.filter(i => i.source.includes("HN") || i.source.includes("Hacker"));
    const hfItems = items.filter(i => i.source.includes("Hugging"));

    statSparks.textContent = (data.sparks || []).length;
    statGitHub.textContent = ghItems.length;
    statHN.textContent = hnItems.length;
    statHF.textContent = hfItems.length;

    renderSparks(data.sparks || []);
    renderItems(githubGrid, ghItems);
    renderItems(hnGrid, hnItems);
    renderItems(hfGrid, hfItems);
}

// Render Vibe Sparks
function renderSparks(sparks) {
    sparksGrid.innerHTML = "";
    sparks.forEach((s, idx) => {
        const card = document.createElement("div");
        card.className = "card";
        card.innerHTML = `
            <div class="card-top">
                <div class="card-header-line">
                    <h3 class="card-title">${s.title}</h3>
                    <span class="vibe-badge">⭐ ${s.vibe_score} VIBE</span>
                </div>
                <p class="card-desc">${s.desc}</p>
                <div class="card-meta">
                    <div class="meta-row">
                        <span class="meta-label">Cảm hứng:</span>
                        <a href="${s.inspiration_url}" target="_blank" class="meta-val" style="color: var(--accent-cyan); text-decoration: none;">${s.inspiration_source} ↗</a>
                    </div>
                    <div class="meta-row">
                        <span class="meta-label">Độ khó:</span>
                        <span class="meta-val">${s.difficulty}</span>
                    </div>
                    <div class="meta-row">
                        <span class="meta-label">Stack đề xuất:</span>
                        <span class="meta-val">${s.tech_stack}</span>
                    </div>
                </div>
            </div>
            <div class="card-footer">
                <div class="tag-list">
                    ${(s.tags || []).map(t => `<span class="tag-chip">#${t}</span>`).join("")}
                </div>
                <div style="display: flex; gap: 6px;">
                    <button class="btn-save-idea" onclick="quickCreateVideoFromSpark('${s.title.replace(/'/g, "\\'")}')" style="background: rgba(255, 183, 3, 0.15); color: var(--accent-yellow); border-color: rgba(255, 183, 3, 0.3);" title="Tạo video ngắn từ ý tưởng này">
                        🎬 Tạo Video
                    </button>
                    <button class="btn-save-idea" onclick="saveSparkToVault(${idx})">
                        📥 Lưu Vào Két
                    </button>
                </div>
            </div>
        `;
        sparksGrid.appendChild(card);
    });
}

// Render Generic Items
function renderItems(container, items) {
    container.innerHTML = "";
    if (!items.length) {
        container.innerHTML = `<p style="color: var(--text-dim); padding: 20px;">Không có dữ liệu.</p>`;
        return;
    }
    items.forEach(it => {
        const card = document.createElement("div");
        card.className = "card";
        card.innerHTML = `
            <div class="card-top">
                <div class="card-header-line">
                    <a href="${it.url}" target="_blank" class="card-title">${it.title} ↗</a>
                    <span class="tag-chip" style="color: var(--accent-yellow)">⭐ ${it.stars || 0}</span>
                </div>
                <p class="card-desc">${it.desc || "Không có mô tả"}</p>
                <div class="card-meta">
                    <div class="meta-row">
                        <span class="meta-label">Phân loại:</span>
                        <span class="meta-val">${it.language || it.category || 'Chung'}</span>
                    </div>
                    <div class="meta-row">
                        <span class="meta-label">Tăng trưởng:</span>
                        <span class="meta-val">${it.stars_period || 'Mới'}</span>
                    </div>
                </div>
            </div>
            <div class="card-footer">
                <span class="tag-chip">${it.source}</span>
                <a href="${it.url}" target="_blank" class="btn-save-idea" style="text-decoration: none;">Xem Nguồn ↗</a>
            </div>
        `;
        container.appendChild(card);
    });
}

// User Idea Vault
async function loadUserIdeas() {
    try {
        const res = await fetch("/api/ideas");
        currentIdeas = await res.json();
        renderUserIdeas(currentIdeas);
    } catch (e) {
        console.error("Failed loading user ideas:", e);
    }
}

function renderUserIdeas(ideas) {
    userIdeaCount.textContent = ideas.length;
    userIdeasList.innerHTML = "";

    if (!ideas.length) {
        userIdeasList.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; color: var(--text-dim); padding: 40px;">
                Chưa có ý tưởng nào trong két. Hãy nhập một ý tưởng bất chợt ở trên hoặc bấm "Lưu Vào Két" từ danh sách gợi ý!
            </div>
        `;
        return;
    }

    ideas.forEach(idea => {
        const card = document.createElement("div");
        card.className = "user-idea-card";

        let statusClass = "status-idea";
        let statusText = "💡 Ý Tưởng";
        if (idea.status === "building") {
            statusClass = "status-building";
            statusText = "🔨 Đang Build";
        } else if (idea.status === "done") {
            statusClass = "status-done";
            statusText = "✅ Hoàn Thành";
        }

        card.innerHTML = `
            <div>
                <div class="card-header-line">
                    <h3 class="card-title">${idea.title}</h3>
                    <span class="status-pill ${statusClass}" onclick="cycleIdeaStatus('${idea.id}', '${idea.status}')" title="Bấm để đổi trạng thái">
                        ${statusText}
                    </span>
                </div>
                <p class="card-desc">${idea.desc || "Không có ghi chú thêm."}</p>
                <div class="tag-list">
                    ${(idea.tags || []).map(t => `<span class="tag-chip">#${t}</span>`).join("")}
                </div>
            </div>
            <div class="card-actions-row">
                <span style="font-size: 11px; color: var(--text-dim);">${idea.created_at || ''}</span>
                <button class="btn-del" onclick="deleteUserIdea('${idea.id}')" title="Xóa ý tưởng này">🗑️ Xóa</button>
            </div>
        `;
        userIdeasList.appendChild(card);
    });
}

// Save Spark to Vault
window.saveSparkToVault = async function(idx) {
    if (!currentData || !currentData.sparks || !currentData.sparks[idx]) return;
    const spark = currentData.sparks[idx];

    try {
        const res = await fetch("/api/ideas", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                title: spark.title,
                desc: `${spark.desc}\n\n[Cảm hứng: ${spark.inspiration_source} (${spark.inspiration_url})] | Stack: ${spark.tech_stack}`,
                tags: spark.tags || ["Vibe Spark"]
            })
        });
        if (res.ok) {
            showToast("✔ Đã lưu ý tưởng vào Két cá nhân!");
            loadUserIdeas();
        }
    } catch (e) {
        showToast("❌ Lỗi khi lưu ý tưởng.");
    }
};

// Add User Idea Form
btnAddIdea.addEventListener("click", async () => {
    const titleInput = document.getElementById("inputIdeaTitle");
    const descInput = document.getElementById("inputIdeaDesc");
    const tagsInput = document.getElementById("inputIdeaTags");

    const title = titleInput.value.trim();
    if (!title) {
        showToast("⚠️ Vui lòng nhập tiêu đề ý tưởng!");
        titleInput.focus();
        return;
    }

    const desc = descInput.value.trim();
    const tags = tagsInput.value.split(",").map(t => t.trim()).filter(Boolean);

    try {
        const res = await fetch("/api/ideas", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ title, desc, tags: tags.length ? tags : ["Vibe"] })
        });
        if (res.ok) {
            titleInput.value = "";
            descInput.value = "";
            tagsInput.value = "";
            showToast("✔ Đã thêm ý tưởng mới vào két!");
            loadUserIdeas();
        }
    } catch (e) {
        showToast("❌ Lỗi khi thêm ý tưởng.");
    }
});

// Cycle status
window.cycleIdeaStatus = async function(id, currentStatus) {
    const nextStatus = currentStatus === "idea" ? "building" : (currentStatus === "building" ? "done" : "idea");
    try {
        const res = await fetch(`/api/ideas/${id}/status`, {
            method: "PATCH",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status: nextStatus })
        });
        if (res.ok) {
            loadUserIdeas();
        }
    } catch (e) {
        showToast("❌ Lỗi cập nhật trạng thái.");
    }
};

// Delete Idea
window.deleteUserIdea = async function(id) {
    if (!confirm("Bạn có chắc muốn xóa ý tưởng này khỏi két?")) return;
    try {
        const res = await fetch(`/api/ideas/${id}`, { method: "DELETE" });
        if (res.ok) {
            showToast("✔ Đã xóa ý tưởng.");
            loadUserIdeas();
        }
    } catch (e) {
        showToast("❌ Lỗi khi xóa ý tưởng.");
    }
};

// Load Report
async function loadReport() {
    try {
        const res = await fetch("/api/report/latest");
        const data = await res.json();
        reportViewer.textContent = data.markdown || "Chưa có báo cáo.";
    } catch (e) {
        reportViewer.textContent = "Lỗi tải báo cáo.";
    }
}

// Copy Report
btnCopyReport.addEventListener("click", () => {
    navigator.clipboard.writeText(reportViewer.textContent).then(() => {
        showToast("📋 Đã sao chép toàn bộ báo cáo Markdown!");
    });
});

// Event Listeners
btnScan.addEventListener("click", triggerScan);
btnDice.addEventListener("click", regenerateSparks);

// Initial Load
document.addEventListener("DOMContentLoaded", () => {
    loadTrends();
    loadUserIdeas();
});

// Video Studio Handlers
const btnGenerateVideo = document.getElementById("btnGenerateVideo");
const videoInputContent = document.getElementById("videoInputContent");
const videoContentType = document.getElementById("videoContentType");
const videoLang = document.getElementById("videoLang");
const videoRatio = document.getElementById("videoRatio");
const videoResultSection = document.getElementById("videoResultSection");
const videoPlayer = document.getElementById("videoPlayer");
const videoMetaBox = document.getElementById("videoMetaBox");
const pastVideosGrid = document.getElementById("pastVideosGrid");

async function loadPastVideos() {
    try {
        const res = await fetch("/api/video/list");
        const videos = await res.json();
        renderPastVideos(videos);
    } catch (e) {
        console.error("Error loading past videos:", e);
    }
}

function renderPastVideos(videos) {
    if (!pastVideosGrid) return;
    pastVideosGrid.innerHTML = "";
    if (!videos.length) {
        pastVideosGrid.innerHTML = `<p style="color: var(--text-dim); padding: 10px;">Chưa có video nào. Hãy tạo video đầu tiên ở trên!</p>`;
        return;
    }

    videos.forEach(v => {
        const card = document.createElement("div");
        card.className = "past-video-card";
        card.innerHTML = `
            <div style="font-weight: 700; color: var(--accent-cyan); font-size: 14px;">🎬 ${v.name}</div>
            <div style="font-size: 12px; color: var(--text-dim);">Dung lượng: ${v.size_mb} MB | ${v.created_at}</div>
            <div style="display: flex; gap: 8px; margin-top: 6px;">
                <button class="btn btn-secondary" style="padding: 4px 10px; font-size: 12px;" onclick="playPastVideo('${v.url}')">▶ Xem Thử</button>
                <a href="${v.url}" download class="btn btn-secondary" style="padding: 4px 10px; font-size: 12px; text-decoration: none;">⬇ Tải Về</a>
            </div>
        `;
        pastVideosGrid.appendChild(card);
    });
}

window.playPastVideo = function(url) {
    videoResultSection.style.display = "block";
    videoPlayer.src = url;
    videoPlayer.scrollIntoView({ behavior: "smooth" });
    videoPlayer.play();
};

if (btnGenerateVideo) {
    btnGenerateVideo.addEventListener("click", async () => {
        const content = videoInputContent.value.trim();
        if (!content) {
            showToast("⚠️ Vui lòng nhập chủ đề hoặc nội dung kịch bản!");
            videoInputContent.focus();
            return;
        }

        const isRawText = videoContentType.value === "text";
        const lang = videoLang.value;
        const ratio = videoRatio.value;

        btnGenerateVideo.disabled = true;
        btnGenerateVideo.innerHTML = `<span>⏳</span> Đang dựng video (TTS + Frames + FFmpeg)...`;
        showToast("🚀 Bắt đầu quá trình dựng video tự động, vui lòng chờ ~20 giây...");

        try {
            const res = await fetch("/api/video/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    content: content,
                    is_raw_text: isRawText,
                    lang: lang,
                    ratio: ratio
                })
            });

            if (!res.ok) {
                const err = await res.json();
                throw new Error(err.detail || "Video generation failed");
            }

            const data = await res.json();
            showToast("🎉 Video đã được render thành công!");

            // Show video player
            videoResultSection.style.display = "block";
            videoPlayer.src = data.video_url;
            videoPlayer.play();

            videoMetaBox.innerHTML = `
                <div><strong>📁 Tên file:</strong> ${data.output_path.split('\\\\').pop().split('/').pop()}</div>
                <div><strong>⏱️ Thời lượng:</strong> ${data.duration} giây (${data.scenes_count} phân cảnh)</div>
                <div><strong>💾 Dung lượng:</strong> ${data.file_size_mb} MB</div>
                <div><strong>⚡ Thời gian dựng:</strong> ${data.elapsed_seconds} giây</div>
                <div style="margin-top: 10px;">
                    <a href="${data.video_url}" download class="btn btn-primary" style="text-decoration: none;">⬇ Tải Video Xuống Máy</a>
                </div>
            `;
            videoResultSection.scrollIntoView({ behavior: "smooth" });
            loadPastVideos();
        } catch (e) {
            showToast(`❌ Lỗi tạo video: ${e.message}`);
        } finally {
            btnGenerateVideo.disabled = false;
            btnGenerateVideo.innerHTML = `<span>🚀</span> Bắt Đầu Tạo Video`;
        }
    });
}

// Initial load past videos
document.addEventListener("DOMContentLoaded", () => {
    loadPastVideos();
});

window.quickCreateVideoFromSpark = function(title) {
    const videoTabBtn = document.querySelector('.tab-btn[data-tab="video"]');
    if (videoTabBtn) videoTabBtn.click();
    if (videoInputContent) {
        // Strip emoji for clean topic
        const cleanTitle = title.replace(/^[^\w\s\u00C0-\u1EF9]+/, '').trim();
        videoInputContent.value = cleanTitle;
        if (videoContentType) videoContentType.value = "topic";
        videoInputContent.scrollIntoView({ behavior: "smooth" });
    }
    showToast(`🎬 Đã chuyển chủ đề sang Video Studio! Hãy bấm "Bắt Đầu Tạo Video".`);
};
