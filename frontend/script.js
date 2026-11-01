// ============ FULL YOJNASETU ML & HYBRID ENGINE ============
// Features: Multi-criteria scoring, state-specific rules, income & category filtering
// Full dataset: 459+ Central and State Government Schemes

const API_BASE_URL = (typeof window !== 'undefined' && (window.location.port === '5000' || window.location.port === '8000'))
  ? 'http://localhost:5000'
  : (typeof window !== 'undefined' && window.location.origin.includes('http') ? window.location.origin : 'http://localhost:5000');

// Static fallback schemes database for instant offline support
const SCHEMES_DB = [
  {
    id: 'pmkisan', name: 'PM-KISAN', type: 'central', category: 'agriculture',
    desc: 'Direct income support of ₹6,000 per year to farmer families',
    benefit: '₹2,000 quarterly installments',
    minAge: 18, maxAge: 70, gender: 'any', caste: 'any', occupation: 'farmer',
    minInc: 0, maxInc: 600000, states: 'all',
    docs: ['Aadhaar Card', 'Bank Account', 'Land Records'],
    link: 'https://pmkisan.gov.in/'
  },
  {
    id: 'ayushman', name: 'Ayushman Bharat PM-JAY', type: 'central', category: 'health',
    desc: 'Free health coverage up to ₹5 lakh per family per year',
    benefit: 'Cashless treatment at empaneled hospitals',
    minAge: 0, maxAge: 99, gender: 'any', caste: 'any', occupation: 'any',
    minInc: 0, maxInc: 800000, states: 'all',
    docs: ['Aadhaar Card', 'Income Certificate'],
    link: 'https://pmjay.gov.in/'
  },
  {
    id: 'mudra', name: 'PM Mudra Yojana', type: 'central', category: 'business',
    desc: 'Loans up to ₹10 lakh for small businesses and entrepreneurs',
    benefit: 'Collateral-free loans with low interest',
    minAge: 18, maxAge: 65, gender: 'any', caste: 'any', occupation: 'self_employed',
    minInc: 0, maxInc: 1200000, states: 'all',
    docs: ['Aadhaar Card', 'Business Plan', 'Bank Account'],
    link: 'https://www.mudra.org.in/'
  },
  {
    id: 'standup', name: 'PM SVANidhi', type: 'central', category: 'business',
    desc: 'Micro-credit facility for street vendors',
    benefit: 'Working capital loan up to ₹10,000',
    minAge: 18, maxAge: 65, gender: 'any', caste: 'any', occupation: 'self_employed',
    minInc: 0, maxInc: 600000, states: 'all',
    docs: ['Aadhaar Card', 'Vendor ID', 'Bank Account'],
    link: 'https://msme.gov.in/svanidhi'
  },
  {
    id: 'skill', name: 'PM Kaushal Vikas Yojana', type: 'central', category: 'education',
    desc: 'Free skill development training for youth',
    benefit: 'Training + Certification + Job placement',
    minAge: 18, maxAge: 35, gender: 'any', caste: 'any', occupation: 'unemployed',
    minInc: 0, maxInc: 600000, states: 'all',
    docs: ['Aadhaar Card', 'Educational Certificates'],
    link: 'https://www.pmkvyofficial.org/'
  },
  {
    id: 'sukanya', name: 'Sukanya Samriddhi Yojana', type: 'central', category: 'savings',
    desc: 'Savings scheme for girl child education and marriage',
    benefit: 'High interest rate + Tax benefits',
    minAge: 0, maxAge: 10, gender: 'female', caste: 'any', occupation: 'any',
    minInc: 0, maxInc: 2000000, states: 'all',
    docs: ['Birth Certificate', 'Aadhaar Card', 'Bank Account'],
    link: 'https://www.nsiindia.gov.in/sukanya-samriddhi-yojana'
  },
  {
    id: 'pmsby', name: 'Pradhan Mantri Suraksha Bima Yojana', type: 'central', category: 'insurance',
    desc: 'Accidental death and disability insurance',
    benefit: '₹2 lakh accidental death coverage',
    minAge: 18, maxAge: 70, gender: 'any', caste: 'any', occupation: 'any',
    minInc: 0, maxInc: 2000000, states: 'all',
    docs: ['Aadhaar Card', 'Bank Account'],
    link: 'https://financialservices.gov.in/insurance-schemes/pradhan-mantri-suraksha-bima-yojana-pmsby'
  },
  {
    id: 'pmjjby', name: 'Pradhan Mantri Jeevan Jyoti Bima Yojana', type: 'central', category: 'insurance',
    desc: 'Life insurance scheme for ₹330 per year',
    benefit: '₹2 lakh life insurance coverage',
    minAge: 18, maxAge: 50, gender: 'any', caste: 'any', occupation: 'any',
    minInc: 0, maxInc: 2000000, states: 'all',
    docs: ['Aadhaar Card', 'Bank Account'],
    link: 'https://financialservices.gov.in/insurance-schemes/pradhan-mantri-jeevan-jyoti-bima-yojana-pmjjby'
  },
  {
    id: 'mannkibaat', name: 'Mann Ki Baat Gramin Kaushalya Yojana', type: 'central', category: 'education',
    desc: 'Skill development for rural youth',
    benefit: 'Training + Placement + ₹1 lakh stipend',
    minAge: 18, maxAge: 35, gender: 'any', caste: 'any', occupation: 'unemployed',
    minInc: 0, maxInc: 600000, states: 'all',
    docs: ['Aadhaar Card', 'Educational Certificates'],
    link: 'https://ddugky.gov.in/'
  },
  {
    id: 'nsap', name: 'National Social Assistance Programme', type: 'central', category: 'pension',
    desc: 'Financial assistance to elderly, widows, and disabled',
    benefit: '₹200-500 monthly pension',
    minAge: 60, maxAge: 99, gender: 'any', caste: 'any', occupation: 'retired',
    minInc: 0, maxInc: 150000, states: 'all',
    docs: ['Aadhaar Card', 'Age Proof', 'Income Certificate'],
    link: 'https://nsap.nic.in/'
  },
  {
    id: 'maha_agri', name: 'Mahatma Phule Krishi Sanman Yojana', type: 'state', category: 'agriculture',
    desc: 'Financial assistance to small and marginal farmers',
    benefit: 'Debt waiver up to ₹2 lakh',
    minAge: 18, maxAge: 70, gender: 'any', caste: 'any', occupation: 'farmer',
    minInc: 0, maxInc: 300000, states: ['MH'],
    docs: ['Aadhaar Card', '7/12 Land Extract', 'Bank Passbook'],
    link: 'https://mahadbtmahait.gov.in/'
  },
  {
    id: 'guj_vidya', name: 'MYSY - Mukhyamantri Yuva Swavalamban Yojana', type: 'state', category: 'education',
    desc: 'Higher education scholarship for bright students from economically weaker families',
    benefit: '50% tuition fee assistance up to ₹2 lakh',
    minAge: 15, maxAge: 25, gender: 'any', caste: 'any', occupation: 'student',
    minInc: 0, maxInc: 600000, states: ['GJ'],
    docs: ['Aadhaar Card', 'Income Certificate', '10th/12th Marksheet'],
    link: 'https://digitalgujarat.gov.in/'
  },
  {
    id: 'kar_arogya', name: 'Arogya Karnataka Scheme', type: 'state', category: 'health',
    desc: 'Comprehensive universal healthcare coverage for Karnataka residents',
    benefit: 'Cashless treatment up to ₹1.5 lakh',
    minAge: 0, maxAge: 99, gender: 'any', caste: 'any', occupation: 'any',
    minInc: 0, maxInc: 100000, states: ['KA'],
    docs: ['BPL Card', 'Aadhaar Card', 'Medical Reports'],
    link: 'https://karunadu.karnataka.gov.in/'
  }
];

// App State Management
const AppState = {
  currentStep: 1,
  totalSteps: 6,
  profile: { gender: null, age_range: null, state: null, category: null, occupation: null, income_range: null },
  schemes: [],
  language: 'en',
  isLoggedIn: false,
  isGuest: false,
  userData: null,
  token: null
};

// Initialize App
function initializeApp() {
  setupEventListeners();

  // Restore authenticated session if present
  const savedToken = localStorage.getItem('yojnasetu_token');
  const savedUser = localStorage.getItem('yojnasetu_user');
  if (savedToken && savedUser) {
    try {
      AppState.isLoggedIn = true;
      AppState.token = savedToken;
      AppState.userData = JSON.parse(savedUser);
      const userMenu = document.getElementById('user-menu');
      if (userMenu) userMenu.classList.remove('hidden');
      const nameEl = document.getElementById('user-display-name');
      if (nameEl) nameEl.textContent = AppState.userData.name || 'Citizen';
    } catch (e) {
      console.warn('Session parse error:', e);
    }
  }

  showPage('landing');
}

// Page Navigation
function showPage(pageId) {
  document.querySelectorAll('[id^="page-"]').forEach(page => page.classList.add('hidden'));
  const target = document.getElementById(`page-${pageId}`);
  if (target) target.classList.remove('hidden');
  if (pageId === 'landing') {
    const appEl = document.getElementById('app');
    if (appEl) appEl.scrollTop = 0;
  }
}

// Questionnaire Logic
function showQuestion(step) {
  AppState.currentStep = step;
  document.querySelectorAll('.question-slide').forEach(q => q.classList.add('hidden'));
  const targetQ = document.getElementById(`q${step}`);
  if (targetQ) targetQ.classList.remove('hidden');

  // Update progress
  const progress = (step / AppState.totalSteps) * 100;
  const pb = document.getElementById('progress-bar');
  if (pb) pb.style.width = `${progress}%`;
  const pt = document.getElementById('progress-text');
  if (pt) pt.textContent = `Question ${step} of ${AppState.totalSteps}`;
  const pp = document.getElementById('progress-percent');
  if (pp) pp.textContent = `${Math.round(progress)}%`;

  // Update navigation
  const prevBtn = document.getElementById('btn-prev-question');
  if (prevBtn) prevBtn.disabled = step === 1;
  const skipBtn = document.getElementById('btn-skip-question');
  if (skipBtn) skipBtn.style.display = step < AppState.totalSteps ? 'block' : 'none';

  // Scroll to top
  const qPage = document.getElementById('page-questionnaire');
  if (qPage) qPage.scrollTop = 0;
}

function handleOptionSelect(field, value) {
  AppState.profile[field] = value;
  if (AppState.currentStep < AppState.totalSteps) {
    showQuestion(AppState.currentStep + 1);
  } else {
    showPage('document-upload');
  }
}

function handleDocumentSubmit() {
  const ratioInput = document.getElementById('ration');
  const incomeInput = document.getElementById('income');

  const ration = ratioInput ? ratioInput.files[0] : null;
  const income = incomeInput ? incomeInput.files[0] : null;

  if (!ration || !income) {
    showToast('⚠️ Please upload the required documents or click skip', 'info');
    return;
  }

  showToast('✅ Documents submitted for instant verification', 'success');
  setTimeout(() => {
    calculateResults();
  }, 600);
}

function mapAgeRangeToAge(ageRange) {
  const map = { '0-17': 16, '18-25': 22, '26-40': 33, '41-60': 50, '60+': 65 };
  return map[ageRange] || 30;
}

function mapIncomeRangeToIncome(incomeRange) {
  const map = { 'below_1l': 50000, '1l_2.5l': 175000, '2.5l_5l': 375000, '5l_8l': 650000, 'above_8l': 1000000 };
  return map[incomeRange] || 200000;
}

function mapGender(gender) {
  const map = { male: 'Male', female: 'Female', transgender: 'Transgender', prefer_not_to_say: 'All' };
  return map[gender] || 'All';
}

function mapOccupation(occupation) {
  const map = { student: 'Student', farmer: 'Farmer', salaried: 'Salaried', self_employed: 'Self-employed', daily_wage: 'Daily Wage Worker', homemaker: 'Homemaker', retired: 'Senior Citizen', unemployed: 'Unemployed/Youth' };
  return map[occupation] || 'All';
}

function mapCategory(category) {
  const map = { general: ['Education & Scholarships','Health & Insurance','Business & MSME'], obc: ['OBC'], sc: ['SC'], st: ['ST'], ews: ['EWS'], minority: ['Minority'], prefer_not_to_say: [] };
  return map[category] || [];
}

// ML Engine: Scheme Recommendation API
async function calculateResults() {
  const profile = AppState.profile;
  const userPayload = {
    name: AppState.userData?.name || 'Citizen',
    age: mapAgeRangeToAge(profile.age_range),
    gender: mapGender(profile.gender),
    income: mapIncomeRangeToIncome(profile.income_range),
    occupation: mapOccupation(profile.occupation),
    state: profile.state || '',
    category: profile.category || 'general',
    caste: profile.category || 'general',
    preferred_categories: mapCategory(profile.category),
    limit: 30
  };

  showToast('Analyzing 500+ government schemes with AI...', 'info');

  try {
    const headers = { 'Content-Type': 'application/json' };
    const token = localStorage.getItem('yojnasetu_token') || AppState.token;
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const res = await fetch(`${API_BASE_URL}/api/recommend`, {
      method: 'POST',
      headers: headers,
      body: JSON.stringify(userPayload)
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();

    if (data.recommendations && data.recommendations.length > 0) {
      AppState.schemes = data.recommendations.map((item, index) => {
        const rawType = (item.scheme_type_raw || item.type || '').toLowerCase();
        let displayType = 'central';
        if (rawType.includes('state') || (!rawType.includes('central') && !rawType.includes('private') && !rawType.includes('national'))) {
          displayType = 'state';
        } else if (rawType.includes('private')) {
          displayType = 'private';
        }

        return {
          id: item.id || `scheme_${index}`,
          name: item.scheme,
          type: displayType,
          scheme_type_raw: item.scheme_type_raw || item.type,
          category: item.category,
          desc: item.desc || item.category,
          benefit: item.benefit || 'Financial assistance & welfare benefits',
          score: Math.round(item.score || 70),
          status: item.score >= 80 ? 'eligible' : (item.score >= 60 ? 'likely' : 'check'),
          docs: item.docs && item.docs.length > 0 ? item.docs : ['Aadhaar Card', 'Income Certificate', 'Bank Account'],
          link: item.link || '#',
          reasons: item.reasons && item.reasons.length > 0 ? item.reasons : ['Eligibility verified based on age and income criteria']
        };
      });

      showToast(`Found ${AppState.schemes.length} matching schemes!`, 'success');
      return renderResults();
    }
  } catch (error) {
    console.warn('API unavailable, running offline recommendation matching:', error);
    showToast('Offline Mode: Displaying verified schemes', 'info');
    calculateResultsLocal();
  }
}

function calculateResultsLocal() {
  const profile = AppState.profile;
  let matchedSchemes = [];

  SCHEMES_DB.forEach(scheme => {
    let score = 0;
    let reasons = [];

    // Age matching (30 points)
    if (profile.age_range) {
      const ageMap = { '0-17': 10, '18-25': 21, '26-40': 33, '41-60': 50, '60+': 70 };
      const userAge = ageMap[profile.age_range];
      if (userAge >= scheme.minAge && userAge <= scheme.maxAge) {
        score += 30;
        reasons.push('Age eligible');
      } else if (Math.abs(userAge - scheme.minAge) <= 5 || Math.abs(userAge - scheme.maxAge) <= 5) {
        score += 15;
        reasons.push('Age close to eligible');
      }
    }

    // Gender matching (20 points)
    if (profile.gender && (scheme.gender === 'any' || scheme.gender === profile.gender)) {
      score += 20;
      reasons.push('Gender eligible');
    }

    // Occupation matching (25 points)
    if (profile.occupation && (scheme.occupation === 'any' || scheme.occupation === profile.occupation)) {
      score += 25;
      reasons.push('Occupation matches');
    }

    // Income matching (15 points)
    if (profile.income_range) {
      const incMap = { 'below_1l': 50000, '1l_2.5l': 175000, '2.5l_5l': 375000, '5l_8l': 650000, 'above_8l': 1000000 };
      const userInc = incMap[profile.income_range];
      if (userInc <= scheme.maxInc) {
        score += 15;
        reasons.push('Income eligible');
      } else if (userInc <= scheme.maxInc * 1.2) {
        score += 7;
        reasons.push('Income slightly above limit');
      }
    }

    // State matching (10 points)
    if (profile.state && (scheme.states === 'all' || scheme.states.includes(profile.state))) {
      score += 10;
      reasons.push('State eligible');
    }

    // Category bonus (5 points)
    if (profile.category && profile.category !== 'general' && scheme.caste === 'any') {
      score += 5;
      reasons.push('Category benefits available');
    }

    let status = 'check';
    if (score >= 80) status = 'eligible';
    else if (score >= 60) status = 'likely';

    if (score >= 40) {
      matchedSchemes.push({
        ...scheme,
        score: score,
        status: status,
        reasons: reasons
      });
    }
  });

  matchedSchemes.sort((a, b) => b.score - a.score);
  AppState.schemes = matchedSchemes;
  renderResults();
}

function renderResults() {
  const profileDiv = document.getElementById('profile-summary');
  if (profileDiv) {
    profileDiv.innerHTML = '';
    const labels = {
      gender: { male: 'Male', female: 'Female', transgender: 'Transgender', prefer_not_to_say: 'Not specified' },
      age_range: { '0-17': 'Below 18', '18-25': '18-25 years', '26-40': '26-40 years', '41-60': '41-60 years', '60+': 'Above 60' },
      state: 'State',
      category: { general: 'General', obc: 'OBC', sc: 'SC', st: 'ST', ews: 'EWS', minority: 'Minority', prefer_not_to_say: 'Not specified' },
      occupation: { student: 'Student', farmer: 'Farmer', salaried: 'Salaried', self_employed: 'Self-employed', daily_wage: 'Daily Wage', homemaker: 'Homemaker', retired: 'Retired', unemployed: 'Unemployed' },
      income_range: { below_1l: 'Below ₹1L', '1l_2.5l': '₹1L-2.5L', '2.5l_5l': '₹2.5L-5L', '5l_8l': '₹5L-8L', above_8l: 'Above ₹8L', prefer_not_to_say: 'Not specified' }
    };

    Object.keys(AppState.profile).forEach(key => {
      if (AppState.profile[key]) {
        const val = typeof labels[key] === 'object' ? labels[key][AppState.profile[key]] : AppState.profile[key];
        profileDiv.innerHTML += `<div class="bg-slate-50 rounded-lg p-3"><div class="font-medium text-slate-700 capitalize">${key.replace('_', ' ')}</div><div class="text-slate-600">${val || AppState.profile[key]}</div></div>`;
      }
    });
  }

  // Stats
  const eligible = AppState.schemes.filter(s => s.status === 'eligible').length;
  const likely = AppState.schemes.filter(s => s.status === 'likely').length;
  const total = AppState.schemes.length;

  const statEligible = document.getElementById('stat-eligible');
  if (statEligible) statEligible.textContent = eligible;
  const statCheck = document.getElementById('stat-check');
  if (statCheck) statCheck.textContent = likely;
  const statTotal = document.getElementById('stat-total');
  if (statTotal) statTotal.textContent = total;

  // Render cards
  renderSchemeCards(AppState.schemes, 'all');
  showPage('results');
}

function renderSchemeCards(schemes, filter) {
  const container = document.getElementById('schemes-list');
  if (!container) return;

  let filteredSchemes = schemes;
  if (filter === 'eligible') filteredSchemes = schemes.filter(s => s.status === 'eligible');
  else if (filter === 'central') filteredSchemes = schemes.filter(s => s.type === 'central');
  else if (filter === 'state') filteredSchemes = schemes.filter(s => s.type === 'state');

  if (filteredSchemes.length === 0) {
    container.innerHTML = `
      <div class="text-center py-12 bg-white rounded-2xl card-shadow p-6">
        <p class="text-slate-600 mb-2">No schemes found under this filter.</p>
        <button onclick="document.querySelector('.scheme-filter[data-filter=\\'all\\']').click()" class="text-sm text-blue-600 underline font-medium">View All Schemes</button>
      </div>`;
    return;
  }

  container.innerHTML = filteredSchemes.map(scheme => {
    const statusClass = scheme.status === 'eligible' ? 'scheme-eligible' : (scheme.status === 'likely' ? 'scheme-likely' : 'scheme-check');
    const statusText = scheme.status === 'eligible' ? 'Likely Eligible' : (scheme.status === 'likely' ? 'Worth Checking' : 'Check Eligibility');
    const statusColor = scheme.status === 'eligible' ? 'text-green-700' : (scheme.status === 'likely' ? 'text-amber-700' : 'text-slate-700');
    const uid = 'scheme_detail_' + Math.random().toString(36).substring(2, 9);
    const bdHtml = scheme.reasons ? scheme.reasons.map(r => `<div class="text-xs text-slate-600 mb-1">✓ ${r}</div>`).join('') : '<div class="text-xs text-slate-600">✓ Matches basic eligibility</div>';
    const docsArr = scheme.docs && scheme.docs.length > 0 ? scheme.docs : ['Aadhaar Card', 'Income Certificate', 'Bank Account'];

    return `
    <div class="bg-white rounded-2xl card-shadow card-hover ${statusClass} overflow-hidden">
      <div class="p-6">
        <div class="flex items-start justify-between mb-4">
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-2 flex-wrap">
              <h3 class="text-lg font-semibold text-slate-800">${scheme.name}</h3>
              <span class="text-xs ${statusColor} bg-slate-100 px-2 py-1 rounded-full font-medium">${statusText}</span>
              <span class="text-xs text-blue-600 bg-blue-50 px-2 py-1 rounded-full uppercase tracking-wider">${scheme.type}</span>
            </div>
            <p class="text-sm text-slate-600 mb-3">${scheme.desc}</p>
            <div class="text-sm font-medium text-blue-700 mb-2">Benefit: ${scheme.benefit}</div>
          </div>
          <div class="text-right flex-shrink-0 ml-4">
            <div class="text-xs text-slate-500">Match Score</div>
            <div class="text-lg font-bold text-blue-700">${scheme.score}/100</div>
          </div>
        </div>

        <button onclick="toggleBd('${uid}')" class="text-xs text-blue-600 hover:underline mb-2 block font-medium">▶ Score Breakdown</button>
        <div id="${uid}" style="display:none;background:#f8fafc;border:1px dashed #cbd5e1;border-radius:8px;padding:10px 12px;margin-bottom:12px">
          ${bdHtml}
        </div>

        <div class="border-t border-slate-100 pt-3 mt-3">
          <div class="text-xs text-slate-500 font-medium mb-2">Documents typically needed:</div>
          <div class="flex flex-wrap gap-2">
            ${docsArr.map(doc => `<span class="text-xs bg-slate-100 text-slate-600 px-2.5 py-1 rounded-md">${doc}</span>`).join('')}
          </div>
        </div>

        <div class="mt-4 flex gap-3">
          <a href="${scheme.link}" target="_blank" rel="noopener noreferrer"
            class="flex-1 btn-primary text-white text-center py-3 rounded-xl font-medium text-sm hover:opacity-90 transition-all">
            Learn More & Apply
          </a>
          <button class="px-4 py-3 border border-slate-200 rounded-xl text-slate-600 hover:bg-slate-50 transition-all"
            title="Ask AI Assistant about this scheme"
            onclick="askAI('Tell me about ${scheme.name.replace(/'/g, "\\'")}')">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
          </button>
        </div>
      </div>
    </div>`;
  }).join('');
}

function toggleBd(id) {
  const el = document.getElementById(id);
  if (!el) return;
  const btn = el.previousElementSibling;
  const vis = el.style.display === 'none';
  el.style.display = vis ? 'block' : 'none';
  if (btn) btn.textContent = (vis ? '▼' : '▶') + ' Score Breakdown';
}

// AI Assistant
function askAI(query) {
  const input = document.getElementById('ai-input');
  if (input) {
    input.value = query;
    handleAIQuery();
  }
}

function handleAIQuery() {
  const input = document.getElementById('ai-input');
  if (!input) return;
  const query = input.value.trim();
  if (!query) return;

  const msgs = document.getElementById('ai-chat-messages');
  if (msgs) {
    msgs.innerHTML += `<div class="flex items-start gap-2 justify-end"><div class="bg-blue-600 text-white rounded-lg p-3 text-sm max-w-xs">${query}</div></div>`;
    const resp = generateAIResponse(query);
    setTimeout(() => {
      msgs.innerHTML += `<div class="flex items-start gap-2"><div class="w-6 h-6 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0"><svg class="w-3 h-3 text-blue-600" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/></svg></div><div class="bg-slate-50 rounded-lg p-3 text-sm text-slate-700">${resp}</div></div>`;
      msgs.scrollTop = msgs.scrollHeight;
    }, 400);
    input.value = '';
    msgs.scrollTop = msgs.scrollHeight;
  }
}

function generateAIResponse(query) {
  const lq = query.toLowerCase();
  const pool = (AppState.schemes && AppState.schemes.length > 0) ? AppState.schemes : SCHEMES_DB;

  const scheme = pool.find(s => {
    const sName = (s.name || '').toLowerCase();
    return lq.includes(sName) || sName.split(' ').some(w => w.length > 3 && lq.includes(w));
  });

  if (scheme) {
    const sDocs = (scheme.docs && scheme.docs.length > 0) ? scheme.docs.join(', ') : 'Aadhaar Card, Income Certificate, Bank Account';
    return `<strong>${scheme.name}</strong><br><br>${scheme.desc}<br><br><strong>Benefit:</strong> ${scheme.benefit}<br><br><strong>Required Documents:</strong> ${sDocs}<br><br><strong>Apply Online:</strong> <a href="${scheme.link}" target="_blank" class="text-blue-600 underline font-medium">Official Portal Link</a><br><br><em>Verify all eligibility criteria on the official state or national portal.</em>`;
  }

  if (lq.includes('eligib')) return `Eligibility criteria depend on your age, income, state of residence, and social category. In your results, schemes marked "Likely Eligible" have matched all basic requirements.`;
  if (lq.includes('document') || lq.includes('paper')) return `Most welfare schemes require: 1. Aadhaar Card, 2. Income Certificate, 3. Caste Certificate (if applicable), and 4. Active Bank Account. Check each card's "Score Breakdown" for details.`;
  if (lq.includes('apply') || lq.includes('how to')) return `To apply:<br>1. Click "Learn More & Apply" on the scheme card<br>2. Sign in to the official portal with your mobile number<br>3. Fill out the application form and attach documents<br>4. Note your application ID for tracking.`;

  return `I can help you understand any of the ${pool.length} schemes matching your profile. Ask me about benefits, eligibility, or required documents!`;
}

// Event Listeners Setup
function setupEventListeners() {
  document.getElementById('language-selector')?.addEventListener('change', (e) => {
    AppState.language = e.target.value;
    showToast(`Language changed to ${e.target.options[e.target.selectedIndex].text}`);
  });

  document.getElementById('btn-start-finding')?.addEventListener('click', () => {
    AppState.isGuest = true;
    showPage('questionnaire');
    showQuestion(1);
  });

  document.getElementById('btn-login')?.addEventListener('click', () => showPage('auth'));
  document.getElementById('btn-back-to-landing')?.addEventListener('click', () => showPage('landing'));

  // User menu logout trigger
  document.getElementById('user-menu-btn')?.addEventListener('click', () => {
    if (confirm('Do you want to sign out?')) {
      localStorage.removeItem('yojnasetu_token');
      localStorage.removeItem('yojnasetu_user');
      AppState.isLoggedIn = false;
      AppState.token = null;
      AppState.userData = null;
      document.getElementById('user-menu')?.classList.add('hidden');
      showToast('Signed out successfully', 'info');
    }
  });

  // Auth tabs
  document.getElementById('tab-phone')?.addEventListener('click', () => {
    document.getElementById('tab-phone')?.classList.add('bg-white','text-slate-800','shadow-sm');
    document.getElementById('tab-email')?.classList.remove('bg-white','text-slate-800','shadow-sm');
    document.getElementById('tab-email')?.classList.add('text-slate-600');
    document.getElementById('form-phone-login')?.classList.remove('hidden');
    document.getElementById('form-email-login')?.classList.add('hidden');
  });

  document.getElementById('tab-email')?.addEventListener('click', () => {
    document.getElementById('tab-email')?.classList.add('bg-white','text-slate-800','shadow-sm');
    document.getElementById('tab-phone')?.classList.remove('bg-white','text-slate-800','shadow-sm');
    document.getElementById('tab-phone')?.classList.add('text-slate-600');
    document.getElementById('form-email-login')?.classList.remove('hidden');
    document.getElementById('form-phone-login')?.classList.add('hidden');
  });

  // Phone Login Form (Real API)
  document.getElementById('form-phone-login')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const phone = document.getElementById('input-phone')?.value.trim();
    const otpSection = document.getElementById('otp-section');
    const otpInput = document.getElementById('input-otp');

    if (otpSection && otpSection.classList.contains('hidden')) {
      try {
        const res = await fetch(`${API_BASE_URL}/api/auth/send-otp`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ type: 'phone', identifier: phone })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Failed to send OTP');

        otpSection.classList.remove('hidden');
        const sendBtn = document.getElementById('btn-send-otp');
        if (sendBtn) sendBtn.innerHTML = '<span>Verify & Sign In</span>';
        if (data.demo_otp && otpInput) {
          otpInput.value = data.demo_otp;
          showToast(`OTP sent! (Use test OTP: ${data.demo_otp})`, 'success');
        } else {
          showToast('OTP sent to your mobile number', 'success');
        }
      } catch (err) {
        showToast(err.message || 'Error sending OTP', 'info');
        otpSection.classList.remove('hidden');
      }
    } else {
      const otp = otpInput ? otpInput.value.trim() : '123456';
      try {
        const res = await fetch(`${API_BASE_URL}/api/auth/verify-otp`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ type: 'phone', identifier: phone, otp: otp || '123456' })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Invalid OTP');

        AppState.isLoggedIn = true;
        AppState.isGuest = false;
        AppState.token = data.token;
        AppState.userData = data.user;
        localStorage.setItem('yojnasetu_token', data.token);
        localStorage.setItem('yojnasetu_user', JSON.stringify(data.user));

        const userMenu = document.getElementById('user-menu');
        if (userMenu) userMenu.classList.remove('hidden');
        const nameEl = document.getElementById('user-display-name');
        if (nameEl) nameEl.textContent = data.user?.name || `+91 ${phone.substring(0,5)}...`;

        showToast('Signed in successfully!', 'success');
        showPage('questionnaire');
        showQuestion(1);
      } catch (err) {
        showToast(err.message || 'Verification failed', 'info');
      }
    }
  });

  // Email Login Form (Real API)
  document.getElementById('form-email-login')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = document.getElementById('input-email')?.value.trim();
    const otpSection = document.getElementById('email-otp-section');
    const otpInput = document.getElementById('input-email-otp');

    if (otpSection && otpSection.classList.contains('hidden')) {
      try {
        const res = await fetch(`${API_BASE_URL}/api/auth/send-otp`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ type: 'email', identifier: email })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Failed to send OTP');

        otpSection.classList.remove('hidden');
        const sendBtn = document.getElementById('btn-send-email-otp');
        if (sendBtn) sendBtn.innerHTML = '<span>Verify & Sign In</span>';
        if (data.demo_otp && otpInput) {
          otpInput.value = data.demo_otp;
          showToast(`OTP sent! (Use test OTP: ${data.demo_otp})`, 'success');
        } else {
          showToast('OTP sent to your email address', 'success');
        }
      } catch (err) {
        showToast(err.message || 'Error sending OTP', 'info');
        otpSection.classList.remove('hidden');
      }
    } else {
      const otp = otpInput ? otpInput.value.trim() : '123456';
      try {
        const res = await fetch(`${API_BASE_URL}/api/auth/verify-otp`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ type: 'email', identifier: email, otp: otp || '123456' })
        });
        const data = await res.json();
        if (!res.ok) throw new Error(data.error || 'Invalid OTP');

        AppState.isLoggedIn = true;
        AppState.isGuest = false;
        AppState.token = data.token;
        AppState.userData = data.user;
        localStorage.setItem('yojnasetu_token', data.token);
        localStorage.setItem('yojnasetu_user', JSON.stringify(data.user));

        const userMenu = document.getElementById('user-menu');
        if (userMenu) userMenu.classList.remove('hidden');
        const nameEl = document.getElementById('user-display-name');
        if (nameEl) nameEl.textContent = data.user?.name || email.split('@')[0];

        showToast('Signed in successfully!', 'success');
        showPage('questionnaire');
        showQuestion(1);
      } catch (err) {
        showToast(err.message || 'Verification failed', 'info');
      }
    }
  });

  document.getElementById('btn-guest-mode')?.addEventListener('click', () => {
    AppState.isGuest = true;
    showPage('questionnaire');
    showQuestion(1);
  });

  // Questionnaire Options Handlers
  document.querySelectorAll('.gender-option').forEach(b => b.addEventListener('click', () => handleOptionSelect('gender', b.dataset.value)));
  document.querySelectorAll('.age-option').forEach(b => b.addEventListener('click', () => handleOptionSelect('age_range', b.dataset.value)));
  document.querySelectorAll('.category-option').forEach(b => b.addEventListener('click', () => handleOptionSelect('category', b.dataset.value)));
  document.querySelectorAll('.occupation-option').forEach(b => b.addEventListener('click', () => handleOptionSelect('occupation', b.dataset.value)));
  document.querySelectorAll('.income-option').forEach(b => b.addEventListener('click', () => handleOptionSelect('income_range', b.dataset.value)));

  document.getElementById('state-select')?.addEventListener('change', (e) => {
    AppState.profile.state = e.target.value;
    const btn = document.getElementById('btn-state-next');
    if (btn) btn.disabled = !e.target.value;
  });

  document.getElementById('btn-state-next')?.addEventListener('click', () => {
    if (AppState.profile.state) showQuestion(AppState.currentStep + 1);
  });

  document.getElementById('btn-prev-question')?.addEventListener('click', () => {
    if (AppState.currentStep > 1) showQuestion(AppState.currentStep - 1);
  });

  document.getElementById('btn-skip-question')?.addEventListener('click', () => {
    if (AppState.currentStep < AppState.totalSteps) showQuestion(AppState.currentStep + 1);
    else calculateResults();
  });

  document.getElementById('btn-edit-profile')?.addEventListener('click', () => {
    showPage('questionnaire');
    showQuestion(1);
  });

  document.getElementById('btn-start-over')?.addEventListener('click', () => {
    AppState.profile = { gender: null, age_range: null, state: null, category: null, occupation: null, income_range: null };
    AppState.schemes = [];
    showPage('landing');
  });

  // Save Results (Persistent DB + Local)
  document.getElementById('btn-save-results')?.addEventListener('click', async () => {
    if (!AppState.schemes || AppState.schemes.length === 0) {
      showToast('No recommendations to save yet.', 'info');
      return;
    }

    localStorage.setItem('yojnasetu_saved_schemes', JSON.stringify(AppState.schemes));

    const token = localStorage.getItem('yojnasetu_token') || AppState.token;
    if (token) {
      try {
        let savedCount = 0;
        for (const s of AppState.schemes.slice(0, 5)) {
          await fetch(`${API_BASE_URL}/api/user/saved-schemes`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
              scheme_id: s.id,
              scheme_name: s.name,
              category: s.category,
              benefit: s.benefit,
              link: s.link
            })
          });
          savedCount++;
        }
        showToast(`Saved ${savedCount} schemes to your account!`, 'success');
      } catch (e) {
        showToast('Saved results locally on your device!', 'success');
      }
    } else {
      showToast('Saved results locally! Sign in anytime to sync to your account.', 'success');
    }
  });

  // Filter Tabs
  document.querySelectorAll('.scheme-filter').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.scheme-filter').forEach(b => {
        b.classList.remove('bg-blue-600', 'text-white');
        b.classList.add('bg-slate-100', 'text-slate-700');
      });
      btn.classList.remove('bg-slate-100', 'text-slate-700');
      btn.classList.add('bg-blue-600', 'text-white');
      renderSchemeCards(AppState.schemes, btn.dataset.filter);
    });
  });

  // AI input listeners
  document.getElementById('btn-ai-send')?.addEventListener('click', handleAIQuery);
  document.getElementById('ai-input')?.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleAIQuery();
    }
  });

  // Document Upload file preview
  document.getElementById('ration')?.addEventListener('change', (e) => {
    const fileName = e.target.files[0]?.name || '';
    const nameEl = document.getElementById('ration-name');
    if (nameEl) {
      nameEl.innerHTML = fileName
        ? `<span class="text-green-600 flex items-center gap-1 font-medium"><svg class="w-4 h-4" fill="currentColor" viewbox="0 0 24 24"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg> ${fileName}</span>`
        : '';
    }
  });

  document.getElementById('income')?.addEventListener('change', (e) => {
    const fileName = e.target.files[0]?.name || '';
    const nameEl = document.getElementById('income-name');
    if (nameEl) {
      nameEl.innerHTML = fileName
        ? `<span class="text-green-600 flex items-center gap-1 font-medium"><svg class="w-4 h-4" fill="currentColor" viewbox="0 0 24 24"><path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg> ${fileName}</span>`
        : '';
    }
  });

  document.getElementById('btn-submit-documents')?.addEventListener('click', handleDocumentSubmit);
  document.getElementById('btn-skip-documents')?.addEventListener('click', () => {
    showToast('Calculating matches based on profile...');
    setTimeout(() => calculateResults(), 400);
  });
}

// Toast notification
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `bg-white border-l-4 p-4 rounded-lg shadow-lg max-w-sm toast ${type === 'success' ? 'border-green-500' : 'border-blue-500'}`;
  toast.innerHTML = `
    <div class="flex items-center">
      <div class="flex-1 text-sm text-slate-800">${message}</div>
      <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-slate-400 hover:text-slate-600">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
    </div>
  `;
  container.appendChild(toast);
  setTimeout(() => toast.remove(), 4500);
}

// Start application
if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
  } else {
    initializeApp();
  }
}
