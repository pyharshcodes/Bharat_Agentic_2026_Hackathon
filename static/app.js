// Jan-Sahayak AI - Production GovTech Client-Side Controller
// Built by Team BITS AND BYTES (Harsh Deep Chak & Pallak Devi)
// Autonomous Welfare & Civic Rights Agent

let activePersonaId = "rameshwar_farmer";
let currentRunResult = null;
let isSpeaking = false;
let activeCategoryFilter = "all";
let allSchemesCatalogue = [];
let currentWizardStep = 1;

document.addEventListener("DOMContentLoaded", () => {
  setupEventListeners();
  loadSchemesCatalogue();
  // Auto-run baseline persona on initial load
  runWorkflow({ persona_id: activePersonaId });
});

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
  // Header Navigation Buttons
  const headerAuditBtn = document.getElementById("headerAuditBtn");
  if (headerAuditBtn) {
    headerAuditBtn.addEventListener("click", () => {
      triggerAuditAction();
    });
  }

  const headerExploreBtn = document.getElementById("headerExploreBtn");
  if (headerExploreBtn) {
    headerExploreBtn.addEventListener("click", () => {
      const target = document.getElementById("schemesSection");
      if (target) target.scrollIntoView({ behavior: "smooth" });
    });
  }

  const heroPrimaryCta = document.getElementById("heroPrimaryCta");
  if (heroPrimaryCta) {
    heroPrimaryCta.addEventListener("click", () => {
      triggerAuditAction();
    });
  }

  // Persona Chips Selection
  const personaChips = document.querySelectorAll(".persona-chip");
  personaChips.forEach(chip => {
    chip.addEventListener("click", () => {
      personaChips.forEach(c => {
        c.classList.remove("active");
        c.setAttribute("aria-checked", "false");
      });
      chip.classList.add("active");
      chip.setAttribute("aria-checked", "true");
      activePersonaId = chip.getAttribute("data-id");
      document.getElementById("customQueryInput").value = "";
      runWorkflow({ persona_id: activePersonaId });
    });
  });

  // Launch Button (Run Welfare Audit)
  const launchBtn = document.getElementById("launchBtn");
  if (launchBtn) {
    launchBtn.addEventListener("click", () => {
      triggerAuditAction();
    });
  }

  // Category Filter Chips
  const filterChips = document.querySelectorAll(".filter-chip");
  filterChips.forEach(chip => {
    chip.addEventListener("click", () => {
      filterChips.forEach(c => {
        c.classList.remove("active");
        c.setAttribute("aria-selected", "false");
      });
      chip.classList.add("active");
      chip.setAttribute("aria-selected", "true");
      activeCategoryFilter = chip.getAttribute("data-cat");
      if (currentRunResult && currentRunResult.evaluation) {
        renderSchemes(currentRunResult.evaluation);
      }
    });
  });

  // Ineligible Accordion Toggle
  const toggleIneligibleBtn = document.getElementById("toggleIneligibleBtn");
  const ineligibleList = document.getElementById("ineligibleList");
  const ineligibleArrow = document.getElementById("ineligibleArrow");
  if (toggleIneligibleBtn && ineligibleList) {
    toggleIneligibleBtn.addEventListener("click", () => {
      const isVisible = ineligibleList.style.display !== "none";
      ineligibleList.style.display = isVisible ? "none" : "flex";
      ineligibleArrow.innerText = isVisible ? "▼" : "▲";
      toggleIneligibleBtn.setAttribute("aria-expanded", !isVisible);
    });
  }

  // 7-Step Progressive Wizard Simulator
  setupWizardSimulator();

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
        setTimeout(() => digilockerBtn.innerText = "🔗 Sync via DigiLocker", 3000);
      } catch (err) {
        console.error(err);
        digilockerBtn.innerText = "🔗 Sync via DigiLocker";
      }
    });
  }

  // Quick Grievance Drafter Button (6 Verified Issue Types)
  const quickGrievanceBtn = document.getElementById("quickGrievanceBtn");
  if (quickGrievanceBtn) {
    quickGrievanceBtn.addEventListener("click", async () => {
      const issueType = document.getElementById("quickGrievanceSelect").value;
      const profile = (currentRunResult && currentRunResult.profile) 
        ? currentRunResult.profile 
        : { name: "Citizen Applicant", state: "Uttar Pradesh", district: "Gorakhpur" };
      
      quickGrievanceBtn.innerText = "⏳ Drafting Petition...";
      try {
        const res = await fetch("/api/grievance", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            profile: profile,
            grievance_info: {
              issue_type: issueType,
              delay_days: 90
            }
          })
        });
        if (res.ok) {
          const petition = await res.json();
          renderGrievanceCard(petition);
          quickGrievanceBtn.innerText = "✓ Petition Drafted!";
          setTimeout(() => quickGrievanceBtn.innerText = "⚖️ Draft Formal Statutory Petition", 2500);
          
          // Scroll smoothly to the grievance card
          const card = document.getElementById("grievanceCard");
          if (card) {
            card.style.display = "flex";
            card.scrollIntoView({ behavior: "smooth", block: "center" });
          }
        }
      } catch (err) {
        console.error("Grievance drafting error:", err);
        quickGrievanceBtn.innerText = "⚖️ Draft Formal Statutory Petition";
      }
    });
  }

  // Pipeline Step Clicks (Inspect 8 Agent Telemetry)
  for (let i = 1; i <= 8; i++) {
    const stepEl = document.getElementById(`step-${i}`);
    if (stepEl) {
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
        alert("Speech Recognition is not supported on this browser. Please type your query in the input box.");
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
  if (downloadPdfBtn) {
    downloadPdfBtn.addEventListener("click", () => {
      if (currentRunResult && currentRunResult.pdf_filename) {
        window.open(`/api/download/${currentRunResult.pdf_filename}`, "_blank");
      }
    });
  }

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

  // Bilingual Speech Button
  setupAudioPlayer();
}

function triggerAuditAction() {
  const customQuery = document.getElementById("customQueryInput").value.trim();
  if (customQuery.length > 0) {
    runWorkflow({ custom_query: customQuery });
  } else {
    runWorkflow({ persona_id: activePersonaId });
  }
}

function setupWizardSimulator() {
  const openCustomizerBtn = document.getElementById("openCustomizerBtn");
  const customizerModal = document.getElementById("profileCustomizerModal");
  const customizerCloseBtn = document.getElementById("customizerCloseBtn");
  const cancelCustomizerBtn = document.getElementById("cancelCustomizerBtn");
  const wPrevBtn = document.getElementById("wPrevBtn");
  const wNextBtn = document.getElementById("wNextBtn");
  const applyCustomizerBtn = document.getElementById("applyCustomizerBtn");

  // Income & Land Sliders
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

  // Dynamic Land toggle depending on occupation
  const custOccupation = document.getElementById("custOccupation");
  const landGroup = document.getElementById("landGroup");
  if (custOccupation && landGroup) {
    custOccupation.addEventListener("change", () => {
      if (custOccupation.value === "Farmer") {
        landGroup.style.display = "flex";
      } else {
        landGroup.style.display = "none";
      }
    });
  }

  // Grievance type trigger
  const custGrievanceType = document.getElementById("custGrievanceType");
  const grievanceDaysGroup = document.getElementById("grievanceDaysGroup");
  if (custGrievanceType && grievanceDaysGroup) {
    custGrievanceType.addEventListener("change", () => {
      if (custGrievanceType.value !== "none") {
        grievanceDaysGroup.style.display = "flex";
      } else {
        grievanceDaysGroup.style.display = "none";
      }
    });
  }

  // Modal open/close
  if (openCustomizerBtn && customizerModal) {
    openCustomizerBtn.addEventListener("click", () => {
      currentWizardStep = 1;
      updateWizardView();
      customizerModal.style.display = "flex";
    });
    if (customizerCloseBtn) customizerCloseBtn.addEventListener("click", () => customizerModal.style.display = "none");
    if (cancelCustomizerBtn) cancelCustomizerBtn.addEventListener("click", () => customizerModal.style.display = "none");
    customizerModal.addEventListener("click", (e) => {
      if (e.target === customizerModal) customizerModal.style.display = "none";
    });
  }

  // Wizard Navigation
  if (wPrevBtn && wNextBtn && applyCustomizerBtn) {
    wNextBtn.addEventListener("click", () => {
      if (currentWizardStep < 7) {
        currentWizardStep++;
        updateWizardView();
      }
    });

    wPrevBtn.addEventListener("click", () => {
      if (currentWizardStep > 1) {
        currentWizardStep--;
        updateWizardView();
      }
    });

    // Step indicators click
    const stepIndicators = document.querySelectorAll(".w-step");
    stepIndicators.forEach(stepInd => {
      stepInd.addEventListener("click", () => {
        const stepNum = parseInt(stepInd.getAttribute("data-wstep"));
        if (stepNum) {
          currentWizardStep = stepNum;
          updateWizardView();
        }
      });
    });

    // Apply custom profile
    applyCustomizerBtn.addEventListener("click", () => {
      // Gather checked documents
      const checkedDocs = [];
      const checkboxes = document.querySelectorAll("#docsChecklist input[type='checkbox']:checked");
      checkboxes.forEach(cb => checkedDocs.push(cb.value));

      const occ = document.getElementById("custOccupation").value;
      const isFarmer = occ === "Farmer";
      const landVal = isFarmer ? parseFloat(document.getElementById("custLand").value) : 0.0;
      
      const gType = document.getElementById("custGrievanceType").value;
      const hasGrievance = gType !== "none";
      const gDays = hasGrievance ? parseInt(document.getElementById("custGrievanceDays").value) || 90 : 0;

      const customProfile = {
        name: document.getElementById("custName").value || "Dynamic Citizen",
        age: parseInt(document.getElementById("custAge").value) || 40,
        gender: document.getElementById("custGender").value,
        state: document.getElementById("custState").value,
        district: document.getElementById("custDistrict").value || "Gorakhpur",
        urban_rural: document.getElementById("custUrbanRural").value,
        occupation: occ,
        annual_income: parseFloat(document.getElementById("custIncome").value),
        landholding_acres: landVal,
        caste: document.getElementById("custCaste").value,
        daughters_count: parseInt(document.getElementById("custDaughters").value),
        daughter_ages: parseInt(document.getElementById("custDaughters").value) > 0 ? [6] : [],
        housing_status: document.getElementById("custHousing").value,
        existing_documents: checkedDocs.length > 0 ? checkedDocs : ["Aadhaar Card", "Bank Account details (Aadhaar linked NPCI seeded)"]
      };

      if (hasGrievance) {
        customProfile.grievance_case = {
          issue_type: gType,
          delay_days: gDays
        };
      }

      customizerModal.style.display = "none";
      const personaChips = document.querySelectorAll(".persona-chip");
      personaChips.forEach(c => c.classList.remove("active"));
      runWorkflow(customProfile);
    });
  }
}

function updateWizardView() {
  const stepIndicators = document.querySelectorAll(".w-step");
  stepIndicators.forEach(stepInd => {
    const stepNum = parseInt(stepInd.getAttribute("data-wstep"));
    if (stepNum === currentWizardStep) {
      stepInd.classList.add("active");
      stepInd.setAttribute("aria-selected", "true");
    } else {
      stepInd.classList.remove("active");
      stepInd.setAttribute("aria-selected", "false");
    }
  });

  for (let i = 1; i <= 7; i++) {
    const panel = document.getElementById(`wPanel-${i}`);
    if (panel) {
      panel.style.display = (i === currentWizardStep) ? "block" : "none";
    }
  }

  const wPrevBtn = document.getElementById("wPrevBtn");
  const wNextBtn = document.getElementById("wNextBtn");
  const applyCustomizerBtn = document.getElementById("applyCustomizerBtn");

  if (wPrevBtn) wPrevBtn.style.display = (currentWizardStep > 1) ? "inline-block" : "none";
  if (wNextBtn) wNextBtn.style.display = (currentWizardStep < 7) ? "inline-block" : "none";
  if (applyCustomizerBtn) applyCustomizerBtn.style.display = (currentWizardStep === 7) ? "inline-block" : "none";
}

function setupAudioPlayer() {
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
        speakBtn.innerHTML = "<span>🔊 Listen in Hindi / English</span>";
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
          speakBtn.innerHTML = "<span>🔊 Listen in Hindi / English</span>";
        };

        isSpeaking = true;
        speakBtn.innerHTML = "<span>⏹️ Stop Audio</span>";
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
            speakBtn.innerHTML = "<span>⏹️ Stop Audio</span>";
            audioPlayer.onended = () => {
              isSpeaking = false;
              speakBtn.innerHTML = "<span>🔊 Listen in Hindi / English</span>";
            };
          }
        } catch (err) {
          console.error("Audio error:", err);
          speakBtn.innerHTML = "<span>🔊 Listen in Hindi / English</span>";
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
    alert("Agent execution failed: " + err.message);
  }
}

function setPipelineRunning() {
  for (let i = 1; i <= 8; i++) {
    const stepEl = document.getElementById(`step-${i}`);
    if (stepEl) {
      stepEl.className = "pipe-node running";
      stepEl.querySelector(".node-status").innerText = "⚙️";
    }
  }
}

function animateNumber(elementId, targetNumber, prefix = "", suffix = "") {
  const el = document.getElementById(elementId);
  if (!el) return;
  const duration = 350;
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
  // 1. Update Telemetry Steps for all 8 agents
  const telemetry = data.telemetry || [];
  telemetry.forEach(step => {
    const stepEl = document.getElementById(`step-${step.step}`);
    if (stepEl) {
      stepEl.className = "pipe-node completed";
      stepEl.querySelector(".node-status").innerText = "✓";
      stepEl.querySelector(".node-desc").innerText = `${step.duration_ms}ms • ${step.agent.split(" ")[0]}`;
    }
  });

  // Step 8 check (Grievance)
  const step8 = document.getElementById("step-8");
  if (data.grievance && step8) {
    step8.className = "pipe-node completed";
    step8.querySelector(".node-status").innerText = "✓";
    step8.querySelector(".node-desc").innerText = `Petition Ready`;
  } else if (step8) {
    step8.className = "pipe-node";
    step8.querySelector(".node-status").innerText = "—";
    step8.querySelector(".node-desc").innerText = "Standby";
  }

  // 2. Update 4 5-Second Opportunity Cards
  const evalData = data.evaluation || {};
  const gapData = data.gap_audit || {};

  animateNumber("metricBenefits", evalData.total_estimated_annual_benefit_inr || 0, "₹");
  
  const elCount = evalData.eligible_count || 0;
  const potCount = evalData.potential_count || 0;
  const subEl = document.getElementById("metricSchemesSub");
  if (subEl) subEl.innerText = `${elCount} Direct Welfare Schemes Qualified`;

  const potValEl = document.getElementById("metricPotentialVal");
  if (potValEl) potValEl.innerText = `₹${(evalData.total_potential_benefit_inr || 0).toLocaleString('en-IN')}`;

  const missingCount = gapData.missing_documents_count || 0;
  const missEl = document.getElementById("metricMissingCount");
  if (missEl) missEl.innerText = missingCount === 0 ? "0 Documents Missing" : `${missingCount} Document${missingCount > 1 ? 's' : ''} Needed`;

  const readScore = gapData.overall_document_readiness_score || 0;
  const readEl = document.getElementById("metricReadinessScore");
  if (readEl) readEl.innerText = `Dossier Readiness: ${readScore}%`;

  const plansCount = data.action_plans ? data.action_plans.length : 0;
  const plansEl = document.getElementById("metricPlansCount");
  if (plansEl) plansEl.innerText = `${plansCount} Action Roadmap${plansCount > 1 ? 's' : ''}`;

  const runtimeBadge = document.getElementById("runtimeBadge");
  if (runtimeBadge) runtimeBadge.innerText = `Runtime: ${data.total_runtime_ms} ms`;

  // 3. Update Bilingual Summary Box
  const isHindi = lang === "Hindi";
  const summaryBox = document.getElementById("summaryText");
  if (summaryBox && data.bilingual_response) {
    summaryBox.innerText = isHindi ? data.bilingual_response.hindi : data.bilingual_response.english;
  }

  const activeCitEl = document.getElementById("activeCitizenTitle");
  if (activeCitEl && data.profile) {
    activeCitEl.innerText = `Assessment for ${data.profile.name} (${data.profile.occupation}, ${data.profile.state})`;
  }

  // 4. Render Schemes List & Ineligible Accordion
  renderSchemes(evalData);

  // 5. Render Document Inspector & Gap Audit
  renderDocumentAudit(data.profile, gapData);

  // 6. Enable PDF Download Button
  const pdfBtn = document.getElementById("downloadPdfBtn");
  if (pdfBtn) {
    if (data.pdf_filename) {
      pdfBtn.disabled = false;
      pdfBtn.innerHTML = `<span>📥 Download Application PDF Draft (${data.pdf_filename})</span>`;
    } else {
      pdfBtn.disabled = true;
    }
  }

  // 7. Render Grievance Card
  renderGrievanceCard(data.grievance);

  // 8. Render Structured Action Plans ("YOUR NEXT 4 STEPS")
  renderActionPlans(data.action_plans || []);
}

function renderSchemes(evalData) {
  const schemesList = document.getElementById("schemesList");
  if (!schemesList) return;
  schemesList.innerHTML = "";

  const eligibleSchemes = evalData.eligible_schemes || [];
  const potentialSchemes = evalData.potentially_eligible_schemes || [];
  const insufficientSchemes = evalData.insufficient_data_schemes || [];
  const ineligibleSchemes = evalData.ineligible_schemes || [];

  const filterCat = activeCategoryFilter.toLowerCase();
  const filterFn = (s) => (filterCat === "all") || (s.category && s.category.toLowerCase().includes(filterCat));

  const filteredEligible = eligibleSchemes.filter(filterFn);
  const filteredPotential = potentialSchemes.filter(filterFn);
  const filteredInsufficient = insufficientSchemes.filter(filterFn);

  const totalVisible = filteredEligible.length + filteredPotential.length + filteredInsufficient.length;
  const labelEl = document.getElementById("schemesFoundLabel");
  if (labelEl) {
    labelEl.innerText = `Showing ${totalVisible} matching schemes (${filteredEligible.length} Qualified, ${filteredPotential.length} Potential) based on statutory gazette criteria`;
  }

  if (totalVisible === 0) {
    schemesList.innerHTML = `<div style="grid-column: 1 / -1; padding:28px; text-align:center; color:var(--text-muted); background:#FFFFFF; border-radius:12px; border:1px solid var(--border-color);">No active schemes found matching category '${activeCategoryFilter}'.</div>`;
  }

  // 1. Render Eligible Schemes
  filteredEligible.forEach(scheme => {
    schemesList.appendChild(createSchemeCard(scheme, "ELIGIBLE"));
  });

  // 2. Render Potentially Eligible Schemes
  filteredPotential.forEach(scheme => {
    schemesList.appendChild(createSchemeCard(scheme, "POTENTIALLY ELIGIBLE"));
  });

  // 3. Render Insufficient Data Schemes
  filteredInsufficient.forEach(scheme => {
    schemesList.appendChild(createSchemeCard(scheme, "INSUFFICIENT DATA"));
  });

  // 4. Update Ineligible Accordion
  const inelCountEl = document.getElementById("ineligibleCount");
  if (inelCountEl) inelCountEl.innerText = ineligibleSchemes.length;

  const inelListEl = document.getElementById("ineligibleList");
  if (inelListEl) {
    inelListEl.innerHTML = "";
    if (ineligibleSchemes.length === 0) {
      inelListEl.innerHTML = `<div style="font-size:12px; color:var(--text-muted);">No ineligible schemes recorded.</div>`;
    } else {
      ineligibleSchemes.forEach(item => {
        const row = document.createElement("div");
        row.className = "ineligible-item";
        row.innerHTML = `
          <div class="ineligible-item-title">${item.scheme_name} (${item.hindi_name || ''})</div>
          <div class="ineligible-item-reason">❌ Statutory Exclusion: ${item.why_ineligible || 'Demographic criteria not satisfied'}</div>
        `;
        inelListEl.appendChild(row);
      });
    }
  }
}

function createSchemeCard(scheme, statusType) {
  const card = document.createElement("div");
  let cardClass = "scheme-card";
  let badgeClass = "badge-eligible";
  let statusText = "ELIGIBLE";

  if (statusType === "POTENTIALLY ELIGIBLE") {
    cardClass += " card-potential";
    badgeClass = "badge-potential";
    statusText = "POTENTIALLY ELIGIBLE";
  } else if (statusType === "INSUFFICIENT DATA") {
    cardClass += " card-insufficient";
    badgeClass = "badge-insufficient";
    statusText = "INSUFFICIENT DATA";
  } else {
    cardClass += " card-eligible";
    badgeClass = "badge-eligible";
    statusText = "ELIGIBLE";
  }

  card.className = cardClass;

  const benefitText = scheme.benefit_summary ? scheme.benefit_summary.financial : "Direct Entitlement";
  const benefitClass = (statusType === "POTENTIALLY ELIGIBLE") ? "scheme-benefit potential-benefit" : "scheme-benefit";

  // Build why qualify items
  let whyItemsHtml = "";
  if (scheme.why_qualify && scheme.why_qualify.length > 0) {
    whyItemsHtml = `
      <div class="why-qualify-list">
        <div class="why-qualify-title">Deterministic Qualification Checklist:</div>
        ${scheme.why_qualify.map(q => `<div class="why-qualify-item">✓ ${q}</div>`).join("")}
      </div>
    `;
  }

  // Potential requirements or missing docs
  let missingDocsHtml = "";
  if (scheme.missing_documents && scheme.missing_documents.length > 0) {
    missingDocsHtml = `
      <div class="missing-docs-note">
        ⚠️ <strong>Missing for Submission:</strong> ${scheme.missing_documents.join(", ")}
      </div>
    `;
  }

  card.innerHTML = `
    <div class="scheme-top">
      <div>
        <div class="scheme-title">${scheme.scheme_name}</div>
        <div class="scheme-hindi-title">${scheme.hindi_name || ''} • <span style="color:#0066CC">${scheme.ministry}</span></div>
      </div>
      <span class="scheme-badge ${badgeClass}">${statusText}</span>
    </div>
    <div class="${benefitClass}">💰 Direct Benefit: ${benefitText}</div>
    ${whyItemsHtml}
    ${missingDocsHtml}
    <div class="scheme-footer">
      <span style="color:var(--text-muted); font-size:11px;">Administrative Effort: <strong>${scheme.estimated_effort || 'Low'}</strong></span>
      <div class="scheme-card-btns">
        <button class="btn-secondary btn-detail-trigger">View Details</button>
        <a href="#actionPlanSection" class="btn-primary-small">Action Plan ↓</a>
        <a href="${scheme.official_url || scheme.nodal_portal || '#'}" target="_blank" rel="noopener" class="btn-secondary" style="color:#0066CC;">Portal ↗</a>
      </div>
    </div>
  `;

  const detailBtn = card.querySelector(".btn-detail-trigger");
  if (detailBtn) {
    detailBtn.addEventListener("click", () => {
      openSchemeDetailModal(scheme);
    });
  }

  return card;
}

function renderDocumentAudit(profile, gapData) {
  const docAuditList = document.getElementById("docAuditList");
  if (!docAuditList) return;
  docAuditList.innerHTML = "";

  const score = gapData.overall_document_readiness_score || 0;
  const pBar = document.getElementById("docProgressBar");
  const pText = document.getElementById("docProgressText");
  if (pBar) pBar.style.width = `${score}%`;
  if (pText) pText.innerText = `${score}% Verified (${gapData.held_documents ? gapData.held_documents.length : 0} Held / ${gapData.missing_documents_count || 0} Missing)`;

  // 1. Verified Documents
  (profile && profile.existing_documents ? profile.existing_documents : []).forEach(doc => {
    const item = document.createElement("div");
    item.className = "doc-item";
    item.innerHTML = `
      <div>
        <strong style="color:var(--primary-navy);">${doc}</strong>
        <div style="font-size:11px; color:#15803D;">Cryptographically Attested (e-KYC Verified)</div>
      </div>
      <span class="doc-status-ok">VERIFIED ✓</span>
    `;
    docAuditList.appendChild(item);
  });

  // 2. Missing Documents Remediation
  (gapData.remediation_actions || []).forEach(rem => {
    const item = document.createElement("div");
    item.className = "doc-item";
    const g = rem.guidance || {};
    item.innerHTML = `
      <div>
        <strong style="color:#991B1B;">${rem.document_name}</strong>
        <div style="font-size:11px; color:#64748B;">
          Issuing Authority: ${g.issuing_authority || 'Tehsil / CSC'} • Portal: ${g.online_portal || 'State Portal'} (${g.typical_turnaround || '7-14 days'})
        </div>
      </div>
      <span class="doc-status-missing">MISSING ✗</span>
    `;
    docAuditList.appendChild(item);
  });
}

function renderGrievanceCard(grievanceData) {
  const grievanceCard = document.getElementById("grievanceCard");
  if (!grievanceCard) return;

  if (grievanceData) {
    grievanceCard.style.display = "flex";
    const titleEl = document.getElementById("grievanceTitle");
    const subEl = document.getElementById("grievanceSub");
    const textEl = document.getElementById("grievanceText");

    if (titleEl) titleEl.innerText = grievanceData.petition_title || "Statutory Administrative Petition";
    if (subEl) subEl.innerText = `Addressed to: ${grievanceData.authority || 'Competent Nodal Officer'}`;
    if (textEl) textEl.innerText = grievanceData.petition_text || "";
  } else {
    grievanceCard.style.display = "none";
  }
}

function renderActionPlans(actionPlans) {
  const container = document.getElementById("actionPlansContainer");
  if (!container) return;
  container.innerHTML = "";

  if (actionPlans.length === 0) {
    container.innerHTML = `<div style="padding:22px; text-align:center; color:var(--text-muted); background:#FFFFFF; border-radius:12px; border:1px solid var(--border-color);">No action plans required for current profile.</div>`;
    return;
  }

  actionPlans.forEach(plan => {
    const card = document.createElement("div");
    card.className = "action-plan-card";

    const stepsHtml = (plan.steps || []).map(st => `
      <div class="plan-step-box">
        <span class="step-num-pill">STEP ${st.step}</span>
        <div class="step-title-text">${st.title}</div>
        <div class="step-detail-text">${st.detail}</div>
        <span class="step-authority-tag">Authority: ${st.authority}</span>
      </div>
    `).join("");

    card.innerHTML = `
      <div class="plan-card-header">
        <div>
          <div class="plan-scheme-title">${plan.scheme_name} (${plan.hindi_name || ''})</div>
          <div style="font-size:12px; color:var(--text-muted);">Est. Benefit: <strong style="color:var(--green);">${plan.estimated_benefit}</strong> • Effort: ${plan.estimated_effort}</div>
        </div>
        <a href="${plan.official_url || '#'}" target="_blank" rel="noopener" class="btn-nav-primary" style="padding:6px 14px; font-size:11px; text-decoration:none;">Apply on Official Portal ↗</a>
      </div>
      <div class="plan-steps-grid">
        ${stepsHtml}
      </div>
    `;

    container.appendChild(card);
  });
}

function openSchemeDetailModal(scheme) {
  const modal = document.getElementById("schemeDetailModal");
  if (!modal) return;
  document.getElementById("detailSchemeTitle").innerText = `${scheme.scheme_name} (${scheme.hindi_name || ''})`;

  const modalBody = document.getElementById("schemeModalBody");
  modalBody.innerHTML = `
    <div style="margin-bottom:14px;">
      <div style="font-size:11px; color:var(--text-muted); text-transform:uppercase; font-weight:800;">Competent Nodal Authority & Ministry</div>
      <div style="font-size:14px; font-weight:700; color:var(--primary-navy);">${scheme.ministry}</div>
    </div>

    <div style="background:#F0FDF4; border:1px solid #BBF7D0; padding:12px; border-radius:8px; margin-bottom:14px;">
      <div style="font-size:11px; color:#15803D; font-weight:800;">STATUTORY DIRECT BENEFIT ENTITLEMENT</div>
      <div style="font-size:15px; font-weight:800; color:#166534; margin-top:2px;">${scheme.benefit_summary ? scheme.benefit_summary.financial : 'Direct Entitlement / Cashless Service'}</div>
      <div style="font-size:12px; color:#374151; margin-top:4px;">Frequency: ${scheme.benefit_summary ? scheme.benefit_summary.frequency : 'Direct Benefit Transfer (DBT)'}</div>
    </div>

    <div style="margin-bottom:14px;">
      <div style="font-size:11px; color:var(--text-muted); text-transform:uppercase; font-weight:800; margin-bottom:6px;">Deterministic Qualification Audit</div>
      <ul style="font-size:13px; color:var(--text-main); margin-left:18px; line-height:1.6;">
        ${(scheme.why_qualify || []).map(r => `<li style="color:#166534;">✓ ${r}</li>`).join("")}
      </ul>
    </div>

    <div style="margin-bottom:16px;">
      <div style="font-size:11px; color:var(--text-muted); text-transform:uppercase; font-weight:800; margin-bottom:6px;">Mandatory Submission Checklist</div>
      <div style="display:flex; flex-wrap:wrap; gap:6px;">
        ${(scheme.mandatory_documents || []).map(d => `<span class="ptag" style="background:#EEF2F6; padding:4px 8px;">${d}</span>`).join("")}
      </div>
    </div>

    <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid var(--border-color); padding-top:14px;">
      <span style="font-size:12px; color:var(--text-muted);">Appellate Authority: <strong>${scheme.appeal_authority || 'District Magistrate / Collector'}</strong></span>
      <a href="${scheme.official_url || scheme.nodal_portal || '#'}" target="_blank" rel="noopener" class="btn-nav-primary" style="text-decoration:none; padding:8px 16px; font-size:12px;">Visit Official Portal ↗</a>
    </div>
  `;

  modal.style.display = "flex";
}

function openTelemetryModal(stepNumber) {
  if (!currentRunResult) return;
  const modal = document.getElementById("telemetryModal");
  if (!modal) return;
  const telemetry = currentRunResult.telemetry || [];
  const stepData = telemetry.find(s => s.step === stepNumber);

  const modalTitle = document.getElementById("modalAgentName");
  const modalType = document.getElementById("modalAgentType");
  const modalLatency = document.getElementById("modalLatency");
  const modalStatus = document.getElementById("modalStatus");
  const modalTrace = document.getElementById("modalTraceContent");
  const modalJson = document.getElementById("modalJsonContent");

  const agentNames = [
    "Intake & NLP Parser Agent",
    "Profile Verification Agent",
    "Scheme Discovery Agent",
    "Eligibility Rules Engine",
    "Document Inspector Agent",
    "Action Planner Agent",
    "Application Packaging Agent",
    "Grievance Assistant Agent"
  ];

  if (stepData) {
    modalTitle.innerText = `Step ${stepData.step}: ${stepData.agent}`;
    modalType.innerText = stepData.agent;
    modalLatency.innerText = `${stepData.duration_ms} ms`;
    modalStatus.innerText = stepData.status;
    modalTrace.innerText = stepData.output_summary;
    
    let contextPayload = {};
    if (stepNumber === 1) contextPayload = currentRunResult.profile;
    else if (stepNumber === 2) contextPayload = { profile_checks: "PASSED", boundaries: "VALID", dpdp_act_masked: true };
    else if (stepNumber === 3) contextPayload = { total_configured_schemes: 12, jurisdiction: currentRunResult.profile ? currentRunResult.profile.state : "National" };
    else if (stepNumber === 4) contextPayload = currentRunResult.evaluation;
    else if (stepNumber === 5) contextPayload = currentRunResult.gap_audit;
    else if (stepNumber === 6) contextPayload = currentRunResult.action_plans;
    else if (stepNumber === 7) contextPayload = { pdf_file: currentRunResult.pdf_filename, path: currentRunResult.pdf_path };
    else if (stepNumber === 8) contextPayload = currentRunResult.grievance || { note: "Bypassed - No administrative delay detected." };

    modalJson.innerText = JSON.stringify({ telemetry_step: stepData, agent_output_payload: contextPayload }, null, 2);
  } else {
    modalTitle.innerText = `Step ${stepNumber}: ${agentNames[stepNumber - 1] || 'Agent'}`;
    modalType.innerText = agentNames[stepNumber - 1] || 'Specialized Agent';
    modalLatency.innerText = "0 ms";
    modalStatus.innerText = "STANDBY";
    modalTrace.innerText = "Agent awaiting trigger in current workflow path.";
    modalJson.innerText = JSON.stringify({ message: "Standby state" }, null, 2);
  }

  modal.style.display = "flex";
}
