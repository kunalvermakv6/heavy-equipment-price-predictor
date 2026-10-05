<template>
  <div class="app-container">
    <!-- Navbar / Header -->
    <header class="header">
      <div class="header-content">
        <div class="brand">
          <span class="brand-icon">🚜</span>
          <div>
            <h1>Heavy Equipment Price AI</h1>
            <p class="subtitle">Machine Learning Valuation Engine for Industrial & Construction Machinery</p>
          </div>
        </div>
        <div class="status-container">
          <div class="status-pill" :class="healthStatus.isHealthy ? 'status-online' : 'status-offline'">
            <span class="status-dot"></span>
            <span>API: {{ healthStatus.text }}</span>
          </div>
          <span class="model-tag" v-if="healthStatus.isHealthy">
            {{ healthStatus.modelName || 'LightGBM Regressor' }}
          </span>
        </div>
      </div>
    </header>

    <!-- Main Content Area -->
    <main class="main-content">
      <!-- Quick Presets -->
      <section class="presets-section">
        <div class="section-title-wrap">
          <span class="badge">1-Click Demos</span>
          <h2>Load Sample Equipment Presets</h2>
        </div>
        <div class="preset-cards">
          <button
            v-for="(preset, idx) in presets"
            :key="idx"
            type="button"
            class="preset-card"
            :class="{ active: selectedPresetIndex === idx }"
            @click="loadPreset(preset, idx)"
          >
            <div class="preset-icon">{{ preset.icon }}</div>
            <div class="preset-info">
              <span class="preset-name">{{ preset.name }}</span>
              <span class="preset-meta">{{ preset.meta }}</span>
            </div>
            <span class="preset-arrow">→</span>
          </button>
        </div>
      </section>

      <!-- Grid Layout: Form on Left, Output on Right -->
      <div class="grid-layout">
        <!-- Input Form Section -->
        <div class="form-container">
          <div class="form-header">
            <h3>Machine Configuration Parameters</h3>
            <p>Modify any parameter below or use presets above to estimate current transaction price.</p>
          </div>

          <form @submit.prevent="runPrediction" class="equipment-form">
            <!-- Section 1: Core Details -->
            <div class="form-group-card">
              <div class="group-title">
                <span class="group-number">1</span>
                <h4>Core Identification & Age</h4>
              </div>
              <div class="input-grid">
                <div class="field">
                  <label for="ManufactureYear">Manufacture Year *</label>
                  <input
                    id="ManufactureYear"
                    type="number"
                    v-model.number="formData.ManufactureYear"
                    placeholder="e.g. 2005"
                    min="1960"
                    max="2030"
                    required
                  />
                  <span class="hint">Year asset was produced</span>
                </div>

                <div class="field">
                  <label for="OperationalHoursMeter">Operational Hours Meter</label>
                  <input
                    id="OperationalHoursMeter"
                    type="number"
                    step="any"
                    v-model.number="formData.OperationalHoursMeter"
                    placeholder="e.g. 68.0"
                    min="0"
                  />
                  <span class="hint">Lifetime active run cycles</span>
                </div>

                <div class="field">
                  <label for="UtilizationTier">Utilization Tier</label>
                  <select id="UtilizationTier" v-model="formData.UtilizationTier">
                    <option value="Low">Low</option>
                    <option value="Medium">Medium</option>
                    <option value="High">High</option>
                    <option value="Unknown">Unknown / Not Specified</option>
                  </select>
                </div>

                <div class="field">
                  <label for="TransactionDate">Transaction Date</label>
                  <input
                    id="TransactionDate"
                    type="date"
                    v-model="formData.TransactionDate"
                  />
                  <span class="hint">Date entry finalized</span>
                </div>
              </div>
            </div>

            <!-- Section 2: Machine Classification & Specs -->
            <div class="form-group-card">
              <div class="group-title">
                <span class="group-number">2</span>
                <h4>Classification & Technical Specifications</h4>
              </div>
              <div class="input-grid">
                <div class="field">
                  <label for="Spec_FullDescriptor">Spec Full Descriptor</label>
                  <input
                    id="Spec_FullDescriptor"
                    type="text"
                    v-model="formData.Spec_FullDescriptor"
                    placeholder="e.g. 521D, 345BL, EX120-5"
                  />
                </div>

                <div class="field">
                  <label for="FunctionalClassification">Functional Classification</label>
                  <input
                    id="FunctionalClassification"
                    type="text"
                    v-model="formData.FunctionalClassification"
                    placeholder="e.g. Wheel Loader - 110.0 to 120.0 HP"
                  />
                </div>

                <div class="field">
                  <label for="InventoryGroupDescription">Inventory Group</label>
                  <select id="InventoryGroupDescription" v-model="formData.InventoryGroupDescription">
                    <option value="Wheel Loader">Wheel Loader</option>
                    <option value="Track Excavators">Track Excavators</option>
                    <option value="Backhoe Loaders">Backhoe Loaders</option>
                    <option value="Skid Steer Loaders">Skid Steer Loaders</option>
                    <option value="Track Type Tractors">Track Type Tractors</option>
                    <option value="Motor Graders">Motor Graders</option>
                    <option value="Unknown">Other / Unknown</option>
                  </select>
                </div>

                <div class="field">
                  <label for="RegionCode">Jurisdiction / Region</label>
                  <input
                    id="RegionCode"
                    type="text"
                    v-model="formData.RegionCode"
                    placeholder="e.g. Alabama, California, Texas"
                  />
                </div>
              </div>
            </div>

            <!-- Section 3: Cabin & Attachments -->
            <div class="form-group-card">
              <div class="group-title">
                <span class="group-number">3</span>
                <h4>Operator Station & Mechanical Config</h4>
              </div>
              <div class="input-grid">
                <div class="field">
                  <label for="CabinType">Cabin Type</label>
                  <select id="CabinType" v-model="formData.CabinType">
                    <option value="EROPS w AC">EROPS w AC (Enclosed w/ Air Conditioning)</option>
                    <option value="EROPS">EROPS (Enclosed Roll Over Protective)</option>
                    <option value="OROPS">OROPS (Open Roll Over Protective)</option>
                    <option value="None or Unspecified">None or Unspecified</option>
                  </select>
                </div>

                <div class="field">
                  <label for="Forks">Forks Attachment</label>
                  <select id="Forks" v-model="formData.Forks">
                    <option value="None or Unspecified">None or Unspecified</option>
                    <option value="Yes">Yes</option>
                    <option value="Unknown">Unknown</option>
                  </select>
                </div>

                <div class="field">
                  <label for="col10">Hydraulic System (col10)</label>
                  <select id="col10" v-model="formData.col10">
                    <option value="2 Valve">2 Valve</option>
                    <option value="Standard">Standard</option>
                    <option value="Auxiliary">Auxiliary</option>
                    <option value="None or Unspecified">None or Unspecified</option>
                  </select>
                </div>

                <div class="field">
                  <label for="col29">Differential Power (col29)</label>
                  <select id="col29" v-model="formData.col29">
                    <option value="Standard">Standard</option>
                    <option value="Limited Slip">Limited Slip</option>
                    <option value="No Spin">No Spin</option>
                    <option value="None or Unspecified">None or Unspecified</option>
                  </select>
                </div>
              </div>
            </div>

            <!-- Actions Bar -->
            <div class="form-actions">
              <button type="submit" class="btn-primary" :disabled="isLoading">
                <span v-if="isLoading" class="spinner"></span>
                <span>{{ isLoading ? 'Calculating Valuation...' : 'Calculate Predicted Selling Price' }}</span>
              </button>
              <button type="button" class="btn-secondary" @click="resetForm" :disabled="isLoading">
                Reset
              </button>
            </div>
          </form>
        </div>

        <!-- Valuation Result Card -->
        <div class="result-container">
          <div class="result-card" :class="{ 'has-prediction': predictionResult }">
            <div class="result-header">
              <span class="badge-accent">Live Model Valuation</span>
              <span class="model-badge">Joblib • LGBM</span>
            </div>

            <div v-if="predictionResult" class="result-body">
              <span class="price-label">Estimated Selling Price</span>
              <div class="price-value">{{ predictionResult.predicted_price_formatted }}</div>
              <div class="price-currency">{{ predictionResult.currency }} (US Dollars)</div>

              <div class="valuation-meta">
                <div class="meta-item">
                  <span class="meta-label">Model Target Log1p</span>
                  <span class="meta-val font-mono">{{ predictionResult.log_prediction }}</span>
                </div>
                <div class="meta-item">
                  <span class="meta-label">Algorithm</span>
                  <span class="meta-val">{{ predictionResult.model_used }}</span>
                </div>
              </div>

              <!-- Breakdown Highlights -->
              <div class="summary-chips">
                <div class="chip" v-if="formData.Spec_FullDescriptor">
                  <span class="chip-k">Model:</span>
                  <span class="chip-v">{{ formData.Spec_FullDescriptor }}</span>
                </div>
                <div class="chip" v-if="formData.ManufactureYear">
                  <span class="chip-k">Year:</span>
                  <span class="chip-v">{{ formData.ManufactureYear }}</span>
                </div>
                <div class="chip" v-if="formData.OperationalHoursMeter !== null && formData.OperationalHoursMeter !== undefined">
                  <span class="chip-k">Hours:</span>
                  <span class="chip-v">{{ formData.OperationalHoursMeter }} hrs</span>
                </div>
                <div class="chip" v-if="formData.CabinType">
                  <span class="chip-k">Cab:</span>
                  <span class="chip-v">{{ formData.CabinType }}</span>
                </div>
              </div>

              <!-- Quick Verification Feedback -->
              <div class="verification-box">
                <div class="v-icon">✓</div>
                <div>
                  <strong>Prediction Verified</strong>
                  <p>Model loaded via joblib. Pipeline automatically cleaned features, applied ordinal encoding, and executed regression.</p>
                </div>
              </div>
            </div>

            <div v-else class="result-placeholder">
              <div class="placeholder-icon">📊</div>
              <h4>Ready to Predict</h4>
              <p>Select any preset above or adjust parameters and click <strong>Calculate Predicted Selling Price</strong>.</p>
            </div>

            <!-- JSON Payload Inspector Accordion -->
            <div class="payload-inspector">
              <button type="button" class="inspector-toggle" @click="showPayload = !showPayload">
                <span>{{ showPayload ? 'Hide API Request JSON' : 'View API Request JSON' }}</span>
                <span>{{ showPayload ? '▲' : '▼' }}</span>
              </button>
              <div v-if="showPayload" class="json-viewer">
                <pre><code>{{ JSON.stringify(formData, null, 2) }}</code></pre>
              </div>
            </div>
          </div>

          <!-- Quick API Documentation Card -->
          <div class="api-info-card">
            <h4>Direct API Endpoints</h4>
            <div class="endpoint-row">
              <span class="badge-get">GET</span>
              <span class="endpoint-path">/health</span>
            </div>
            <div class="endpoint-row">
              <span class="badge-post">POST</span>
              <span class="endpoint-path">/predict</span>
            </div>
            <p class="api-tip">FastAPI interactive Swagger UI available at <a href="/docs" target="_blank">/docs</a></p>
          </div>
        </div>
      </div>
    </main>

    <!-- Footer -->
    <footer class="footer">
      <p>Heavy Equipment Price Prediction • Powered by FastAPI & Vue 3 • LightGBM Model Engine</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

const healthStatus = ref({
  isHealthy: false,
  text: 'Checking...',
  modelName: ''
})

const isLoading = ref(false)
const predictionResult = ref(null)
const showPayload = ref(false)
const selectedPresetIndex = ref(0)

// Sample presets extracted directly from test.csv
const presets = [
  {
    icon: '🚜',
    name: 'Wheel Loader 521D',
    meta: '2005 • 68 hrs • Alabama',
    data: {
      AssetID: 999097,
      ProductConfigID: 3168,
      DataOriginCode: 'ACH138',
      VendorPartnerID: 'GTX',
      ManufactureYear: 2005,
      OperationalHoursMeter: 68.0,
      UtilizationTier: 'Low',
      TransactionDate: '2007-11-16',
      Spec_FullDescriptor: '521D',
      Spec_BaseClass: '521',
      Spec_SubClass: 'D',
      FunctionalClassification: 'Wheel Loader - 110.0 to 120.0 Horsepower',
      RegionCode: 'Alabama',
      InventoryGroupCategory: 'WL',
      InventoryGroupDescription: 'Wheel Loader',
      CabinType: 'EROPS w AC',
      Forks: 'None or Unspecified',
      col10: '2 Valve',
      col28: 'Standard',
      col29: 'Conventional',
      HasOperationalHours: 1
    }
  },
  {
    icon: '🏗️',
    name: 'Track Excavator 345BL',
    meta: '1999 • 10,466 hrs • Minnesota',
    data: {
      AssetID: 1018084,
      ProductConfigID: 1344,
      DataOriginCode: 'ACH138',
      VendorPartnerID: 'GTX',
      ManufactureYear: 1999,
      OperationalHoursMeter: 10466.0,
      UtilizationTier: 'Medium',
      TransactionDate: '2007-06-01',
      Spec_FullDescriptor: '345BL',
      Spec_BaseClass: '345',
      Spec_SubClass: 'BL',
      FunctionalClassification: 'Hydraulic Excavator, Track - 40.0 to 50.0 Metric Tons',
      RegionCode: 'Minnesota',
      InventoryGroupCategory: 'TEX',
      InventoryGroupDescription: 'Track Excavators',
      CabinType: 'EROPS w AC',
      Forks: 'None or Unspecified',
      col10: 'Standard',
      col28: 'Standard',
      col29: 'Conventional',
      HasOperationalHours: 1
    }
  },
  {
    icon: '⛏️',
    name: 'Excavator EX120-5',
    meta: '2001 • 3,817 hrs • California',
    data: {
      AssetID: 1048712,
      ProductConfigID: 2808,
      DataOriginCode: 'ACH138',
      VendorPartnerID: 'GTX',
      ManufactureYear: 2001,
      OperationalHoursMeter: 3817.0,
      UtilizationTier: 'Low',
      TransactionDate: '2012-06-16',
      Spec_FullDescriptor: 'EX120-5',
      Spec_BaseClass: 'EX120',
      Spec_SubClass: '-5',
      FunctionalClassification: 'Hydraulic Excavator, Track - 8.0 to 11.0 Metric Tons',
      RegionCode: 'California',
      InventoryGroupCategory: 'TEX',
      InventoryGroupDescription: 'Track Excavators',
      CabinType: 'EROPS w AC',
      Forks: 'None or Unspecified',
      col10: 'Standard',
      col28: 'Standard',
      col29: 'Conventional',
      HasOperationalHours: 1
    }
  },
  {
    icon: '⚙️',
    name: 'Mini Excavator 304CR',
    meta: '2006 • 1,498 hrs • Illinois',
    data: {
      AssetID: 697537,
      ProductConfigID: 1089,
      DataOriginCode: 'ACH138',
      VendorPartnerID: 'GTX',
      ManufactureYear: 2006,
      OperationalHoursMeter: 1498.0,
      UtilizationTier: 'Medium',
      TransactionDate: '2010-08-27',
      Spec_FullDescriptor: '304CR',
      Spec_BaseClass: '304',
      Spec_SubClass: 'CR',
      FunctionalClassification: 'Hydraulic Excavator, Track - 4.0 to 5.0 Metric Tons',
      RegionCode: 'Illinois',
      InventoryGroupCategory: 'TEX',
      InventoryGroupDescription: 'Track Excavators',
      CabinType: 'EROPS w AC',
      Forks: 'None or Unspecified',
      col10: 'Auxiliary',
      col28: 'Standard',
      col29: 'Conventional',
      HasOperationalHours: 1
    }
  }
]

const formData = ref({ ...presets[0].data })

const loadPreset = (preset, idx) => {
  selectedPresetIndex.value = idx
  formData.value = { ...preset.data }
  runPrediction()
}

const checkHealth = async () => {
  try {
    const res = await fetch('/health')
    if (res.ok) {
      const data = await res.json()
      healthStatus.value = {
        isHealthy: data.model_loaded,
        text: data.status === 'healthy' ? 'Online' : 'Degraded',
        modelName: data.model_name
      }
    } else {
      healthStatus.value = { isHealthy: false, text: 'Offline', modelName: '' }
    }
  } catch (err) {
    healthStatus.value = { isHealthy: false, text: 'Disconnected', modelName: '' }
  }
}

const runPrediction = async () => {
  isLoading.value = true
  try {
    const res = await fetch('/predict', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData.value)
    })

    if (!res.ok) {
      const err = await res.json()
      alert(`Prediction failed: ${err.detail || 'Unknown error'}`)
      return
    }

    const data = await res.json()
    predictionResult.value = data
  } catch (err) {
    alert(`Network error calling prediction API: ${err.message}`)
  } finally {
    isLoading.value = false
  }
}

const resetForm = () => {
  formData.value = { ...presets[0].data }
  predictionResult.value = null
  selectedPresetIndex.value = 0
}

onMounted(() => {
  checkHealth()
  // Automatically run first prediction on load for instant interactive demo
  runPrediction()
})
</script>

<style>
:root {
  --primary: #f59e0b;
  --primary-hover: #d97706;
  --primary-light: #fef3c7;
  --dark-bg: #0f172a;
  --card-bg: #1e293b;
  --card-border: #334155;
  --text-main: #f8fafc;
  --text-muted: #94a3b8;
  --success: #10b981;
  --danger: #ef4444;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: 'Plus Jakarta Sans', sans-serif;
  background-color: var(--dark-bg);
  color: var(--text-main);
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}

.font-mono {
  font-family: 'JetBrains Mono', monospace;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Header */
.header {
  background: rgba(30, 41, 59, 0.7);
  backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--card-border);
  position: sticky;
  top: 0;
  z-index: 50;
  padding: 1rem 1.5rem;
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.brand-icon {
  font-size: 2.25rem;
}

.brand h1 {
  font-size: 1.35rem;
  font-weight: 800;
  letter-spacing: -0.025em;
  color: #fff;
}

.subtitle {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.status-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.status-pill {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.35rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-online {
  background: rgba(16, 185, 129, 0.15);
  color: #34d399;
  border: 1px solid rgba(16, 185, 129, 0.3);
}

.status-offline {
  background: rgba(239, 68, 68, 0.15);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
  box-shadow: 0 0 6px currentColor;
}

.model-tag {
  background: rgba(245, 158, 11, 0.15);
  color: var(--primary);
  border: 1px solid rgba(245, 158, 11, 0.3);
  padding: 0.35rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
}

/* Main */
.main-content {
  flex: 1;
  max-width: 1400px;
  width: 100%;
  margin: 0 auto;
  padding: 1.5rem;
}

/* Presets */
.presets-section {
  margin-bottom: 1.75rem;
}

.section-title-wrap {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.badge {
  background: rgba(245, 158, 11, 0.2);
  color: #fbbf24;
  font-size: 0.7rem;
  font-weight: 700;
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.section-title-wrap h2 {
  font-size: 1.1rem;
  font-weight: 700;
  color: #e2e8f0;
}

.preset-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 0.75rem;
}

.preset-card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 10px;
  padding: 0.85rem 1rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
  text-align: left;
  color: inherit;
}

.preset-card:hover {
  border-color: var(--primary);
  transform: translateY(-2px);
  background: #243247;
}

.preset-card.active {
  border-color: var(--primary);
  background: rgba(245, 158, 11, 0.08);
  box-shadow: 0 0 0 1px var(--primary);
}

.preset-icon {
  font-size: 1.75rem;
}

.preset-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.preset-name {
  font-weight: 700;
  font-size: 0.9rem;
  color: #f1f5f9;
}

.preset-meta {
  font-size: 0.75rem;
  color: var(--text-muted);
}

.preset-arrow {
  color: var(--text-muted);
  font-size: 1.1rem;
  transition: transform 0.2s;
}

.preset-card:hover .preset-arrow {
  color: var(--primary);
  transform: translateX(3px);
}

/* Grid layout */
.grid-layout {
  display: grid;
  grid-template-columns: 1fr 420px;
  gap: 1.5rem;
  align-items: start;
}

@media (max-width: 1024px) {
  .grid-layout {
    grid-template-columns: 1fr;
  }
}

/* Form Container */
.form-container {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 12px;
  padding: 1.5rem;
}

.form-header {
  margin-bottom: 1.5rem;
}

.form-header h3 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #fff;
  margin-bottom: 0.25rem;
}

.form-header p {
  font-size: 0.85rem;
  color: var(--text-muted);
}

.form-group-card {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(51, 65, 85, 0.6);
  border-radius: 10px;
  padding: 1.25rem;
  margin-bottom: 1.25rem;
}

.group-title {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin-bottom: 1rem;
}

.group-number {
  background: var(--primary);
  color: #000;
  font-weight: 800;
  font-size: 0.75rem;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.group-title h4 {
  font-size: 0.95rem;
  font-weight: 700;
  color: #e2e8f0;
}

.input-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.field label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #cbd5e1;
}

.field input,
.field select {
  background: #0b1120;
  border: 1px solid var(--card-border);
  border-radius: 6px;
  padding: 0.6rem 0.75rem;
  color: #fff;
  font-size: 0.85rem;
  font-family: inherit;
  outline: none;
  transition: border-color 0.2s;
}

.field input:focus,
.field select:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 1px var(--primary);
}

.field .hint {
  font-size: 0.7rem;
  color: #64748b;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
}

.btn-primary {
  flex: 1;
  background: var(--primary);
  color: #000;
  font-weight: 700;
  font-size: 0.95rem;
  padding: 0.85rem 1.25rem;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  transition: background-color 0.2s, transform 0.1s;
}

.btn-primary:hover:not(:disabled) {
  background: var(--primary-hover);
  transform: translateY(-1px);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: #334155;
  color: #fff;
  font-weight: 600;
  font-size: 0.95rem;
  padding: 0.85rem 1.25rem;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-secondary:hover:not(:disabled) {
  background: #475569;
}

.spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(0, 0, 0, 0.3);
  border-top-color: #000;
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Result Card */
.result-container {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.result-card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
  position: relative;
  overflow: hidden;
}

.result-card.has-prediction {
  border-color: rgba(245, 158, 11, 0.5);
  box-shadow: 0 0 30px rgba(245, 158, 11, 0.15);
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
}

.badge-accent {
  background: rgba(245, 158, 11, 0.15);
  color: var(--primary);
  font-size: 0.75rem;
  font-weight: 700;
  padding: 0.25rem 0.6rem;
  border-radius: 4px;
}

.model-badge {
  font-size: 0.7rem;
  color: var(--text-muted);
  font-family: 'JetBrains Mono', monospace;
}

.price-label {
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-muted);
}

.price-value {
  font-size: 2.75rem;
  font-weight: 800;
  color: #fbbf24;
  letter-spacing: -0.03em;
  line-height: 1.1;
  margin: 0.25rem 0;
}

.price-currency {
  font-size: 0.8rem;
  color: #94a3b8;
  margin-bottom: 1.25rem;
}

.valuation-meta {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  background: #0f172a;
  border: 1px solid rgba(51, 65, 85, 0.7);
  border-radius: 8px;
  padding: 0.75rem;
  margin-bottom: 1.25rem;
}

.meta-item {
  display: flex;
  flex-direction: column;
}

.meta-label {
  font-size: 0.7rem;
  color: var(--text-muted);
}

.meta-val {
  font-size: 0.85rem;
  font-weight: 600;
  color: #e2e8f0;
}

.summary-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-bottom: 1.25rem;
}

.chip {
  background: #334155;
  border-radius: 6px;
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}

.chip-k {
  color: var(--text-muted);
  margin-right: 0.25rem;
}

.chip-v {
  font-weight: 600;
  color: #fff;
}

.verification-box {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.25);
  border-radius: 8px;
  padding: 0.75rem;
  font-size: 0.75rem;
}

.v-icon {
  color: var(--success);
  font-weight: 900;
  font-size: 0.9rem;
}

.verification-box p {
  color: #a7f3d0;
  margin-top: 0.15rem;
}

.result-placeholder {
  text-align: center;
  padding: 2.5rem 1rem;
}

.placeholder-icon {
  font-size: 3rem;
  margin-bottom: 0.75rem;
}

.result-placeholder h4 {
  font-size: 1.1rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.result-placeholder p {
  font-size: 0.85rem;
  color: var(--text-muted);
}

/* JSON Viewer */
.payload-inspector {
  margin-top: 1.25rem;
  border-top: 1px solid var(--card-border);
  padding-top: 1rem;
}

.inspector-toggle {
  width: 100%;
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.35rem 0;
}

.inspector-toggle:hover {
  color: #fff;
}

.json-viewer {
  margin-top: 0.75rem;
  background: #090d16;
  border: 1px solid var(--card-border);
  border-radius: 6px;
  padding: 0.75rem;
  max-height: 220px;
  overflow-y: auto;
}

.json-viewer pre {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.7rem;
  color: #38bdf8;
}

/* API Info Card */
.api-info-card {
  background: var(--card-bg);
  border: 1px solid var(--card-border);
  border-radius: 12px;
  padding: 1.25rem;
}

.api-info-card h4 {
  font-size: 0.85rem;
  font-weight: 700;
  color: #cbd5e1;
  margin-bottom: 0.75rem;
}

.endpoint-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.badge-get {
  background: rgba(16, 185, 129, 0.2);
  color: #34d399;
  font-weight: 700;
  font-size: 0.65rem;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  font-family: 'JetBrains Mono', monospace;
}

.badge-post {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
  font-weight: 700;
  font-size: 0.65rem;
  padding: 0.15rem 0.4rem;
  border-radius: 4px;
  font-family: 'JetBrains Mono', monospace;
}

.endpoint-path {
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.8rem;
  color: #f1f5f9;
}

.api-tip {
  font-size: 0.75rem;
  color: var(--text-muted);
  margin-top: 0.75rem;
}

.api-tip a {
  color: var(--primary);
  text-decoration: none;
}

.api-tip a:hover {
  text-decoration: underline;
}

/* Footer */
.footer {
  border-top: 1px solid var(--card-border);
  padding: 1.25rem;
  text-align: center;
  font-size: 0.75rem;
  color: var(--text-muted);
  background: rgba(15, 23, 42, 0.4);
}
</style>
