/**
 * Coffee RAG System - Frontend Logic
 */

document.addEventListener('DOMContentLoaded', () => {
    initQueryForm();
    initDemoActions();
    initModal();
    initProviderToggle();
});

/**
 * Get currently selected LLM provider from the toggle
 */
function getSelectedProvider() {
    const selected = document.querySelector('input[name="llm-provider"]:checked');
    return selected ? selected.value : 'gemini';
}

/**
 * Handle Provider Toggle state & persistence
 */
function initProviderToggle() {
    const saved = localStorage.getItem('llm-provider');
    if (saved) {
        const radio = document.querySelector(`input[name="llm-provider"][value="${saved}"]`);
        if (radio) radio.checked = true;
    }

    document.querySelectorAll('input[name="llm-provider"]').forEach(radio => {
        radio.addEventListener('change', (e) => {
            localStorage.setItem('llm-provider', e.target.value);
            console.log("LLM Provider switched to:", e.target.value);
        });
    });
}

/**
 * Handle CNN Pending Modal
 */
function initModal() {
    const modal = document.getElementById("cnnModal");
    const btn = document.getElementById("cnn-card");
    const span = document.getElementsByClassName("close-modal")[0];

    if (!btn || !modal) return;

    btn.onclick = function() {
        modal.style.display = "block";
    }

    span.onclick = function() {
        modal.style.display = "none";
    }

    window.onclick = function(event) {
        if (event.target == modal) {
            modal.style.display = "none";
        }
    }
}

/**
 * Handle Single-Question Query page
 */
function initQueryForm() {
    const form = document.getElementById('query-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const queryInput = document.getElementById('query-input');
        const query = queryInput.value.trim();
        if (!query) return;

        const loading = document.getElementById('loading');
        const results = document.getElementById('results');
        
        loading.style.display = 'block';
        results.innerHTML = '';

        try {
            const response = await fetch('/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    query,
                    provider: getSelectedProvider()
                })
            });
            const data = await response.json();
            
            loading.style.display = 'none';
            if (data.error) {
                results.innerHTML = `<div class="card"><p style="color:red">Error: ${data.error}</p></div>`;
            } else {
                // data is now a list of Results
                results.innerHTML = `
                    <div style="margin-top: 40px; margin-bottom: 20px;">
                        <h2 style="font-size: 24px; font-weight: 700;">Top 3 Agricultural Insights</h2>
                        <p style="color: var(--text-secondary);">Expert answers based on ranked RAG knowledge.</p>
                    </div>
                `;
                
                data.slice(0, 3).forEach((r, idx) => {
                    const htmlAnswer = marked.parse(r.answer);
                    results.innerHTML += `
                        <div class="card answer-card" style="margin-top: 20px;">
                            <div class="result-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
                                <div style="display:flex; align-items:center;">
                                    <span class="rank-badge">#${idx + 1}</span>
                                    <h3 style="margin:0">Insight</h3>
                                </div>
                                <span class="confidence">Confidence: ${(r.confidence * 100).toFixed(1)}%</span>
                            </div>
                            <div class="formatted-answer">${htmlAnswer}</div>
                            ${r.sources.length ? `
                                <div class="sources">
                                    <h4>Sources</h4>
                                    <ul>${r.sources.map(s => `<li>${s}</li>`).join('')}</ul>
                                </div>
                            ` : ''}
                        </div>
                    `;
                });
            }
        } catch (err) {
            loading.style.display = 'none';
            results.innerHTML = `<div class="card"><p style="color:red">Connection error: ${err.message}</p></div>`;
        }
    });

    const clearBtn = document.getElementById('btn-clear-query');
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            const queryInput = document.getElementById('query-input');
            const results = document.getElementById('results');
            if (queryInput) queryInput.value = '';
            if (results) results.innerHTML = '';
        });
    }
}

/**
 * Handle Demo Simulation page
 */
function initDemoActions() {
    const demoContainer = document.getElementById('demo-scenarios');
    if (!demoContainer) return;

    // Attach listener for specific scenario runs
    document.querySelectorAll('.btn-run-demo').forEach(btn => {
        btn.addEventListener('click', async (e) => {
            const mode = btn.dataset.mode;
            const index = parseInt(btn.dataset.index);
            const card = btn.closest('.card');
            const resultArea = card.querySelector('.scenario-result');
            
            btn.disabled = true;
            btn.textContent = 'Simulating...';
            resultArea.innerHTML = '<p class="loading-small">Processing RAG pipeline...</p>';

            const results = await runDemo(mode, index);
            renderDemoResults(results, resultArea);
            
            btn.disabled = false;
            btn.textContent = 'Run Scenario';
        });
    });

    // Attach listener for individual scenario clear
    document.querySelectorAll('.btn-clear-scenario').forEach(btn => {
        btn.addEventListener('click', () => {
            const card = btn.closest('.card');
            const resultArea = card.querySelector('.scenario-result');
            if (resultArea) resultArea.innerHTML = '';
        });
    });

    // Attach listener for "Run All"
    const runAllBtn = document.getElementById('btn-run-all');
    if (runAllBtn) {
        runAllBtn.addEventListener('click', async () => {
            const globalResult = document.getElementById('all-results');
            runAllBtn.disabled = true;
            runAllBtn.textContent = 'Simulating All...';
            
            globalResult.innerHTML = '<div class="loading" style="display:block">Running all scenarios through vector store and Gemini...</div>';
            
            // Run CNN all
            const cnnResults = await runDemo('cnn', 'all');
            // Run Query all
            const queryResults = await runDemo('query', 'all');
            
            globalResult.innerHTML = '<h2>Simulation Results</h2>';
            renderDemoResults([...cnnResults, ...queryResults], globalResult, true);
            
            runAllBtn.disabled = false;
            runAllBtn.textContent = 'Run All Scenarios';
        });
    }

    // Attach listener for "Clear All"
    const clearAllBtn = document.getElementById('btn-clear-all');
    if (clearAllBtn) {
        clearAllBtn.addEventListener('click', () => {
            const globalResult = document.getElementById('all-results');
            if (globalResult) globalResult.innerHTML = '';
            document.querySelectorAll('.scenario-result').forEach(area => {
                area.innerHTML = '';
            });
        });
    }
}

async function runDemo(mode, index) {
    try {
        const response = await fetch('/run_demo', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                mode, 
                index,
                provider: getSelectedProvider()
            })
        });
        return await response.json();
    } catch (err) {
        console.error(err);
        return [];
    }
}

function renderDemoResults(results, container, isFullList = false) {
    if (!results || results.length === 0) {
        container.innerHTML = '<p>No results returned.</p>';
        return;
    }

    let currentIdx = 0;
    const html = results.map(res => {
        const htmlAnswer = marked.parse(res.answer);
        // Only show # rank if there are multiple results for the same scenario (Mode 2)
        // or for each demo item if you prefer. Here we use it for clarity in all demos.
        currentIdx++;
        return `
            <div class="result-card" style="margin-top: 16px;">
                <div style="display:flex; justify-content:space-between; align-items:start;">
                    <div style="display:flex; align-items:center;">
                         <span class="rank-badge">#${currentIdx}</span>
                         <span class="label">${res.disease ? 'Mode 1: CNN' : 'Mode 2: Query'}</span>
                    </div>
                    <div style="display:flex; gap:8px;">
                        <span class="confidence" style="background:#f5f5f7; color:#1d1d1f; border:1px solid #d2d2d7; padding:2px 8px; border-radius:4px; font-size:11px;">
                            ${res.disease ? 'CNN: ' : 'RAG: '}${typeof res.confidence === 'string' ? res.confidence : (res.confidence * 100).toFixed(1) + '%'}
                        </span>
                        ${res.confidence_rag ? `
                            <span class="confidence" style="background:#000; color:#fff; padding:2px 8px; border-radius:4px; font-size:11px;">
                                RAG: ${(res.confidence_rag * 100).toFixed(1)}%
                            </span>
                        ` : ''}
                    </div>
                </div>
                <h4 style="margin-top:12px;">${res.disease ? res.disease : res.question}</h4>
                ${res.env && Object.keys(res.env).length ? `
                    <div class="metadata">
                        ${Object.entries(res.env).map(([key, value]) => `
                            <span>${key}: ${value}</span>
                        `).join('')}
                    </div>
                ` : ''}
                <div class="answer formatted-answer">
                    ${htmlAnswer}
                </div>
                ${res.sources && res.sources.length ? `
                    <div class="sources">
                        <ul>${res.sources.map(s => `<li>${s}</li>`).join('')}</ul>
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');

    if (isFullList) {
        container.innerHTML += html;
    } else {
        container.innerHTML = html;
    }
}
