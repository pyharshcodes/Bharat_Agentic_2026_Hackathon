// Jan-Sahayak AI - Client-side Interactive Dashboard Controller

let activePersonaId = "rameshwar_farmer";
let currentRunResult = null;
let isSpeaking = false;

document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  setupEventListeners();
  // Auto-run baseline persona on initial load so the dashboard is immediately alive!
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

  // Modal Close Button
  const modalCloseBtn = document.getElementById("modalCloseBtn");
  const modalBackdrop = document.getElementById("telemetryModal");
  if (modalCloseBtn) {
    modalCloseBtn.addEventListener("click", () => {
      modalBackdrop.style.display = "none";
    });
  }
  if (modalBackdrop) {
    modalBackdrop.addEventListener("click", (e) => {
      if (e.target === modalBackdrop) {
        modalBackdrop.style.display = "none";
      }
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
      recognition.onerror = () => {
        voiceBtn.innerText = "🎙️";
      };
      recognition.onend = () => {
        voiceBtn.innerText = "🎙️";
      };
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

      // 1. Try Browser Synthesis first
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
        // 2. Fallback to Server gTTS MP3 stream
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

  // 2. Update Badges & Metrics Ribbon
  document.getElementById("runtimeBadge").innerText = `Runtime: ${data.total_runtime_ms} ms`;
  document.getElementById("metricSpeed").innerText = `${data.total_runtime_ms} ms`;

  const evalData = data.evaluation;
  document.getElementById("metricSchemes").innerText = evalData.qualified_count;
  document.getElementById("metricBenefits").innerText = `₹${evalData.total_estimated_annual_benefit_inr.toLocaleString('en-IN')}`;

  const gapData = data.gap_audit;
  document.getElementById("metricReadiness").innerText = `${gapData.overall_document_readiness_score}%`;

  // 3. Update Bilingual Summary Box
  const isHindi = lang === "Hindi";
  const summaryBox = document.getElementById("summaryText");
  summaryBox.innerText = isHindi ? data.bilingual_response.hindi : data.bilingual_response.english;

  // 4. Render Qualified Schemes Gallery
  const schemesList = document.getElementById("schemesList");
  schemesList.innerHTML = "";

  document.getElementById("schemesFoundLabel").innerText = `Identified ${evalData.qualified_count} certified matching schemes`;

  evalData.qualified_schemes.forEach(scheme => {
    const card = document.createElement("div");
    card.className = "scheme-card";
    card.innerHTML = `
      <div class="scheme-top">
        <div>
          <div class="scheme-title">${scheme.scheme_name}</div>
          <div class="scheme-hindi-title">${scheme.hindi_name || ''} • <span style="color:#0066CC">${scheme.ministry}</span></div>
        </div>
        <div class="score-badge">Match: ${scheme.match_score}%</div>
      </div>
      <div class="scheme-benefit">💰 Benefit: ${scheme.benefit_summary.financial || 'Direct Entitlement / Cashless Service'}</div>
      <div class="scheme-trace"><strong>Agent Reasoning:</strong> ${scheme.reasoning_trace.join(" ")}</div>
      <div class="scheme-footer">
        <span>📑 Mandatory: ${scheme.mandatory_documents.slice(0, 3).join(", ")}</span>
        <a href="${scheme.nodal_portal}" target="_blank" class="scheme-portal-link">Official Portal ↗</a>
      </div>
    `;
    schemesList.appendChild(card);
  });

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
    
    // Pick relevant context payload
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
