/**
 * AI Health Risk Prediction System - Assessment Page Logic
 * Manages live BMI calculation, client-side validation, unified JSON payload construction,
 * backend API submission (POST /api/analyze), and session storage handoff.
 */

const API_BASE_URL = 'http://127.0.0.1:8001';

document.addEventListener('DOMContentLoaded', () => {
  initBmiCalculator();
  initFormValidationAndSubmit();
  initClearButton();
  initDemoSampleLoaders();
});

/**
 * Live Automatic BMI Calculation
 */
function initBmiCalculator() {
  const heightInput = document.getElementById('height-cm');
  const weightInput = document.getElementById('weight-kg');
  const bmiValDisplay = document.getElementById('calculated-bmi-val');
  const bmiCatDisplay = document.getElementById('calculated-bmi-cat');
  const bmiHiddenInput = document.getElementById('calculated-bmi-hidden');
  const bmiBox = document.getElementById('bmi-display-box');

  function calculateBmi() {
    const height = parseFloat(heightInput.value);
    const weight = parseFloat(weightInput.value);

    if (height > 40 && weight > 10) {
      const heightInMeters = height / 100.0;
      const bmi = weight / (heightInMeters * heightInMeters);
      const roundedBmi = parseFloat(bmi.toFixed(1));

      bmiValDisplay.textContent = `${roundedBmi}`;
      bmiHiddenInput.value = roundedBmi;

      // Classify category
      let category = '';
      let catClass = '';

      if (roundedBmi < 18.5) {
        category = 'Underweight (<18.5)';
        catClass = 'cat-underweight';
      } else if (roundedBmi < 25.0) {
        category = 'Normal Weight (18.5 - 24.9)';
        catClass = 'cat-normal';
      } else if (roundedBmi < 30.0) {
        category = 'Overweight (25.0 - 29.9)';
        catClass = 'cat-overweight';
      } else {
        category = 'Obese Class (>=30.0)';
        catClass = 'cat-obese';
      }

      bmiCatDisplay.textContent = category;
      bmiBox.className = `bmi-display-box ${catClass}`;
      clearFieldError('bmi');
    } else {
      bmiValDisplay.textContent = '--';
      bmiCatDisplay.textContent = 'Awaiting measurements';
      bmiHiddenInput.value = '';
      bmiBox.className = 'bmi-display-box';
    }
  }

  heightInput.addEventListener('input', calculateBmi);
  weightInput.addEventListener('input', calculateBmi);
}

/**
 * Validation Helpers
 */
function setFieldError(fieldId, errorMsg) {
  const inputEl = document.getElementById(fieldId);
  const errorEl = document.getElementById(`error-${fieldId}`);
  if (inputEl) inputEl.classList.add('input-invalid');
  if (errorEl) {
    errorEl.textContent = errorMsg;
    errorEl.style.display = 'block';
  }
}

function clearFieldError(fieldId) {
  const inputEl = document.getElementById(fieldId);
  const errorEl = document.getElementById(`error-${fieldId}`);
  if (inputEl) inputEl.classList.remove('input-invalid');
  if (errorEl) {
    errorEl.textContent = '';
    errorEl.style.display = 'none';
  }
}

function clearAllErrors() {
  const invalidInputs = document.querySelectorAll('.input-invalid');
  invalidInputs.forEach((el) => el.classList.remove('input-invalid'));

  const errorMessages = document.querySelectorAll('.field-error');
  errorMessages.forEach((el) => {
    el.textContent = '';
    el.style.display = 'none';
  });

  const generalError = document.getElementById('form-general-error');
  if (generalError) generalError.style.display = 'none';
}

/**
 * Form Validation and Submission
 */
function initFormValidationAndSubmit() {
  const form = document.getElementById('unified-patient-form');
  const submitBtn = document.getElementById('btn-analyze-health');
  const btnText = document.getElementById('btn-analyze-text');
  const btnSpinner = document.getElementById('btn-analyze-spinner');
  const btnIcon = document.getElementById('btn-analyze-icon');
  const generalError = document.getElementById('form-general-error');
  const errorTitle = document.getElementById('form-error-title');
  const errorDesc = document.getElementById('form-error-desc');

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearAllErrors();

    let isValid = true;
    let firstErrorField = null;

    // Helper validation checker
    function check(condition, fieldId, message) {
      if (!condition) {
        setFieldError(fieldId, message);
        isValid = false;
        if (!firstErrorField) firstErrorField = document.getElementById(fieldId);
      } else {
        clearFieldError(fieldId);
      }
    }

    // 1. Patient Demographics
    const patientId = document.getElementById('patient-id').value.trim();
    check(patientId.length >= 2, 'patient-id', 'Patient ID must be at least 2 characters.');

    const age = parseInt(document.getElementById('patient-age').value, 10);
    check(!isNaN(age) && age >= 1 && age <= 120, 'patient-age', 'Enter a valid age between 1 and 120.');

    const gender = document.getElementById('patient-gender').value;
    check(gender !== '', 'patient-gender', 'Please select biological sex.');

    // 2. Physical Measurements
    const height = parseFloat(document.getElementById('height-cm').value);
    check(!isNaN(height) && height >= 50 && height <= 250, 'height-cm', 'Height must be between 50 and 250 cm.');

    const weight = parseFloat(document.getElementById('weight-kg').value);
    check(!isNaN(weight) && weight >= 20 && weight <= 300, 'weight-kg', 'Weight must be between 20 and 300 kg.');

    const bmi = parseFloat(document.getElementById('calculated-bmi-hidden').value);
    check(!isNaN(bmi) && bmi >= 5 && bmi <= 90, 'bmi', 'Valid BMI must be calculated from height & weight.');

    // 3. Vital Signs
    const systolicBp = parseInt(document.getElementById('systolic-bp').value, 10);
    check(!isNaN(systolicBp) && systolicBp >= 70 && systolicBp <= 250, 'systolic-bp', 'Systolic BP must be between 70 and 250 mmHg.');

    const diastolicBp = parseInt(document.getElementById('diastolic-bp').value, 10);
    check(!isNaN(diastolicBp) && diastolicBp >= 40 && diastolicBp <= 150, 'diastolic-bp', 'Diastolic BP must be between 40 and 150 mmHg.');

    if (!isNaN(systolicBp) && !isNaN(diastolicBp) && diastolicBp >= systolicBp) {
      setFieldError('diastolic-bp', 'Diastolic BP must be lower than Systolic BP.');
      isValid = false;
      if (!firstErrorField) firstErrorField = document.getElementById('diastolic-bp');
    }

    const heartRate = parseInt(document.getElementById('heart-rate').value, 10);
    check(!isNaN(heartRate) && heartRate >= 35 && heartRate <= 220, 'heart-rate', 'Heart rate must be between 35 and 220 bpm.');

    // 4. Laboratory
    const glucose = parseFloat(document.getElementById('lab-glucose').value);
    check(!isNaN(glucose) && glucose >= 40 && glucose <= 500, 'lab-glucose', 'Fasting glucose must be between 40 and 500 mg/dL.');

    // Optional Lab Fields
    const hba1cVal = document.getElementById('lab-hba1c').value.trim();
    let hba1c = null;
    if (hba1cVal !== '') {
      hba1c = parseFloat(hba1cVal);
      check(!isNaN(hba1c) && hba1c >= 3.0 && hba1c <= 18.0, 'lab-hba1c', 'HbA1c must be between 3.0% and 18.0%.');
    }

    const cholVal = document.getElementById('lab-cholesterol').value.trim();
    let cholesterol = null;
    if (cholVal !== '') {
      cholesterol = parseFloat(cholVal);
      check(!isNaN(cholesterol) && cholesterol >= 50 && cholesterol <= 500, 'lab-cholesterol', 'Total cholesterol must be between 50 and 500 mg/dL.');
    }

    const hdlVal = document.getElementById('lab-hdl').value.trim();
    let hdl = null;
    if (hdlVal !== '') {
      hdl = parseFloat(hdlVal);
      check(!isNaN(hdl) && hdl >= 10 && hdl <= 150, 'lab-hdl', 'HDL must be between 10 and 150 mg/dL.');
    }

    const ldlVal = document.getElementById('lab-ldl').value.trim();
    let ldl = null;
    if (ldlVal !== '') {
      ldl = parseFloat(ldlVal);
      check(!isNaN(ldl) && ldl >= 20 && ldl <= 350, 'lab-ldl', 'LDL must be between 20 and 350 mg/dL.');
    }

    const trigVal = document.getElementById('lab-triglycerides').value.trim();
    let triglycerides = null;
    if (trigVal !== '') {
      triglycerides = parseFloat(trigVal);
      check(!isNaN(triglycerides) && triglycerides >= 30 && triglycerides <= 800, 'lab-triglycerides', 'Triglycerides must be between 30 and 800 mg/dL.');
    }

    // 5. Lifestyle
    const smoking = document.getElementById('lifestyle-smoking').value;
    check(smoking !== '', 'lifestyle-smoking', 'Please select smoking status.');

    const activity = document.getElementById('lifestyle-activity').value;
    check(activity !== '', 'lifestyle-activity', 'Please select physical activity level.');

    const alcohol = document.getElementById('lifestyle-alcohol').value;
    check(alcohol !== '', 'lifestyle-alcohol', 'Please select alcohol consumption.');

    // 6. Medical History
    const hypertension = form.querySelector('input[name="history_hypertension"]:checked').value === 'true';
    const existingDiabetes = form.querySelector('input[name="history_diabetes"]:checked').value === 'true';
    const familyDiabetes = form.querySelector('input[name="family_diabetes"]:checked').value === 'true';
    const familyCvd = form.querySelector('input[name="family_cvd"]:checked').value === 'true';

    // If validation fails
    if (!isValid) {
      generalError.style.display = 'flex';
      errorTitle.textContent = 'Validation Incomplete';
      errorDesc.textContent = 'Please review the highlighted fields above and correct the values.';
      if (firstErrorField) {
        firstErrorField.scrollIntoView({ behavior: 'smooth', block: 'center' });
        firstErrorField.focus();
      }
      return;
    }

    // Build the ONE Unified Patient Health Object
    const unifiedPatientData = {
      patient_id: patientId,
      demographics: {
        age: age,
        gender: gender
      },
      physical: {
        height_cm: height,
        weight_kg: weight,
        bmi: bmi
      },
      vitals: {
        systolic_bp: systolicBp,
        diastolic_bp: diastolicBp,
        heart_rate: heartRate
      },
      laboratory: {
        glucose: glucose,
        hba1c: hba1c,
        total_cholesterol: cholesterol,
        hdl: hdl,
        ldl: ldl,
        triglycerides: triglycerides
      },
      lifestyle: {
        smoking: smoking,
        physical_activity: activity,
        alcohol: alcohol
      },
      medical_history: {
        hypertension: hypertension,
        existing_diabetes: existingDiabetes,
        family_history_diabetes: familyDiabetes,
        family_history_cvd: familyCvd
      }
    };

    // Submit to FastAPI Backend
    try {
      submitBtn.disabled = true;
      btnText.textContent = 'Analyzing Health...';
      btnSpinner.style.display = 'inline-block';
      if (btnIcon) btnIcon.style.display = 'none';

      const response = await fetch(`${API_BASE_URL}/api/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(unifiedPatientData)
      });

      if (!response.ok) {
        const errJson = await response.json().catch(() => ({}));
        throw new Error(errJson.detail || `Server responded with status ${response.status}`);
      }

      const resultData = await response.json();

      // Store result temporarily in sessionStorage
      sessionStorage.setItem('current_health_analysis', JSON.stringify(resultData));

      // Navigate to Unified Results Dashboard
      window.location.href = 'results.html';

    } catch (err) {
      console.error('Analysis submission failed:', err);
      generalError.style.display = 'flex';
      errorTitle.textContent = 'Backend Connection Notice';
      errorDesc.textContent = `Unable to complete analysis on ${API_BASE_URL}. Ensure the FastAPI server is running. (${err.message})`;
      generalError.scrollIntoView({ behavior: 'smooth', block: 'center' });
    } finally {
      submitBtn.disabled = false;
      btnText.textContent = 'Analyze Health Risk';
      btnSpinner.style.display = 'none';
      if (btnIcon) btnIcon.style.display = 'inline-block';
    }
  });
}

/**
 * Clear Form Handler
 */
function initClearButton() {
  const clearBtn = document.getElementById('btn-clear-form');
  const form = document.getElementById('unified-patient-form');

  if (!clearBtn || !form) return;

  clearBtn.addEventListener('click', () => {
    form.reset();
    clearAllErrors();

    // Reset BMI Display
    const bmiValDisplay = document.getElementById('calculated-bmi-val');
    const bmiCatDisplay = document.getElementById('calculated-bmi-cat');
    const bmiHiddenInput = document.getElementById('calculated-bmi-hidden');
    const bmiBox = document.getElementById('bmi-display-box');

    bmiValDisplay.textContent = '--';
    bmiCatDisplay.textContent = 'Awaiting measurements';
    bmiHiddenInput.value = '';
    bmiBox.className = 'bmi-display-box';

    // Clear saved analysis state
    sessionStorage.removeItem('current_health_analysis');

    window.scrollTo({ top: 0, behavior: 'smooth' });
  });
}

/**
 * Sample Patient Loaders for Review Demonstration
 */
function initDemoSampleLoaders() {
  const btnSample1 = document.getElementById('btn-load-sample-1');
  const btnSample2 = document.getElementById('btn-load-sample-2');

  function populateForm(data) {
    clearAllErrors();
    document.getElementById('patient-id').value = data.patient_id;
    document.getElementById('patient-age').value = data.age;
    document.getElementById('patient-gender').value = data.gender;
    document.getElementById('height-cm').value = data.height_cm;
    document.getElementById('weight-kg').value = data.weight_kg;

    // Trigger BMI calculation
    document.getElementById('height-cm').dispatchEvent(new Event('input'));

    document.getElementById('systolic-bp').value = data.systolic_bp;
    document.getElementById('diastolic-bp').value = data.diastolic_bp;
    document.getElementById('heart-rate').value = data.heart_rate;

    document.getElementById('lab-glucose').value = data.glucose;
    document.getElementById('lab-hba1c').value = data.hba1c;
    document.getElementById('lab-cholesterol').value = data.total_cholesterol;
    document.getElementById('lab-hdl').value = data.hdl;
    document.getElementById('lab-ldl').value = data.ldl;
    document.getElementById('lab-triglycerides').value = data.triglycerides;

    document.getElementById('lifestyle-smoking').value = data.smoking;
    document.getElementById('lifestyle-activity').value = data.physical_activity;
    document.getElementById('lifestyle-alcohol').value = data.alcohol;

    // Medical History radios
    const form = document.getElementById('unified-patient-form');
    form.querySelector(`input[name="history_hypertension"][value="${data.hypertension}"]`).checked = true;
    form.querySelector(`input[name="history_diabetes"][value="${data.existing_diabetes}"]`).checked = true;
    form.querySelector(`input[name="family_diabetes"][value="${data.family_history_diabetes}"]`).checked = true;
    form.querySelector(`input[name="family_cvd"][value="${data.family_history_cvd}"]`).checked = true;
  }

  if (btnSample1) {
    btnSample1.addEventListener('click', () => {
      populateForm({
        patient_id: 'PAT-MOD-2026',
        age: 44,
        gender: 'Female',
        height_cm: 165,
        weight_kg: 72,
        systolic_bp: 128,
        diastolic_bp: 82,
        heart_rate: 72,
        glucose: 104,
        hba1c: 5.8,
        total_cholesterol: 195,
        hdl: 52,
        ldl: 118,
        triglycerides: 145,
        smoking: 'Former',
        physical_activity: 'Moderate',
        alcohol: 'None',
        hypertension: false,
        existing_diabetes: false,
        family_history_diabetes: true,
        family_history_cvd: false
      });
    });
  }

  if (btnSample2) {
    btnSample2.addEventListener('click', () => {
      populateForm({
        patient_id: 'PAT-HIGH-2026',
        age: 58,
        gender: 'Male',
        height_cm: 174,
        weight_kg: 92,
        systolic_bp: 148,
        diastolic_bp: 94,
        heart_rate: 84,
        glucose: 142,
        hba1c: 6.8,
        total_cholesterol: 245,
        hdl: 38,
        ldl: 164,
        triglycerides: 210,
        smoking: 'Current',
        physical_activity: 'Sedentary',
        alcohol: 'Moderate',
        hypertension: true,
        existing_diabetes: false,
        family_history_diabetes: true,
        family_history_cvd: true
      });
    });
  }
}
