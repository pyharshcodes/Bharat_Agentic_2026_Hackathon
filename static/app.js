// Jan-Sahayak AI - Client-side Interactive Dashboard Controller
// Powered by Team CodeNova (Harsh Deep Chak & Pallak Devi)

let activePersonaId = "rameshwar_farmer";
let currentRunResult = null;
let isSpeaking = false;
let activeCategoryFilter = "all";
let allSchemesCatalogue = [];

document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  setupEventListeners();
  loadSchemesCatalogue();
  // Auto-run baseline persona on initial load
  runWorkflow({ persona_id: activePersonaId });
});

function initTheme() {
  const saved = localStorage.getItem("jansahayak_theme");
  const toggleBtn = document.getElementById("themeToggleBtn");
  if (saved === "dark") {
    document.body.classList.add("theme-dark");
    if (toggleBtn) toggleBtn.innerText = "☀️ Light Mode";
  } else {
    document.body.classList.remove("theme-dark");
    if (toggleBtn) toggleBtn.innerText = "🌙 Dark Mode";
  }
}

async function loadSchemesCatalogue() {
  try {
    const res = await fetch("/api/schemes");
    if (res.ok) {
      const data = await res.json();
      allSchemesCatalogue = data.schemes || [];
    }
  } catch (e) {
    console.warn("Could not load schemes catalogue:", e);
  }
}

function setupEventListeners() {
  // Theme Toggle Button
  const themeBtn = document.getElementById("themeToggleBtn");
  if (themeBtn) {
    themeBtn.addEventListener("click", () => {
      document.body.classList.toggle("theme-dark");
      const isDark = document.body.classList.contains("theme-dark");
      localStorage.setItem("jansahayak_theme", isDark ? "dark" : "light");
      themeBtn.innerText = isDark ? "☀️ Light Mode" : "🌙 Dark Mode";
    });
  }

  // Persona Card Clicks
  const personaCards = document.querySelectorAll(".persona-card");
  personaCards.forEach(card => {
    card.addEventListener("click", () => {
      personaCards.forEach(c => c.classList.remove("active"));
      card.classList.add("active");
      activePersonaId = card.getAttribute("data-id");
      document.getElementById("customQueryInput").value = "";
      runWorkflow({ persona_id: activePersonaId });
    });
  });

  // Launch Button Click
  const launchBtn = document.getElementById("launchBtn");
  launchBtn.addEventListener("click", () => {
    const customQuery = document.getElementById("customQueryInput").value.trim();
    if (customQuery.length > 0) {
      runWorkflow({ custom_query: customQuery });
    } else {
      runWorkflow({ persona_id: activePersonaId });
    }
  });

  // Category Filter Chips
  const filterChips = document.querySelectorAll(".filter-chip");
  filterChips.forEach(chip => {
    chip.addEventListener("click", () => {
      filterChips.forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      activeCategoryFilter = chip.getAttribute("data-cat");
      if (currentRunResult) {
        renderSchemes(currentRunResult.evaluation);
      }
    });
  });

  // Profile Customizer Sliders & Modal
  const openCustomizerBtn = document.getElementById("openCustomizerBtn");
  const customizerModal = document.getElementById("profileCustomizerModal");
  const customizerCloseBtn = document.getElementById("customizerCloseBtn");
  const cancelCustomizerBtn = document.getElementById("cancelCustomizerBtn");
  const applyCustomizerBtn = document.getElementById("applyCustomizerBtn");

  const custIncome = document.getElementById("custIncome");
  const custIncomeVal = document.getElementById("custIncomeVal");
  if (custIncome && custIncomeVal) {
    custIncome.addEventListener("input", () => {
      custIncomeVal.innerText = `₹ ${parseInt(custIncome.value).toLocaleString('en-IN')}`;
    });
  }

  const custLand = document.getElementById("custLand");
  const custLandVal = document.getElementById("custLandVal");
  if (custLand && custLandVal) {
    custLand.addEventListener("input", () => {
      custLandVal.innerText = `${custLand.value} Acres`;
    });
  }

  if (openCustomizerBtn && customizerModal) {
    openCustomizerBtn.addEventListener("click", () => {
      customizerModal.style.display = "flex";
    });
    customizerCloseBtn.addEventListener("click", () => customizerModal.style.display = "none");
    cancelCustomizerBtn.addEventListener("click", () => customizerModal.style.display = "none");
    customizerModal.addEventListener("click", (e) => {
      if (e.target === customizerModal) customizerModal.style.display = "none";
    });

    applyCustomizerBtn.addEventListener("click", () => {
      const customProfile = {
        name: document.getElementById("custName").value || "Dynamic Citizen",
        age: parseInt(document.getElementById("custAge").value) || 40,
        gender: document.getElementById("custGender").value,
        state: document.getElementById("custState").value,
        district: "Varanasi",
        urban_rural: document.getElementById("custOccupation").value === "Street Vendor" ? "Urban" : "Rural",
        occupation: document.getElementById("custOccupation").value,
        annual_income: parseFloat(custIncome.value),
        landholding_acres: parseFloat(custLand.value),
        caste: document.getElementById("custCaste").value,
        marital_status: "Married",
        daughters_count: parseInt(document.getElementById("custDaughters").value),
        daughter_ages: parseInt(document.getElementById("custDaughters").value) > 0 ? [6] : [],
        housing_status: "Kutcha/Semi-pucca",
        existing_documents: ["Aadhaar Card", "Bank Account"]
      };

      customizerModal.style.display = "none";
      personaCards.forEach(c => c.classList.remove("active"));
      runWorkflow(customProfile);
    });
  }

  // DigiLocker Fetch Simulation
  const digilockerBtn = document.getElementById("digilockerFetchBtn");
  if (digilockerBtn) {
    digilockerBtn.addEventListener("click", async () => {
      if (!currentRunResult || !currentRunResult.profile) return;
      digilockerBtn.innerText = "⏳ Ingesting XML...";
      try {
        const res = await fetch("/api/digilocker-fetch", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ profile: currentRunResult.profile })
        });
        const updated = await res.json();
        currentRunResult = updated;
        const lang = document.getElementById("langSelect").value;
        renderResults(updated, lang);
        digilockerBtn.innerText = "✓ Synced via DigiLocker!";
        setTimeout(() => digilockerBtn.innerText = "🔗 Fetch via DigiLocker", 3000);
      } catch (err) {
        console.error(err);
        digilockerBtn.innerText = "🔗 Fetch via DigiLocker";
      }
    });
  }

  // Pipeline Step Clicks (Inspect Agent Telemetry)
  for (let i = 1; i <= 5; i++) {
    const stepEl = document.getElementById(`step-${i}`);
    if (stepEl) {
      stepEl.style.cursor = "pointer";
      stepEl.title = "Click to inspect agent telemetry and thoughts";
      stepEl.addEventListener("click", () => {
        openTelemetryModal(i);
      });
    }
  }

  // Modal Close Handlers
  const modalCloseBtn = document.getElementById("modalCloseBtn");
  const modalBackdrop = document.getElementById("telemetryModal");
  if (modalCloseBtn) {
    modalCloseBtn.addEventListener("click", () => modalBackdrop.style.display = "none");
  }
  if (modalBackdrop) {
    modalBackdrop.addEventListener("click", (e) => {
      if (e.target === modalBackdrop) modalBackdrop.style.display = "none";
    });
  }

  const schemeModal = document.getElementById("schemeDetailModal");
  const schemeCloseBtn = document.getElementById("schemeModalCloseBtn");
  if (schemeCloseBtn) {
    schemeCloseBtn.addEventListener("click", () => schemeModal.style.display = "none");
  }
  if (schemeModal) {
    schemeModal.addEventListener("click", (e) => {
      if (e.target === schemeModal) schemeModal.style.display = "none";
    });
  }

  // Voice Input (Web Speech Recognition)
  const voiceBtn = document.getElementById("voiceBtn");
  if (voiceBtn) {
    voiceBtn.addEventListener("click", () => {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) {
        alert("Speech Recognition is not supported on this browser. Please type your query.");
        return;
      }
      const recognition = new SpeechRecognition();
      recognition.lang = document.getElementById("langSelect").value === "Hindi" ? "hi-IN" : "en-IN";
      voiceBtn.innerText = "🔴 Listening...";
      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        document.getElementById("customQueryInput").value = transcript;
        voiceBtn.innerText = "🎙️";
        runWorkflow({ custom_query: transcript });
      };
      recognition.onerror = () => voiceBtn.innerText = "🎙️";
      recognition.onend = () => voiceBtn.innerText = "🎙️";
      recognition.start();
    });
  }

  // PDF Download Button
  const downloadPdfBtn = document.getElementById("downloadPdfBtn");
  downloadPdfBtn.addEventListener("click", () => {
    if (currentRunResult && currentRunResult.pdf_filename) {
      window.open(`/api/download/${currentRunResult.pdf_filename}`, "_blank");
    }
  });

  // Copy Grievance Button
  const copyBtn = document.getElementById("copyGrievanceBtn");
  if (copyBtn) {
    copyBtn.addEventListener("click", () => {
      const text = document.getElementById("grievanceText").innerText;
      navigator.clipboard.writeText(text).then(() => {
        const orig = copyBtn.innerText;
        copyBtn.innerText = "✓ Copied to Clipboard!";
        setTimeout(() => copyBtn.innerText = orig, 2000);
      });
    });
  }

  // Speech Button (Dual Mode: Browser Synthesis + Server gTTS fallback)
  const speakBtn = document.getElementById("speakBtn");
  const audioPlayer = document.getElementById("ttsAudioPlayer");

  if (speakBtn) {
    speakBtn.addEventListener("click", async () => {
      if (isSpeaking) {
        if ('speechSynthesis' in window) window.speechSynthesis.cancel();
        if (audioPlayer) {
          audioPlayer.pause();
          audioPlayer.currentTime = 0;
        }
        isSpeaking = false;
        speakBtn.innerText = "🔊 Listen in Hindi / English";
        return;
      }

      const summaryText = document.getElementById("summaryText").innerText;
      const lang = document.getElementById("langSelect").value;
      const isHindi = lang === "Hindi";

      if ('speechSynthesis' in window && window.speechSynthesis.getVoices().length > 0) {
        const utterance = new SpeechSynthesisUtterance(summaryText);
        utterance.lang = isHindi ? "hi-IN" : "en-IN";
        utterance.rate = 0.95;

        utterance.onend = () => {
          isSpeaking = false;
          speakBtn.innerText = "🔊 Listen in Hindi / English";
        };

        isSpeaking = true;
        speakBtn.innerText = "⏹️ Stop Audio";
        window.speechSynthesis.speak(utterance);
      } else {
        try {
          speakBtn.innerText = "⏳ Loading audio...";
          const res = await fetch("/api/speech", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text: summaryText, lang: lang })
          });
          const d = await res.json();
          if (d.audio_url) {
            audioPlayer.src = d.audio_url;
            audioPlayer.play();
            isSpeaking = true;
            speakBtn.innerText = "⏹️ Stop Audio";
            audioPlayer.onended = () => {
              isSpeaking = false;
              speakBtn.innerText = "🔊 Listen in Hindi / English";
            };
          }
        } catch (err) {
          console.error("Audio error:", err);
          speakBtn.innerText = "🔊 Listen in Hindi / English";
        }
      }
    });
  }
}

async function runWorkflow(payload) {
  setPipelineRunning();

  const lang = document.getElementById("langSelect").value;
  payload.language = lang;

  try {
    const res = await fetch("/api/run", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      throw new Error(`Server returned HTTP ${res.status}`);
    }

    const data = await res.json();
    currentRunResult = data;

    renderResults(data, lang);
  } catch (err) {
    console.error("Execution error:", err);
    alert("Failed to execute agent: " + err.message);
  }
}

function setPipelineRunning() {
  for (let i = 1; i <= 5; i++) {
    const stepEl = document.getElementById(`step-${i}`);
    if (stepEl) {
      stepEl.className = "pipeline-step step-running";
      stepEl.querySelector(".step-status").innerText = "⚙️";
    }
  }
}

function animateNumber(elementId, targetNumber, prefix = "", suffix = "") {
  const el = document.getElementById(elementId);
  if (!el) return;
  let start = 0;
  const duration = 400;
  const startTime = performance.now();

  function update(currentTime) {
    const elapsed = currentTime - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const current = Math.floor(progress * targetNumber);
    el.innerText = `${prefix}${current.toLocaleString('en-IN')}${suffix}`;
    if (progress < 1) {
      requestAnimationFrame(update);
    } else {
      el.innerText = `${prefix}${targetNumber.toLocaleString('en-IN')}${suffix}`;
    }
  }
  requestAnimationFrame(update);
}

function renderResults(data, lang) {
  // 1. Update Telemetry Steps
  const telemetry = data.telemetry || [];
  telemetry.forEach(step => {
    const stepEl = document.getElementById(`step-${step.step}`);
    if (stepEl) {
      stepEl.className = "pipeline-step step-completed";
      stepEl.querySelector(".step-status").innerText = "✅";
      stepEl.querySelector(".step-desc").innerText = `${step.duration_ms}ms • ${step.output_summary}`;
    }
  });

  // Step 5 check (Grievance)
  const step5 = document.getElementById("step-5");
  if (data.grievance) {
    step5.className = "pipeline-step step-completed";
    step5.querySelector(".step-status").innerText = "✅";
    step5.querySelector(".step-desc").innerText = `Drafted formal CPGRAMS petition for ${data.grievance.authority}`;
  } else {
    step5.className = "pipeline-step";
    step5.querySelector(".step-status").innerText = "—";
    step5.querySelector(".step-desc").innerText = "No delay detected. Grievance bypassed.";
  }

  // 2. Update Badges & Metrics Ribbon with animation
  document.getElementById("runtimeBadge").innerText = `Runtime: ${data.total_runtime_ms} ms`;
  document.getElementById("metricSpeed").innerText = `${data.total_runtime_ms} ms`;

  const evalData = data.evaluation;
  animateNumber("metricSchemes", evalData.qualified_count);
  animateNumber("metricBenefits", evalData.total_estimated_annual_benefit_inr, "₹");

  const gapData = data.gap_audit;
  animateNumber("metricReadiness", gapData.overall_document_readiness_score, "", "%");

  // 3. Update Bilingual Summary Box
  const isHindi = lang === "Hindi";
  const summaryBox = document.getElementById("summaryText");
  summaryBox.innerText = isHindi ? data.bilingual_response.hindi : data.bilingual_response.english;

  // 4. Render Schemes with Category Filter
  renderSchemes(evalData);

  // 5. Render Document Compliance Audit
  const docAuditList = document.getElementById("docAuditList");
  docAuditList.innerHTML = "";

  (data.profile.existing_documents || []).forEach(doc => {
    const item = document.createElement("div");
    item.className = "doc-item";
    item.innerHTML = `
      <span>${doc}</span>
      <span class="doc-status-ok">VERIFIED ✓</span>
    `;
    docAuditList.appendChild(item);
  });

  (gapData.remediation_actions || []).forEach(rem => {
    const item = document.createElement("div");
    item.className = "doc-item";
    item.innerHTML = `
      <div>
        <strong>${rem.document_name}</strong>
        <div style="font-size:11px;color:#64748B;">Portal: ${rem.guidance.online_portal} (${rem.guidance.typical_turnaround})</div>
      </div>
      <span class="doc-status-missing">MISSING ✗</span>
    `;
    docAuditList.appendChild(item);
  });

  // 6. Enable PDF Download Button
  const pdfBtn = document.getElementById("downloadPdfBtn");
  if (data.pdf_filename) {
    pdfBtn.disabled = false;
    pdfBtn.innerHTML = `<span>📥 Download Application PDF (${data.pdf_filename})</span>`;
  } else {
    pdfBtn.disabled = true;
  }

  // 7. Render Grievance Card if present
  const grievanceCard = document.getElementById("grievanceCard");
  if (data.grievance) {
    grievanceCard.style.display = "block";
    document.getElementById("grievanceTitle").innerText = data.grievance.petition_title;
    document.getElementById("grievanceSub").innerText = `Addressed to: ${data.grievance.authority}`;
    document.getElementById("grievanceText").innerText = data.grievance.petition_text;
  } else {
    grievanceCard.style.display = "none";
  }
}

function renderSchemes(evalData) {
  const schemesList = document.getElementById("schemesList");
  schemesList.innerHTML = "";

  const allQualified = evalData.qualified_schemes || [];
  const filtered = activeCategoryFilter === "all" 
    ? allQualified 
    : allQualified.filter(s => s.category.toLowerCase().includes(activeCategoryFilter.toLowerCase()));

  document.getElementById("schemesFoundLabel").innerText = `Showing ${filtered.length} of ${allQualified.length} certified schemes`;

  if (filtered.length === 0) {
    schemesList.innerHTML = `<div style="padding:20px; text-align:center; color:var(--text-muted);">No schemes found matching this category filter.</div>`;
    return;
  }

  filtered.forEach(scheme => {
    const card = document.createElement("div");
    card.className = "scheme-card";
    card.style.cursor = "pointer";
    card.title = "Click for deep dive & application guidelines";
    card.innerHTML = `
      <div class="scheme-top">
        <div>
          <div class="scheme-title">${scheme.scheme_name} 🔍</div>
          <div class="scheme-hindi-title">${scheme.hindi_name || ''} • <span style="color:#0066CC">${scheme.ministry}</span></div>
        </div>
        <div class="score-badge">Match: ${scheme.match_score}%</div>
      </div>
      <div class="scheme-benefit">💰 Benefit: ${scheme.benefit_summary.financial || 'Direct Entitlement / Cashless Service'}</div>
      <div class="scheme-trace"><strong>Agent Reasoning:</strong> ${scheme.reasoning_trace.join(" ")}</div>
      <div class="scheme-footer">
        <span>📑 Mandatory: ${scheme.mandatory_documents.slice(0, 3).join(", ")}</span>
        <span class="scheme-portal-link">View Details & Apply ↗</span>
      </div>
    `;

    card.addEventListener("click", () => {
      openSchemeDetailModal(scheme);
    });

    schemesList.appendChild(card);
  });
}

function openSchemeDetailModal(scheme) {
  const modal = document.getElementById("schemeDetailModal");
  document.getElementById("detailSchemeTitle").innerText = `${scheme.scheme_name} (${scheme.hindi_name || ''})`;

  const modalBody = document.getElementById("schemeModalBody");
  modalBody.innerHTML = `
    <div style="margin-bottom:14px;">
      <div style="font-size:12px; color:var(--text-muted); text-transform:uppercase; font-weight:700;">Nodal Authority & Ministry</div>
      <div style="font-size:14px; font-weight:600; color:var(--primary-navy);">${scheme.ministry}</div>
    </div>

    <div style="background:#F0FDF4; border:1px solid #BBF7D0; padding:12px; border-radius:8px; margin-bottom:14px;">
      <div style="font-size:12px; color:#15803D; font-weight:700;">DIRECT ENTITLEMENT BREAKDOWN</div>
      <div style="font-size:15px; font-weight:700; color:#166534; margin-top:2px;">${scheme.benefit_summary.financial || 'Government Subsidy / Cashless Hospitalization'}</div>
      <div style="font-size:12px; color:#374151; margin-top:4px;">Frequency: ${scheme.benefit_summary.frequency || 'Direct Benefit Transfer (DBT)'}</div>
    </div>

    <div style="margin-bottom:14px;">
      <div style="font-size:12px; color:var(--text-muted); text-transform:uppercase; font-weight:700; margin-bottom:6px;">Agent Verification Audit</div>
      <ul style="font-size:13px; color:var(--text-main); margin-left:18px; line-height:1.6;">
        ${scheme.reasoning_trace.map(r => `<li>${r}</li>`).join("")}
      </ul>
    </div>

    <div style="margin-bottom:16px;">
      <div style="font-size:12px; color:var(--text-muted); text-transform:uppercase; font-weight:700; margin-bottom:6px;">Required Submission Documents</div>
      <div style="display:flex; flex-wrap:wrap; gap:6px;">
        ${scheme.mandatory_documents.map(d => `<span class="tag" style="background:#EEF2F6;">${d}</span>`).join("")}
      </div>
    </div>

    <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid var(--border-color); padding-top:12px;">
      <span style="font-size:12px; color:var(--text-muted);">Appeal Officer: ${scheme.appeal_authority || 'District Collector'}</span>
      <a href="${scheme.nodal_portal}" target="_blank" class="launch-btn" style="text-decoration:none; padding:8px 16px; font-size:12px;">Visit Official Portal ↗</a>
    </div>
  `;

  modal.style.display = "flex";
}

function openTelemetryModal(stepNumber) {
  if (!currentRunResult) return;
  const modal = document.getElementById("telemetryModal");
  const telemetry = currentRunResult.telemetry || [];
  const stepData = telemetry.find(s => s.step === stepNumber);

  const modalTitle = document.getElementById("modalAgentName");
  const modalType = document.getElementById("modalAgentType");
  const modalLatency = document.getElementById("modalLatency");
  const modalStatus = document.getElementById("modalStatus");
  const modalTrace = document.getElementById("modalTraceContent");
  const modalJson = document.getElementById("modalJsonContent");

  if (stepData) {
    modalTitle.innerText = `Step ${stepData.step}: ${stepData.agent}`;
    modalType.innerText = stepData.agent;
    modalLatency.innerText = `${stepData.duration_ms} ms`;
    modalStatus.innerText = stepData.status;
    modalTrace.innerText = stepData.output_summary;
    
    let contextPayload = {};
    if (stepNumber === 1) contextPayload = currentRunResult.profile;
    else if (stepNumber === 2) contextPayload = currentRunResult.evaluation;
    else if (stepNumber === 3) contextPayload = currentRunResult.gap_audit;
    else if (stepNumber === 4) contextPayload = { pdf_file: currentRunResult.pdf_filename, path: currentRunResult.pdf_path };
    else if (stepNumber === 5) contextPayload = currentRunResult.grievance || { note: "Bypassed - No administrative delay detected." };

    modalJson.innerText = JSON.stringify({ telemetry_step: stepData, agent_output_payload: contextPayload }, null, 2);
  } else if (stepNumber === 5 && currentRunResult.grievance) {
    modalTitle.innerText = `Step 5: Grievance Redressal Agent`;
    modalType.innerText = "Grievance Redressal & Legal Drafting Agent";
    modalLatency.innerText = `12 ms`;
    modalStatus.innerText = "COMPLETED";
    modalTrace.innerText = "Statutory CPGRAMS petition drafted under Section 19 of Citizen Charter.";
    modalJson.innerText = JSON.stringify(currentRunResult.grievance, null, 2);
  } else {
    modalTitle.innerText = `Step ${stepNumber} Inspection`;
    modalType.innerText = "Specialized Sub-Agent";
    modalLatency.innerText = "0 ms";
    modalStatus.innerText = "BYPASS";
    modalTrace.innerText = "Step was not triggered in current execution path.";
    modalJson.innerText = JSON.stringify({ message: "No execution data" }, null, 2);
  }

  modal.style.display = "flex";
}
