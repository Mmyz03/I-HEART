/**
 * AI Health Risk Prediction System - Results Dashboard Logic
 * Parses stored session analysis, renders patient summary, dual risk cards,
 * animated gauge progress meters, and handles new assessment navigation.
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
    document.getElementById('res-patient-id').textContent = patient.patient_id || 'PAT-DEMO';
    document.getElementById('res-age').textContent = `${patient.demographics.age} yrs`;
    document.getElementById('res-gender').textContent = patient.demographics.gender;
    document.getElementById('res-bmi').textContent = `${patient.physical.bmi.toFixed(1)} kg/m²`;
    document.getElementById('res-bp').textContent = `${patient.vitals.systolic_bp}/${patient.vitals.diastolic_bp} mmHg`;
    document.getElementById('res-hr').textContent = `${patient.vitals.heart_rate} bpm`;
    document.getElementById('res-glucose').textContent = `${patient.laboratory.glucose} mg/dL`;

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

  } catch (err) {
    console.error('Error rendering results:', err);
    if (contentWrapper) contentWrapper.style.display = 'none';
    if (noDataCard) noDataCard.style.display = 'block';
  }
}

/**
 * Helper to render individual disease risk card
 */
function renderRiskCard(diseaseData, pctElemId, barElemId, badgeElemId, noteElemId, listElemId) {
  const pctElem = document.getElementById(pctElemId);
  const barElem = document.getElementById(barElemId);
  const badgeElem = document.getElementById(badgeElemId);
  const noteElem = document.getElementById(noteElemId);
  const listElem = document.getElementById(listElemId);

  const pct = diseaseData.risk_percentage || 0;
  const level = diseaseData.risk_level || 'Moderate';

  // Set Percentage & Animate Progress Bar
  pctElem.textContent = `${pct}%`;

  // Set progress bar with small timeout for smooth animation
  setTimeout(() => {
    barElem.style.width = `${pct}%`;
  }, 100);

  // Set Badge & Colors
  badgeElem.textContent = `${level} Risk`;
  badgeElem.className = 'risk-level-badge';

  if (level === 'High') {
    badgeElem.classList.add('level-high');
    barElem.classList.add('bar-high');
  } else if (level === 'Moderate') {
    badgeElem.classList.add('level-moderate');
    barElem.classList.add('bar-moderate');
  } else {
    badgeElem.classList.add('level-low');
    barElem.classList.add('bar-low');
  }

  // Set Summary Note
  noteElem.textContent = diseaseData.summary_note || 'Calculated based on clinical factor evaluation.';

  // Render Contributing Factors List
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
      btn.addEventListener('click', (e) => {
        // Clear saved result to allow fresh assessment
        sessionStorage.removeItem('current_health_analysis');
      });
    }
  });
}
