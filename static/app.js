// Jan-Sahayak AI - Client-side Interactive Dashboard Controller

let activePersonaId = "rameshwar_farmer";
let currentRunResult = null;
let isSpeaking = false;

document.addEventListener("DOMContentLoaded", () => {
  setupEventListeners();
  // Auto-run baseline persona on initial load so the dashboard is immediately alive!
  runWorkflow({ persona_id: activePersonaId });
});

function setupEventListeners() {
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
  const copyBtn = document.getElementById("copyBtn") || document.getElementById("copyGrievanceBtn");
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

  // Text-to-Speech Button
  const speakBtn = document.getElementById("speakBtn");
  if (speakBtn) {
    speakBtn.addEventListener("click", () => {
      if (!('speechSynthesis' in window)) {
        alert("Audio synthesis is not supported on this browser.");
        return;
      }
      if (isSpeaking) {
        window.speechSynthesis.cancel();
        isSpeaking = false;
        speakBtn.innerText = "🔊 Listen in Hindi / English";
        return;
      }

      const summaryText = document.getElementById("summaryText").innerText;
      const utterance = new SpeechSynthesisUtterance(summaryText);
      const isHindi = document.getElementById("langSelect").value === "Hindi";
      utterance.lang = isHindi ? "hi-IN" : "en-IN";
      utterance.rate = 0.95;

      utterance.onend = () => {
        isSpeaking = false;
        speakBtn.innerText = "🔊 Listen in Hindi / English";
      };

      isSpeaking = true;
      speakBtn.innerText = "⏹️ Stop Audio";
      window.speechSynthesis.speak(utterance);
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
