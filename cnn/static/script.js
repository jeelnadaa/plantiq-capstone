document.addEventListener('DOMContentLoaded', () => {
    
    // --- Layout Elements ---
    const toggleSidebarBtn = document.getElementById('toggle-sidebar-btn');
    const historySidebar = document.getElementById('history-sidebar');
    const clearHistoryBtn = document.getElementById('clear-history-btn');
    const historyList = document.getElementById('history-list');

    // Modals
    const imageModal = document.getElementById('image-modal');
    const modalImage = document.getElementById('modal-image');
    const closeModalBtn = document.getElementById('close-modal-btn');

    const confirmModal = document.getElementById('confirm-modal');
    const cancelClearBtn = document.getElementById('cancel-clear-btn');
    const confirmClearBtn = document.getElementById('confirm-clear-btn');

    // Initialize History on Load
    loadHistory();

    // Sidebar Toggle
    if (toggleSidebarBtn) {
        toggleSidebarBtn.addEventListener('click', () => {
            historySidebar.classList.toggle('expanded');
        });
    }

    // Modal Listeners
    if (closeModalBtn) {
        closeModalBtn.addEventListener('click', () => imageModal.classList.add('hidden'));
        imageModal.addEventListener('click', (e) => {
            if (e.target === imageModal) imageModal.classList.add('hidden');
        });
    }

    if (clearHistoryBtn) {
        clearHistoryBtn.addEventListener('click', () => {
            confirmModal.classList.remove('hidden');
        });
        cancelClearBtn.addEventListener('click', () => confirmModal.classList.add('hidden'));
        confirmClearBtn.addEventListener('click', () => {
            localStorage.removeItem('plantiq_history');
            loadHistory();
            confirmModal.classList.add('hidden');
        });
    }

    // --- Upload Elements (for index page only) ---
    const dropZone = document.getElementById('drop-zone');
    if (dropZone) {
        const fileInput = document.getElementById('file-input');
        const predictLoading = document.getElementById('predict-loading');
        
        const overallSection = document.getElementById('overall-metrics-section');
        const resultsGrid = document.getElementById('individual-results-grid');
        
        const statTotal = document.getElementById('overall-total');
        const statDominant = document.getElementById('overall-dominant');
        const statHealthy = document.getElementById('overall-healthy');

        dropZone.addEventListener('click', () => fileInput.click());
        dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
        dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
        dropZone.addEventListener('drop', (e) => {
            e.preventDefault(); dropZone.classList.remove('dragover');
            if (e.dataTransfer.files.length > 0) handleFiles(e.dataTransfer.files);
        });
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) handleFiles(e.target.files);
        });

        async function handleFiles(files) {
            overallSection.classList.add('hidden');
            resultsGrid.classList.add('hidden');
            resultsGrid.innerHTML = '';
            predictLoading.style.display = 'block';

            const formData = new FormData();
            for (let i = 0; i < files.length; i++) {
                formData.append('files[]', files[i]);
            }

            try {
                const response = await fetch('/predict', { method: 'POST', body: formData });
                const data = await response.json();
                
                if (data.results) {
                    renderResults(data.results, files);
                } else {
                    alert(data.error || "An error occurred.");
                }
            } catch (error) {
                console.error(error);
                alert("Failed to connect to the server.");
            } finally {
                predictLoading.style.display = 'none';
            }
        }

        async function renderResults(results, files) {
            let classCounts = {};
            let healthyCount = 0;
            let validResults = 0;
            let batchImages = []; 

            // Create promises for thumbnail generation so batch saves simultaneously
            const promises = results.map(async (res, index) => {
                if (res.error) return;
                validResults++;

                const predClass = res.prediction.class;
                classCounts[predClass] = (classCounts[predClass] || 0) + 1;
                if (predClass === "Healthy") healthyCount++;

                const file = files[index];
                const url = URL.createObjectURL(file);

                const card = document.createElement('div');
                card.className = 'result-item';
                card.innerHTML = `
                    <img src="${url}" class="img-preview" alt="${res.filename}">
                    <div class="result-content">
                        <div class="result-filename" title="${res.filename}">${res.filename}</div>
                        <div class="predicted-class">${predClass}</div>
                        <div class="confidence">${res.prediction.confidence.toFixed(2)}% Match</div>
                    </div>
                `;
                
                card.querySelector('.img-preview').addEventListener('click', () => {
                    modalImage.src = url;
                    imageModal.classList.remove('hidden');
                });
                resultsGrid.appendChild(card);

                // Generate Base64 Thumb for batch
                const thumbData = await generateThumbnail(file);
                batchImages.push({
                    filename: res.filename,
                    class: predClass,
                    conf: res.prediction.confidence,
                    thumbnail: thumbData
                });
            });

            await Promise.all(promises);

            if (validResults > 0) {
                statTotal.textContent = validResults;
                let dom = Object.keys(classCounts).reduce((a, b) => classCounts[a] > classCounts[b] ? a : b);
                statDominant.textContent = dom;
                let ratio = (healthyCount / validResults) * 100;
                statHealthy.textContent = `${ratio.toFixed(0)}%`;

                overallSection.classList.remove('hidden');
                resultsGrid.classList.remove('hidden');

                // Save entire batch
                saveBatchToHistory(batchImages, dom);
            }
        }
    }

    // --- HTML5 Canvas Resizing Logic ---
    function generateThumbnail(file) {
        return new Promise((resolve) => {
            const reader = new FileReader();
            reader.onload = function(e) {
                const img = new Image();
                img.onload = function() {
                    const canvas = document.createElement('canvas');
                    const MAX_SIZE = 100; 
                    let width = img.width;
                    let height = img.height;

                    if (width > height) {
                        if (width > MAX_SIZE) { height *= MAX_SIZE / width; width = MAX_SIZE; }
                    } else {
                        if (height > MAX_SIZE) { width *= MAX_SIZE / height; height = MAX_SIZE; }
                    }

                    canvas.width = width;
                    canvas.height = height;
                    const ctx = canvas.getContext('2d');
                    ctx.drawImage(img, 0, 0, width, height);
                    resolve(canvas.toDataURL('image/jpeg', 0.6));
                }
                img.src = e.target.result;
            }
            reader.readAsDataURL(file);
        });
    }

    // --- Batched History Logic ---
    function saveBatchToHistory(imagesArray, dominantClass) {
        const batchItem = {
            id: 'batch_' + Date.now(),
            timestamp: new Date().toLocaleString(),
            dominant: dominantClass,
            total: imagesArray.length,
            images: imagesArray
        };
        
        let history = JSON.parse(localStorage.getItem('plantiq_history')) || [];
        history.unshift(batchItem);
        if (history.length > 20) history.pop(); // Keep last 20 batches
        
        localStorage.setItem('plantiq_history', JSON.stringify(history));
        loadHistory();
    }

    function loadHistory() {
        if (!historyList) return;
        historyList.innerHTML = '';
        let history = JSON.parse(localStorage.getItem('plantiq_history')) || [];
        
        if (history.length === 0) {
            historyList.innerHTML = '<p style="color:#86868b; text-align:center; margin-top:20px;">No recent analyses.</p>';
            return;
        }

        history.forEach(batch => {
            const el = document.createElement('div');
            el.className = 'batch-item';
            
            // Build thumbnails HTML
            let thumbsHtml = '';
            batch.images.slice(0, 5).forEach(img => {
                thumbsHtml += `<img src="${img.thumbnail}" class="batch-thumb" title="${img.class} (${img.conf.toFixed(1)}%)">`;
            });
            if (batch.images.length > 5) {
                thumbsHtml += `<div class="batch-thumb" style="display:flex;align-items:center;justify-content:center;background:#eee;font-weight:600;">+${batch.images.length - 5}</div>`;
            }

            el.innerHTML = `
                <div class="batch-header">
                    <div>
                        <div class="batch-title">Batch Analysis</div>
                        <div class="batch-time">${batch.timestamp}</div>
                    </div>
                    <button class="del-btn" data-id="${batch.id}" title="Remove Batch">&times;</button>
                </div>
                <div class="batch-imgs">
                    ${thumbsHtml}
                </div>
                <div class="batch-dominant">
                    <span>Dominant: ${batch.dominant}</span>
                    <span style="color:var(--text-secondary)">${batch.total} item(s)</span>
                </div>
            `;

            // Thumbnail modal trigger
            el.querySelectorAll('.batch-thumb[src]').forEach(img => {
                img.addEventListener('click', (e) => {
                    e.stopPropagation(); // Prevent batch render click
                    modalImage.src = e.target.src;
                    imageModal.classList.remove('hidden');
                });
            });

            // Batch Render trigger (clicking anywhere else on the item)
            el.addEventListener('click', () => {
                renderHistoryBatch(batch);
                // Optionally auto-collapse sidebar if browsing
                historySidebar.classList.remove('expanded');
            });

            // Delete batch
            el.querySelector('.del-btn').addEventListener('click', () => {
                let current = JSON.parse(localStorage.getItem('plantiq_history')) || [];
                current = current.filter(b => b.id !== batch.id);
                localStorage.setItem('plantiq_history', JSON.stringify(current));
                loadHistory();
            });

            historyList.appendChild(el);
        });
    }

    function renderHistoryBatch(batch) {
        const overallSection = document.getElementById('overall-metrics-section');
        const resultsGrid = document.getElementById('individual-results-grid');
        
        // If not on the analyze page, redirect or do nothing
        if (!resultsGrid) {
            window.location.href = '/'; 
            return;
        }

        resultsGrid.innerHTML = '';
        let healthyCount = 0;

        batch.images.forEach(res => {
            if (res.class === "Healthy") healthyCount++;

            const card = document.createElement('div');
            card.className = 'result-item';
            card.innerHTML = `
                <img src="${res.thumbnail}" class="img-preview" alt="${res.filename}">
                <div class="result-content">
                    <div class="result-filename" title="${res.filename}">${res.filename}</div>
                    <div class="predicted-class">${res.class}</div>
                    <div class="confidence">${res.conf.toFixed(2)}% Match</div>
                </div>
            `;
            
            card.querySelector('.img-preview').addEventListener('click', () => {
                modalImage.src = res.thumbnail;
                imageModal.classList.remove('hidden');
            });
            resultsGrid.appendChild(card);
        });

        document.getElementById('overall-total').textContent = batch.total;
        document.getElementById('overall-dominant').textContent = batch.dominant;
        document.getElementById('overall-healthy').textContent = `${((healthyCount / batch.total) * 100).toFixed(0)}%`;

        overallSection.classList.remove('hidden');
        resultsGrid.classList.remove('hidden');
    }

    // --- Evaluation Page Logic ---
    const evalBtn = document.getElementById('run-eval-btn');
    if (evalBtn) {
        const evalLoading = document.getElementById('eval-loading');
        const evalResults = document.getElementById('eval-results-container');
        let chartInstance = null;

        evalBtn.addEventListener('click', async () => {
            evalBtn.style.display = 'none';
            evalLoading.style.display = 'block';
            evalResults.classList.add('hidden');

            try {
                const response = await fetch('/evaluate');
                const data = await response.json();

                if (data.error) {
                    alert(data.error);
                    evalBtn.style.display = 'inline-block';
                    return;
                }

                document.getElementById('eval-acc').textContent = `${data.accuracy.toFixed(2)}%`;
                document.getElementById('eval-f1').textContent = data.macro_f1.toFixed(3);
                document.getElementById('eval-prec').textContent = data.macro_precision.toFixed(3);
                document.getElementById('eval-rec').textContent = data.macro_recall.toFixed(3);

                renderChart(data.classes, data.class_metrics);
                evalResults.classList.remove('hidden');

            } catch (error) {
                console.error(error);
                alert("Failed to run evaluation.");
                evalBtn.style.display = 'inline-block';
            } finally {
                evalLoading.style.display = 'none';
            }
        });

        function renderChart(classes, metrics) {
            const ctx = document.getElementById('confusionMatrixChart').getContext('2d');
            if (chartInstance) chartInstance.destroy();
            const f1Scores = classes.map(c => metrics[c]['f1-score']);
            chartInstance = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: classes,
                    datasets: [{ label: 'F1-Score', data: f1Scores, backgroundColor: '#1d1d1f', borderRadius: 6 }]
                },
                options: {
                    responsive: true,
                    plugins: { legend: { display: false }, title: { display: true, text: 'Class F1-Scores' } },
                    scales: { y: { beginAtZero: true, max: 1.0 } }
                }
            });
        }
    }
});
