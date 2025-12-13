/**
 * Healthcare Telemedicine AI - Frontend Application
 */

// Configuration
const API_BASE_URL = 'http://localhost:8000/api';

// State
let currentSessionId = null;
let selectedFile = null;

// DOM Elements
const views = document.querySelectorAll('.view');
const navButtons = document.querySelectorAll('.nav-btn');
const loadingOverlay = document.getElementById('loading-overlay');

// ============== Navigation ==============

navButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        const viewId = btn.dataset.view;
        switchView(viewId);
    });
});

function switchView(viewId) {
    // Update nav buttons
    navButtons.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.view === viewId);
    });

    // Update views
    views.forEach(view => {
        view.classList.toggle('active', view.id === viewId);
    });
}

// ============== Symptom Checker ==============

const assessBtn = document.getElementById('assess-btn');
const symptomsInput = document.getElementById('symptoms');
const ageInput = document.getElementById('age');
const genderSelect = document.getElementById('gender');
const medicalHistoryInput = document.getElementById('medical-history');
const medicationsInput = document.getElementById('medications');
const assessmentResults = document.getElementById('assessment-results');

assessBtn.addEventListener('click', assessSymptoms);

async function assessSymptoms() {
    const symptoms = symptomsInput.value.trim();
    
    if (!symptoms) {
        alert('Please describe your symptoms');
        return;
    }

    // Prepare request data
    const requestData = {
        symptoms: symptoms,
        age: ageInput.value ? parseInt(ageInput.value) : null,
        gender: genderSelect.value || null,
        medical_history: medicalHistoryInput.value 
            ? medicalHistoryInput.value.split(',').map(s => s.trim()) 
            : [],
        current_medications: medicationsInput.value 
            ? medicationsInput.value.split(',').map(s => s.trim()) 
            : []
    };

    try {
        showLoading();
        setButtonLoading(assessBtn, true);

        const response = await fetch(`${API_BASE_URL}/symptoms/assess`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestData)
        });

        if (!response.ok) {
            throw new Error('Assessment failed');
        }

        const result = await response.json();
        displayAssessmentResults(result);

    } catch (error) {
        console.error('Assessment error:', error);
        alert('Failed to process assessment. Please try again.');
    } finally {
        hideLoading();
        setButtonLoading(assessBtn, false);
    }
}

function displayAssessmentResults(result) {
    // Show results container
    assessmentResults.classList.remove('hidden');

    // Risk badge
    const riskBadge = document.getElementById('risk-badge');
    riskBadge.textContent = `${result.risk_level.toUpperCase()} RISK (${result.risk_score}/100)`;
    riskBadge.className = `risk-badge ${result.risk_level}`;

    // Conditions
    const conditionsList = document.getElementById('conditions-list');
    conditionsList.innerHTML = result.possible_conditions.map(c => `
        <li>
            <strong>${c.name}</strong> 
            <span class="likelihood">(${c.likelihood})</span>
            <br><small>${c.description}</small>
        </li>
    `).join('');

    // Follow-up questions
    const questionsList = document.getElementById('questions-list');
    questionsList.innerHTML = result.follow_up_questions.map(q => `
        <li>${q}</li>
    `).join('');

    // Recommendations
    const recommendationsList = document.getElementById('recommendations-list');
    recommendationsList.innerHTML = result.recommendations.map(r => `
        <li>${r}</li>
    `).join('');

    // Urgency level
    const urgencyLevel = document.getElementById('urgency-level');
    urgencyLevel.textContent = result.urgency.replace('-', ' ').toUpperCase();
    urgencyLevel.className = result.urgency;

    // Scroll to results
    assessmentResults.scrollIntoView({ behavior: 'smooth' });
}

// Triage button
document.getElementById('triage-btn')?.addEventListener('click', async () => {
    alert('Triage request submitted. A healthcare provider will contact you shortly.');
});

// Chat button in results
document.getElementById('chat-btn')?.addEventListener('click', () => {
    switchView('chat');
});

// ============== Chat ==============

const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const chatSuggestions = document.getElementById('chat-suggestions');

sendBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

// Suggestion buttons
chatSuggestions.addEventListener('click', (e) => {
    if (e.target.classList.contains('suggestion-btn')) {
        chatInput.value = e.target.textContent;
        sendMessage();
    }
});

async function sendMessage() {
    const message = chatInput.value.trim();
    
    if (!message) return;

    // Add user message to chat
    addMessage('user', message);
    chatInput.value = '';

    try {
        const response = await fetch(`${API_BASE_URL}/chat/message`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                message: message,
                session_id: currentSessionId
            })
        });

        if (!response.ok) {
            throw new Error('Chat request failed');
        }

        const result = await response.json();
        
        // Update session ID
        currentSessionId = result.session_id;

        // Add assistant response
        addMessage('assistant', result.response);

        // Update suggestions
        updateSuggestions(result.suggestions);

        // Handle human handoff
        if (result.requires_human) {
            addMessage('assistant', '🔔 A human representative will be connected shortly.');
        }

    } catch (error) {
        console.error('Chat error:', error);
        addMessage('assistant', 'Sorry, I\'m having trouble connecting. Please try again.');
    }
}

function addMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    const contentDiv = document.createElement('div');
    contentDiv.className = 'message-content';
    contentDiv.innerHTML = formatMessage(content);
    
    messageDiv.appendChild(contentDiv);
    chatMessages.appendChild(messageDiv);
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function formatMessage(content) {
    // Convert markdown-like formatting
    return content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\n/g, '<br>')
        .replace(/- (.*?)(?=<br>|$)/g, '<li>$1</li>')
        .replace(/(<li>.*<\/li>)+/g, '<ul>$&</ul>');
}

function updateSuggestions(suggestions) {
    if (!suggestions || suggestions.length === 0) return;
    
    chatSuggestions.innerHTML = suggestions.map(s => `
        <button class="suggestion-btn">${s}</button>
    `).join('');
}

// ============== Document Analysis ==============

const uploadArea = document.getElementById('upload-area');
const fileInput = document.getElementById('file-input');
const docTypeSelect = document.getElementById('doc-type');
const analyzeBtn = document.getElementById('analyze-btn');
const docResults = document.getElementById('doc-results');

// File upload handling
uploadArea.addEventListener('click', () => fileInput.click());

uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

function handleFileSelect(file) {
    // Validate file type
    const validTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'];
    if (!validTypes.includes(file.type)) {
        alert('Please upload a PDF or image file (PNG, JPG)');
        return;
    }

    selectedFile = file;
    uploadArea.classList.add('has-file');
    uploadArea.querySelector('p').textContent = `Selected: ${file.name}`;
    analyzeBtn.disabled = false;
}

analyzeBtn.addEventListener('click', analyzeDocument);

async function analyzeDocument() {
    if (!selectedFile) {
        alert('Please select a document first');
        return;
    }

    try {
        showLoading();
        setButtonLoading(analyzeBtn, true);

        // In a real implementation, you would:
        // 1. Upload the file to S3
        // 2. Get the S3 URL
        // 3. Call the analyze endpoint

        // For demo, we'll simulate the API call
        const response = await fetch(`${API_BASE_URL}/documents/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                document_url: `s3://telemedicine-documents/${selectedFile.name}`,
                document_type: docTypeSelect.value
            })
        });

        if (!response.ok) {
            throw new Error('Analysis failed');
        }

        const result = await response.json();
        displayDocumentResults(result);

    } catch (error) {
        console.error('Document analysis error:', error);
        // Show demo results for testing
        displayDocumentResults(getDemoDocumentResults());
    } finally {
        hideLoading();
        setButtonLoading(analyzeBtn, false);
    }
}

function displayDocumentResults(result) {
    docResults.classList.remove('hidden');

    // Summary
    document.getElementById('doc-summary').textContent = result.summary;

    // Key findings
    const findingsList = document.getElementById('findings-list');
    findingsList.innerHTML = result.key_findings.map(f => `<li>${f}</li>`).join('');

    // Medications
    const medicationsList = document.getElementById('medications-list');
    const meds = result.extracted_entities?.medications || [];
    medicationsList.innerHTML = meds.length > 0 
        ? meds.map(m => `<li>${m.text || m}</li>`).join('')
        : '<li>No medications found</li>';

    // Conditions
    const conditionsList = document.getElementById('doc-conditions-list');
    const conditions = result.extracted_entities?.conditions || [];
    conditionsList.innerHTML = conditions.length > 0
        ? conditions.map(c => `<li>${c.text || c}</li>`).join('')
        : '<li>No conditions found</li>';

    // Recommendations
    const recommendationsList = document.getElementById('doc-recommendations-list');
    recommendationsList.innerHTML = result.recommendations.map(r => `<li>${r}</li>`).join('');

    // Flags
    const flagsContainer = document.getElementById('doc-flags');
    const flagsList = document.getElementById('flags-list');
    
    if (result.flags && result.flags.length > 0) {
        flagsContainer.classList.remove('hidden');
        flagsList.innerHTML = result.flags.map(f => `<li>⚠️ ${f}</li>`).join('');
    } else {
        flagsContainer.classList.add('hidden');
    }

    // Scroll to results
    docResults.scrollIntoView({ behavior: 'smooth' });
}

function getDemoDocumentResults() {
    return {
        analysis_id: 'demo-123',
        document_type: docTypeSelect.value,
        summary: 'This document contains lab results showing routine blood work. Most values are within normal ranges with a few items requiring attention.',
        key_findings: [
            'Complete Blood Count (CBC) within normal limits',
            'Cholesterol levels slightly elevated',
            'Blood glucose levels normal',
            'Kidney function tests normal'
        ],
        extracted_entities: {
            medications: [
                { text: 'Metformin 500mg' },
                { text: 'Lisinopril 10mg' }
            ],
            conditions: [
                { text: 'Type 2 Diabetes' },
                { text: 'Hypertension' }
            ]
        },
        recommendations: [
            'Follow up with primary care physician regarding cholesterol levels',
            'Continue current medication regimen',
            'Repeat lipid panel in 3 months'
        ],
        flags: [
            'LDL Cholesterol: 145 mg/dL (above optimal range)'
        ]
    };
}

// ============== Utility Functions ==============

function showLoading() {
    loadingOverlay.classList.remove('hidden');
}

function hideLoading() {
    loadingOverlay.classList.add('hidden');
}

function setButtonLoading(button, isLoading) {
    const btnText = button.querySelector('.btn-text');
    const btnLoading = button.querySelector('.btn-loading');
    
    if (isLoading) {
        btnText?.classList.add('hidden');
        btnLoading?.classList.remove('hidden');
        button.disabled = true;
    } else {
        btnText?.classList.remove('hidden');
        btnLoading?.classList.add('hidden');
        button.disabled = false;
    }
}

// ============== Initialize ==============

document.addEventListener('DOMContentLoaded', () => {
    console.log('Healthcare Telemedicine AI initialized');
    
    // Generate session ID for chat
    currentSessionId = 'session-' + Date.now();
});
