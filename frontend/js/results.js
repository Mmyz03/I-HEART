/**
 * AI Health Risk Prediction System - Results Dashboard Logic
 * Parses stored session analysis, renders patient summary, dual risk cards,
 * animated gauge progress meters, detailed human-understandable Explainable AI (XAI)
 * factor breakdowns, dynamic clinical synthesis, and handles assessment navigation.
 */

document.addEventListener('DOMContentLoaded', () => {
  renderResults();
  initActionButtons();
});

/**
 * Main Results Renderer
 */
function renderResults() {
  const contentWrapper = document.getElementById('results-content-wrapper');
  const noDataCard = document.getElementById('no-data-card');

  const rawData = sessionStorage.getItem('current_health_analysis');

  if (!rawData) {
    if (contentWrapper) contentWrapper.style.display = 'none';
    if (noDataCard) noDataCard.style.display = 'block';
    return;
  }

  try {
    const analysis = JSON.parse(rawData);
    const patient = analysis.patient;
    const predictions = analysis.predictions;

    if (!patient || !predictions) {
      throw new Error('Invalid analysis payload structure');
    }

    if (contentWrapper) contentWrapper.style.display = 'block';
    if (noDataCard) noDataCard.style.display = 'none';

    // 1. Populate Patient Summary
    const patientIdElem = document.getElementById('res-patient-id');
    if (patientIdElem) patientIdElem.textContent = patient.patient_id || 'PAT-DEMO';

    const ageElem = document.getElementById('res-age');
    if (ageElem) ageElem.textContent = `${patient.demographics.age} yrs`;

    const genderElem = document.getElementById('res-gender');
    if (genderElem) genderElem.textContent = patient.demographics.gender;

    const bmiElem = document.getElementById('res-bmi');
    if (bmiElem) bmiElem.textContent = `${patient.physical.bmi.toFixed(1)} kg/m²`;

    const bpElem = document.getElementById('res-bp');
    if (bpElem) bpElem.textContent = `${patient.vitals.systolic_bp}/${patient.vitals.diastolic_bp} mmHg`;

    const hrElem = document.getElementById('res-hr');
    if (hrElem) hrElem.textContent = `${patient.vitals.heart_rate} bpm`;

    const glucoseElem = document.getElementById('res-glucose');
    if (glucoseElem) glucoseElem.textContent = `${patient.laboratory.glucose} mg/dL`;

    // 2. Render Diabetes Risk Card
    renderRiskCard(
      predictions.diabetes,
      'res-diabetes-pct',
      'bar-diabetes-fill',
      'badge-diabetes-level',
      'res-diabetes-note',
      'list-diabetes-factors'
    );

    // 3. Render Cardiovascular Risk Card
    renderRiskCard(
      predictions.cardiovascular,
      'res-cvd-pct',
      'bar-cvd-fill',
      'badge-cvd-level',
      'res-cvd-note',
      'list-cvd-factors'
    );

    // 4. Render Deep-Dive Explainable AI (XAI) Clinical Section
    renderExplainableAI(analysis);

    // 5. Initialize scroll reveal on newly shown elements
    if (window.initScrollReveal) {
      window.initScrollReveal();
    }
  } catch (err) {
    console.error('Error rendering results:', err);
    if (contentWrapper) contentWrapper.style.display = 'none';
    if (noDataCard) noDataCard.style.display = 'block';
  }
}

/**
 * Helper to render individual disease risk card (compact overview)
 */
function renderRiskCard(diseaseData, pctElemId, barElemId, badgeElemId, noteElemId, listElemId) {
  const pctElem = document.getElementById(pctElemId);
  const barElem = document.getElementById(barElemId);
  const badgeElem = document.getElementById(badgeElemId);
  const noteElem = document.getElementById(noteElemId);
  const listElem = document.getElementById(listElemId);

  if (!diseaseData) return;

  const pct = diseaseData.risk_percentage || 0;
  const level = diseaseData.risk_level || 'Moderate';

  // Set Percentage & Animate Progress Bar
  if (pctElem) pctElem.textContent = `${pct}%`;

  if (barElem) {
    setTimeout(() => {
      barElem.style.width = `${pct}%`;
    }, 100);
  }

  // Set Badge & Colors
  if (badgeElem) {
    badgeElem.textContent = `${level} Risk`;
    badgeElem.className = 'risk-level-badge';

    if (level === 'High') {
      badgeElem.classList.add('level-high');
      if (barElem) barElem.classList.add('bar-high');
    } else if (level === 'Moderate') {
      badgeElem.classList.add('level-moderate');
      if (barElem) barElem.classList.add('bar-moderate');
    } else {
      badgeElem.classList.add('level-low');
      if (barElem) barElem.classList.add('bar-low');
    }
  }

  // Set Summary Note
  if (noteElem) {
    noteElem.textContent = diseaseData.summary_note || 'Calculated based on clinical factor evaluation.';
  }

  // Render Contributing Factors List
  if (listElem) {
    listElem.innerHTML = '';
    const factors = diseaseData.contributing_factors || [];

    if (factors.length === 0) {
      const li = document.createElement('li');
      li.textContent = 'All evaluated clinical parameters within standard baselines.';
      listElem.appendChild(li);
    } else {
      factors.forEach((factor) => {
        const li = document.createElement('li');
        li.textContent = factor;
        listElem.appendChild(li);
      });
    }
  }
}

/**
 * Render Human-Understandable Explainable AI (XAI) Section
 */
function renderExplainableAI(analysis) {
  const fallbackAlert = document.getElementById('xai-fallback-alert');
  const panelsContainer = document.getElementById('xai-panels-container');
  const synthesisContainer = document.getElementById('xai-synthesis-container');
  const synthesisText = document.getElementById('xai-synthesis-text');

  const cardsDiabPrimary = document.getElementById('cards-diabetes-primary');
  const cardsDiabSecondary = document.getElementById('cards-diabetes-secondary');
  const groupDiabSecondary = document.getElementById('group-diabetes-secondary');

  const cardsCvdPrimary = document.getElementById('cards-cvd-primary');
  const cardsCvdSecondary = document.getElementById('cards-cvd-secondary');
  const groupCvdSecondary = document.getElementById('group-cvd-secondary');

  try {
    const patient = analysis.patient;
    const predictions = analysis.predictions;

    if (!patient || !predictions) {
      triggerXaiFallback(fallbackAlert, panelsContainer, synthesisContainer);
      return;
    }

    const diabFactorsRaw = predictions.diabetes?.contributing_factors || [];
    const cvdFactorsRaw = predictions.cardiovascular?.contributing_factors || [];

    // Check if both pipelines returned fallback notice or empty factors
    const isDiabUnavailable = diabFactorsRaw.length === 0 || diabFactorsRaw.some(f => f.toLowerCase().includes('temporarily unavailable'));
    const isCvdUnavailable = cvdFactorsRaw.length === 0 || cvdFactorsRaw.some(f => f.toLowerCase().includes('temporarily unavailable'));

    if (isDiabUnavailable && isCvdUnavailable) {
      triggerXaiFallback(fallbackAlert, panelsContainer, synthesisContainer);
      return;
    }

    // Reset fallback alert if at least one pipeline has factors
    if (fallbackAlert) fallbackAlert.style.display = 'none';
    if (panelsContainer) panelsContainer.style.display = 'grid';
    if (synthesisContainer) synthesisContainer.style.display = 'block';

    // Parse Diabetes factors
    const parsedDiab = parseDiseaseFactors(diabFactorsRaw, patient, 'diabetes');
    // Parse CVD factors
    const parsedCvd = parseDiseaseFactors(cvdFactorsRaw, patient, 'cvd');

    // Populate Diabetes Factor Cards
    renderDiseaseFactorCards(
      parsedDiab,
      cardsDiabPrimary,
      cardsDiabSecondary,
      groupDiabSecondary,
      isDiabUnavailable,
      'Type 2 Diabetes'
    );

    // Populate CVD Factor Cards
    renderDiseaseFactorCards(
      parsedCvd,
      cardsCvdPrimary,
      cardsCvdSecondary,
      groupCvdSecondary,
      isCvdUnavailable,
      'Cardiovascular Disease'
    );

    // Dynamic "What this means" Synthesis Narrative
    if (synthesisText) {
      synthesisText.textContent = generateClinicalSynthesis(parsedDiab, parsedCvd, patient);
    }

  } catch (err) {
    console.error('Error rendering Explainable AI section:', err);
    triggerXaiFallback(fallbackAlert, panelsContainer, synthesisContainer);
  }
}

/**
 * Display graceful fallback message if detailed attribution is unavailable
 */
function triggerXaiFallback(fallbackAlert, panelsContainer, synthesisContainer) {
  if (fallbackAlert) {
    fallbackAlert.style.display = 'flex';
  }
  if (panelsContainer) {
    panelsContainer.style.display = 'none';
  }
  if (synthesisContainer) {
    synthesisContainer.style.display = 'none';
  }
}

/**
 * Parses raw rule-based factor strings into structured, human-understandable clinical objects
 */
function parseDiseaseFactors(rawFactors, patient, diseaseType) {
  const result = [];
  let indexCounter = 1;

  for (const factorStr of rawFactors) {
    if (factorStr.toLowerCase().includes('temporarily unavailable')) {
      continue;
    }

    let item = null;
    if (diseaseType === 'diabetes') {
      item = parseSingleDiabetesFactor(factorStr, patient);
    } else {
      item = parseSingleCvdFactor(factorStr, patient);
    }

    if (item) {
      item.index = indexCounter++;
      result.push(item);
    }
  }

  return result;
}

/**
 * Clinical Parser for Diabetes Factors
 */
function parseSingleDiabetesFactor(str, patient) {
  const lower = str.toLowerCase();

  // 1. Fasting Blood Glucose
  if (lower.includes('glucose')) {
    const val = patient.laboratory?.glucose != null ? patient.laboratory.glucose : '--';
    const isElevated = lower.includes('elevated');
    const isPrediabetic = lower.includes('pre-diabetic') || lower.includes('prediabetic');

    if (isElevated) {
      return {
        name: 'Fasting Blood Glucose',
        value: val,
        unit: 'mg/dL',
        referenceRange: '70–99 mg/dL',
        status: 'Elevated',
        statusClass: 'badge-elevated',
        contributionText: 'Higher-risk contribution',
        contributionClass: 'badge-higher',
        priority: 'primary',
        whyItMatters: `Your fasting blood glucose is ${val} mg/dL, which is above the reference range used by this assessment (70–99 mg/dL). Elevated glucose levels are associated with increased diabetes risk, making this an important factor in your current assessment.`
      };
    } else if (isPrediabetic) {
      return {
        name: 'Fasting Blood Glucose',
        value: val,
        unit: 'mg/dL',
        referenceRange: '70–99 mg/dL (Pre-diabetes: 100–125)',
        status: 'Elevated',
        statusClass: 'badge-elevated',
        contributionText: 'Higher-risk contribution',
        contributionClass: 'badge-higher',
        priority: 'primary',
        whyItMatters: `Your fasting blood glucose is ${val} mg/dL, which falls within the pre-diabetic reference range (100–125 mg/dL). Blood glucose in this range is associated with increased diabetes risk and contributes to your current assessment.`
      };
    } else {
      return {
        name: 'Fasting Blood Glucose',
        value: val,
        unit: 'mg/dL',
        referenceRange: '70–99 mg/dL',
        status: 'Normal',
        statusClass: 'badge-normal',
        contributionText: 'Lower-risk contribution',
        contributionClass: 'badge-lower',
        priority: 'primary',
        whyItMatters: `Your fasting blood glucose is ${val} mg/dL, which is within the optimal reference range (70–99 mg/dL). Normal glucose levels are associated with healthy metabolic function and support a lower assessed risk.`
      };
    }
  }

  // 2. HbA1c
  if (lower.includes('hba1c')) {
    const val = patient.laboratory?.hba1c != null ? patient.laboratory.hba1c : 5.5;
    const isDiabeticRange = lower.includes('diabetic range');

    if (isDiabeticRange) {
      return {
        name: 'Glycated Hemoglobin (HbA1c)',
        value: val,
        unit: '%',
        referenceRange: '< 5.7%',
        status: 'Elevated',
        statusClass: 'badge-elevated',
        contributionText: 'Higher-risk contribution',
        contributionClass: 'badge-higher',
        priority: 'primary',
        whyItMatters: `Your HbA1c is ${val}%, which exceeds the standard clinical reference limit (< 5.7%). HbA1c reflects average blood sugar control over the past 2–3 months, and elevated levels are associated with higher diabetes risk.`
      };
    } else {
      return {
        name: 'Glycated Hemoglobin (HbA1c)',
        value: val,
        unit: '%',
        referenceRange: '< 5.7% (Pre-diabetes: 5.7–6.4%)',
        status: 'Elevated',
        statusClass: 'badge-elevated',
        contributionText: 'Higher-risk contribution',
        contributionClass: 'badge-higher',
        priority: 'primary',
        whyItMatters: `Your HbA1c is ${val}%, which falls into the pre-diabetic reference range (5.7–6.4%). This intermediate indicator of average blood sugar is associated with increased diabetes risk and was identified as a contributing factor.`
      };
    }
  }

  // 3. Body Mass Index (BMI)
  if (lower.includes('body mass index') || lower.includes('bmi')) {
    const val = patient.physical?.bmi ? patient.physical.bmi.toFixed(1) : '--';
    const isObese = lower.includes('obese');

    if (isObese) {
      return {
        name: 'Body Mass Index (BMI)',
        value: val,
        unit: 'kg/m²',
        referenceRange: '18.5–24.9 kg/m²',
        status: 'Elevated',
        statusClass: 'badge-elevated',
        contributionText: 'Higher-risk contribution',
        contributionClass: 'badge-higher',
        priority: 'primary',
        whyItMatters: `Your BMI is ${val} kg/m², which is above the healthy weight reference range (18.5–24.9 kg/m²). Higher body mass can increase insulin resistance, which is associated with increased diabetes risk in metabolic evaluations.`
      };
    } else {
      return {
        name: 'Body Mass Index (BMI)',
        value: val,
        unit: 'kg/m²',
        referenceRange: '18.5–24.9 kg/m²',
        status: 'Elevated',
        statusClass: 'badge-elevated',
        contributionText: 'Higher-risk contribution',
        contributionClass: 'badge-higher',
        priority: 'primary',
        whyItMatters: `Your BMI is ${val} kg/m², placing it in the overweight reference range (25.0–29.9 kg/m²). Excess body mass may influence metabolic regulation and was identified as a contributing factor in your assessment.`
      };
    }
  }

  // 4. Age Demographic
  if (lower.includes('age')) {
    const val = patient.demographics?.age != null ? patient.demographics.age : '--';
    return {
      name: 'Age Demographic',
      value: val,
      unit: 'years',
      referenceRange: '< 45 years',
      status: 'Relevant',
      statusClass: 'badge-relevant',
      contributionText: 'Relevant factor',
      contributionClass: 'badge-relevant',
      priority: 'secondary',
      whyItMatters: `You are ${val} years of age. Natural age-related metabolic shifts are epidemiologically associated with gradual changes in glucose handling, making age an established demographic factor considered in your risk evaluation.`
    };
  }

  // 5. Hypertension Comorbidity
  if (lower.includes('hypertension')) {
    return {
      name: 'Hypertension Comorbidity',
      value: 'Diagnosed',
      unit: '',
      referenceRange: 'No clinical hypertension',
      status: 'Relevant',
      statusClass: 'badge-relevant',
      contributionText: 'Higher-risk contribution',
      contributionClass: 'badge-higher',
      priority: 'secondary',
      whyItMatters: 'A diagnosed history of hypertension is a recognized comorbidity that frequently co-occurs with vascular resistance and metabolic strain, contributing to your overall diabetes risk assessment.'
    };
  }

  // 6. Family History of Diabetes
  if (lower.includes('family history')) {
    return {
      name: 'Family History of Diabetes',
      value: 'Documented',
      unit: '',
      referenceRange: 'No family history',
      status: 'Relevant',
      statusClass: 'badge-relevant',
      contributionText: 'Higher-risk contribution',
      contributionClass: 'badge-higher',
      priority: 'secondary',
      whyItMatters: 'A documented family history of diabetes reflects shared genetic and environmental factors that are associated with higher susceptibility to metabolic dysregulation.'
    };
  }

  // Fallback for any other valid diabetes factor string
  return {
    name: 'Metabolic Factor',
    value: 'Present',
    unit: '',
    referenceRange: 'Clinical normative limit',
    status: 'Relevant',
    statusClass: 'badge-relevant',
    contributionText: 'Relevant factor',
    contributionClass: 'badge-relevant',
    priority: 'secondary',
    whyItMatters: `${str}. This factor was identified by clinical evaluation rules as a relevant parameter influencing your assessed diabetes risk.`
  };
}

/**
 * Clinical Parser for Cardiovascular Disease Factors
 */
function parseSingleCvdFactor(str, patient) {
  const lower = str.toLowerCase();

  // 1. Resting Blood Pressure
  if (lower.includes('hypertension') || lower.includes('blood pressure')) {
    const sbp = patient.vitals?.systolic_bp != null ? patient.vitals.systolic_bp : '--';
    const dbp = patient.vitals?.diastolic_bp != null ? patient.vitals.diastolic_bp : '--';
    const bpVal = `${sbp}/${dbp}`;
    const isStage2 = lower.includes('stage 2');
    const isStage1 = lower.includes('stage 1');

    if (isStage2) {
      return {
        name: 'Resting Blood Pressure',
        value: bpVal,
        unit: 'mmHg',
        referenceRange: '< 120/80 mmHg',
        status: 'Elevated',
        statusClass: 'badge-elevated',
        contributionText: 'Higher-risk contribution',
        contributionClass: 'badge-higher',
        priority: 'primary',
        whyItMatters: `Your blood pressure is ${bpVal} mmHg, which is above the standard clinical reference threshold (< 120/80 mmHg). Sustained high arterial pressure places mechanical workload on the vascular system and is associated with increased cardiovascular risk.`
      };
    } else if (isStage1) {
      return {
        name: 'Resting Blood Pressure',
        value: bpVal,
        unit: 'mmHg',
        referenceRange: '< 120/80 mmHg',
        status: 'Elevated',
        statusClass: 'badge-elevated',
        contributionText: 'Higher-risk contribution',
        contributionClass: 'badge-higher',
        priority: 'primary',
        whyItMatters: `Your blood pressure is ${bpVal} mmHg, which is above the optimal resting reference range (< 120/80 mmHg). Mildly elevated blood pressure is associated with increased vascular stress and contributes to your assessed risk.`
      };
    } else {
      return {
        name: 'Resting Blood Pressure',
        value: bpVal,
        unit: 'mmHg',
        referenceRange: '< 120/80 mmHg',
        status: 'Normal',
        statusClass: 'badge-normal',
        contributionText: 'Lower-risk contribution',
        contributionClass: 'badge-lower',
        priority: 'primary',
        whyItMatters: `Your resting blood pressure is ${bpVal} mmHg, which aligns with normative clinical baseline levels (< 120/80 mmHg). Healthy resting blood pressure reduces arterial strain and supports a lower assessed cardiovascular risk.`
      };
    }
  }

  // 2. Active Tobacco Smoking
  if (lower.includes('smoking') || lower.includes('tobacco')) {
    const val = patient.lifestyle?.smoking ? `${patient.lifestyle.smoking} Smoker` : 'Active Smoker';
    return {
      name: 'Tobacco Smoking Status',
      value: val,
      unit: '',
      referenceRange: 'Non-smoker / Never',
      status: 'Elevated',
      statusClass: 'badge-elevated',
      contributionText: 'Higher-risk contribution',
      contributionClass: 'badge-higher',
      priority: 'primary',
      whyItMatters: 'Active tobacco smoking is associated with vascular inflammation, accelerated plaque formation, and reduced arterial elasticity, making it a critical contributor to your cardiovascular risk assessment.'
    };
  }

  // 3. Total Serum Cholesterol
  if (lower.includes('cholesterol')) {
    const val = patient.laboratory?.total_cholesterol != null ? Math.round(patient.laboratory.total_cholesterol) : '--';
    const isHigh = lower.includes('high');

    if (isHigh) {
      return {
        name: 'Total Serum Cholesterol',
        value: val,
        unit: 'mg/dL',
        referenceRange: '< 200 mg/dL',
        status: 'Elevated',
        statusClass: 'badge-elevated',
        contributionText: 'Higher-risk contribution',
        contributionClass: 'badge-higher',
        priority: 'primary',
        whyItMatters: `Your total cholesterol is ${val} mg/dL, which is above the desirable reference threshold (< 200 mg/dL). High circulating lipid concentrations are associated with arterial plaque buildup and increased cardiovascular risk.`
      };
    } else {
      return {
        name: 'Total Serum Cholesterol',
        value: val,
        unit: 'mg/dL',
        referenceRange: '< 200 mg/dL (Borderline: 200–239)',
        status: 'Elevated',
        statusClass: 'badge-elevated',
        contributionText: 'Higher-risk contribution',
        contributionClass: 'badge-higher',
        priority: 'primary',
        whyItMatters: `Your total cholesterol is ${val} mg/dL, falling into the borderline high range (200–239 mg/dL). Borderline lipid levels can influence arterial health and are identified as a contributing factor in your assessment.`
      };
    }
  }

  // 4. Age Demographic
  if (lower.includes('age')) {
    const val = patient.demographics?.age != null ? patient.demographics.age : '--';
    return {
      name: 'Age Demographic',
      value: val,
      unit: 'years',
      referenceRange: '< 55 years',
      status: 'Relevant',
      statusClass: 'badge-relevant',
      contributionText: 'Relevant factor',
      contributionClass: 'badge-relevant',
      priority: 'secondary',
      whyItMatters: `You are ${val} years of age. Epidemiological evidence indicates that cardiovascular elasticity naturally declines with advancing age, making your age bracket a standard contributor considered in this evaluation.`
    };
  }

  // 5. Clinical History of Hypertension
  if (lower.includes('history of hypertension')) {
    return {
      name: 'Clinical History of Hypertension',
      value: 'Documented',
      unit: '',
      referenceRange: 'No clinical hypertension',
      status: 'Relevant',
      statusClass: 'badge-relevant',
      contributionText: 'Higher-risk contribution',
      contributionClass: 'badge-higher',
      priority: 'secondary',
      whyItMatters: 'A documented clinical history of hypertension indicates chronic vascular demand over time, which clinical models factor into your cardiovascular risk assessment.'
    };
  }

  // 6. Family History of Cardiovascular Disease
  if (lower.includes('family history')) {
    return {
      name: 'Family History of CVD',
      value: 'Documented',
      unit: '',
      referenceRange: 'No family history',
      status: 'Relevant',
      statusClass: 'badge-relevant',
      contributionText: 'Higher-risk contribution',
      contributionClass: 'badge-higher',
      priority: 'secondary',
      whyItMatters: 'Having immediate family members with cardiovascular disease is associated with elevated familial and hereditary predisposition to cardiovascular complications.'
    };
  }

  // Fallback for any other valid CVD factor string
  return {
    name: 'Cardiovascular Factor',
    value: 'Present',
    unit: '',
    referenceRange: 'Clinical baseline',
    status: 'Relevant',
    statusClass: 'badge-relevant',
    contributionText: 'Relevant factor',
    contributionClass: 'badge-relevant',
    priority: 'secondary',
    whyItMatters: `${str}. This parameter was identified by clinical evaluation rules as a relevant factor influencing your assessed cardiovascular risk.`
  };
}

/**
 * Renders categorized factor cards (Most Relevant vs Other Relevant) into the DOM
 */
function renderDiseaseFactorCards(factors, primaryContainer, secondaryContainer, secondaryGroupElem, isUnavailable, diseaseTitle) {
  if (!primaryContainer || !secondaryContainer) return;

  primaryContainer.innerHTML = '';
  secondaryContainer.innerHTML = '';

  if (isUnavailable) {
    primaryContainer.innerHTML = `
      <div class="xai-factor-card status-relevant">
        <p class="narrative-text" style="color: var(--text-dim);">
          Detailed factor attribution is currently unavailable, but your risk prediction was completed successfully.
        </p>
      </div>
    `;
    if (secondaryGroupElem) secondaryGroupElem.style.display = 'none';
    return;
  }

  const primaryFactors = factors.filter(f => f.priority === 'primary');
  const secondaryFactors = factors.filter(f => f.priority === 'secondary');

  // Render Primary Factors
  if (primaryFactors.length > 0) {
    primaryFactors.forEach(factor => {
      primaryContainer.appendChild(createFactorCardElement(factor));
    });
  } else {
    primaryContainer.innerHTML = `
      <div class="xai-factor-card status-normal">
        <p class="narrative-text">All primary physiological biomarkers were evaluated within standard baseline limits.</p>
      </div>
    `;
  }

  // Render Secondary Factors
  if (secondaryFactors.length > 0) {
    if (secondaryGroupElem) secondaryGroupElem.style.display = 'block';
    secondaryFactors.forEach(factor => {
      secondaryContainer.appendChild(createFactorCardElement(factor));
    });
  } else {
    if (secondaryGroupElem) secondaryGroupElem.style.display = 'none';
  }
}

/**
 * Creates a rich factor card DOM element
 */
function createFactorCardElement(factor) {
  const card = document.createElement('div');
  const cardClass = factor.status === 'Elevated' ? 'status-elevated' : (factor.status === 'Normal' ? 'status-normal' : 'status-relevant');
  card.className = `xai-factor-card ${cardClass}`;

  const unitHtml = factor.unit ? `<span class="factor-val-unit">${escapeHtml(factor.unit)}</span>` : '';

  card.innerHTML = `
    <div class="factor-card-top">
      <div class="factor-meta-left">
        <span class="factor-name">${factor.index}. ${escapeHtml(factor.name)}</span>
        <div class="factor-value-row">
          <span class="factor-val-num">${escapeHtml(String(factor.value))}</span>
          ${unitHtml}
        </div>
      </div>
      <div class="factor-badges-right">
        <span class="status-badge ${factor.statusClass}">Status: ${escapeHtml(factor.status)}</span>
        <span class="contribution-badge ${factor.contributionClass}">${escapeHtml(factor.contributionText)}</span>
      </div>
    </div>
    <div class="factor-reference-row">
      <span class="ref-label">Reference Range:</span>
      <span class="ref-value">${escapeHtml(factor.referenceRange)}</span>
    </div>
    <div class="factor-narrative-block">
      <span class="narrative-heading">Why this matters:</span>
      <p class="narrative-text">${escapeHtml(factor.whyItMatters)}</p>
    </div>
  `;

  return card;
}

/**
 * Generates the cohesive, plain-language "What this means" synthesis
 */
function generateClinicalSynthesis(diabetesFactors, cvdFactors, patient) {
  const sentences = [];

  // 1. Diabetes synthesis
  const diabElevated = diabetesFactors.filter(f => f.status === 'Elevated');
  if (diabElevated.length > 0) {
    const factorNames = diabElevated.map(f => f.name.toLowerCase()).join(' and ');
    sentences.push(`The assessment identified elevated ${factorNames} as important factors associated with your current diabetes risk.`);
  } else {
    sentences.push('Key glycemic indicators, including fasting blood glucose, were evaluated within optimal reference ranges, supporting a lower assessed diabetes risk.');
  }

  // 2. CVD synthesis
  const cvdElevated = cvdFactors.filter(f => f.status === 'Elevated');
  if (cvdElevated.length > 0) {
    const factorNames = cvdElevated.map(f => f.name.toLowerCase()).join(', ');
    sentences.push(`For cardiovascular health, ${factorNames} were identified as relevant factors influencing your assessed risk.`);
  } else {
    sentences.push('Resting blood pressure and cardiovascular indicators were measured within optimal baseline levels, supporting a favorable cardiovascular risk profile.');
  }

  // 3. Demographic & history factors
  const historyFactors = [...diabetesFactors, ...cvdFactors].filter(f => f.priority === 'secondary');
  if (historyFactors.length > 0) {
    const uniqueNames = [...new Set(historyFactors.map(f => f.name.toLowerCase()))].slice(0, 2).join(' and ');
    sentences.push(`Demographic and clinical history factors (${uniqueNames}) were also taken into account.`);
  }

  sentences.push('These explanations provide transparency into the specific parameters considered during your assessment, helping facilitate productive conversations with your physician.');

  return sentences.join(' ');
}

/**
 * Simple HTML Escaping for XSS prevention
 */
function escapeHtml(text) {
  if (text == null) return '';
  return String(text)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

/**
 * Action Button Event Handlers
 */
function initActionButtons() {
  const newAssessmentBtns = [
    document.getElementById('btn-new-assessment'),
    document.getElementById('nav-new-assessment-btn')
  ];

  newAssessmentBtns.forEach((btn) => {
    if (btn) {
      btn.addEventListener('click', () => {
        // Clear saved result to allow fresh assessment
        sessionStorage.removeItem('current_health_analysis');
      });
    }
  });
}
