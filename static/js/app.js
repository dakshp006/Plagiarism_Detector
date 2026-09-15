/* ============================================================================
   VERITEXT AI - FRONTEND APPLICATION JAVASCRIPT
   Handles API communication, live text plagiarism analysis, synchronized highlighting,
   algorithm visualizer, repository scanning, history logs, and analytics.
   ============================================================================ */

document.addEventListener('DOMContentLoaded', () => {
    // API Host Configuration
    const API_BASE = '';

    // State Variables
    let currentAnalysis = null;
    let isHighlightingMode = false;
    let storedUsersList = [];
    let storedDocsList = [];

    // DOM Elements
    const navItems = document.querySelectorAll('.nav-item');
    const tabContents = document.querySelectorAll('.tab-content');
    const pageTitle = document.getElementById('pageTitle');
    const pageSubtitle = document.getElementById('pageSubtitle');
    const dbEngineText = document.getElementById('dbEngineText');
    const statusIndicator = document.getElementById('statusIndicator');

    // Studio Inputs
    const textInput1 = document.getElementById('textInput1');
    const textInput2 = document.getElementById('textInput2');
    const highlightViewer1 = document.getElementById('highlightViewer1');
    const highlightViewer2 = document.getElementById('highlightViewer2');
    const wordCount1 = document.getElementById('wordCount1');
    const wordCount2 = document.getElementById('wordCount2');
    const fileInput1 = document.getElementById('fileInput1');
    const fileInput2 = document.getElementById('fileInput2');
    const windowSizeSelect = document.getElementById('windowSizeSelect');

    // Action Buttons
    const btnRunAnalysis = document.getElementById('btnRunAnalysis');
    const btnQuickDemo = document.getElementById('btnQuickDemo');
    const toggleHighlighterBtn = document.getElementById('toggleHighlighterBtn');

    // Dashboard Results
    const resultsDashboard = document.getElementById('resultsDashboard');
    const scoreVal = document.getElementById('scoreVal');
    const gaugeCircle = document.getElementById('gaugeCircle');
    const riskBadge = document.getElementById('riskBadge');
    const statMatches = document.getElementById('statMatches');
    const statLongest = document.getElementById('statLongest');
    const matchesList = document.getElementById('matchesList');

    // Visualizer Elements
    const valWindow = document.getElementById('valWindow');
    const hashSamplesGrid = document.getElementById('hashSamplesGrid');
    const lpsContainer = document.getElementById('lpsContainer');

    // Report Modal
    const reportModal = document.getElementById('reportModal');
    const reportModalBody = document.getElementById('reportModalBody');
    const btnCloseModal = document.getElementById('btnCloseModal');
    const btnDownloadReportFile = document.getElementById('btnDownloadReportFile');

    // Tab Navigation Configuration
    const tabHeaders = {
        'live-studio': { title: 'Live Comparison Studio', subtitle: 'Compare texts in real time using Rabin-Karp Rolling Hash & KMP Pattern Verification' },
        'algorithm-visualizer': { title: 'Algorithm Mechanics & Visualizer', subtitle: 'Inspect Rabin-Karp polynomial hash calculation & KMP Longest Prefix Suffix (LPS) array' },
        'repo-analyzer': { title: 'Repository Document Compare', subtitle: 'Run pairwise comparison or 1-to-Many scan against stored database documents' },
        'doc-manager': { title: 'Document Repository & User Management', subtitle: 'Register students/users and upload text files to database' },
        'history-reports': { title: 'Comparison History & Plagiarism Reports', subtitle: 'View historic document comparison logs and download text reports' },
        'analytics': { title: 'Advanced SQL Analytics & Metrics', subtitle: 'View database aggregate stats, high-risk user grouping, and subquery filters' }
    };

    // Initialize App
    init();

    function init() {
        setupNavigation();
        checkSystemStatus();
        setupInputListeners();
        loadUsersAndDocs();

        // Auto-run status poll
        setInterval(checkSystemStatus, 30000);
    }

    // Navigation Handler
    function setupNavigation() {
        navItems.forEach(item => {
            item.addEventListener('click', () => {
                const targetTab = item.getAttribute('data-tab');
                
                navItems.forEach(i => i.classList.remove('active'));
                tabContents.forEach(c => c.classList.remove('active'));

                item.classList.add('active');
                const targetContent = document.getElementById(targetTab);
                if (targetContent) targetContent.classList.add('active');

                if (tabHeaders[targetTab]) {
                    pageTitle.textContent = tabHeaders[targetTab].title;
                    pageSubtitle.textContent = tabHeaders[targetTab].subtitle;
                }

                // Tab-specific trigger actions
                if (targetTab === 'repo-analyzer') loadRepoSelectors();
                if (targetTab === 'history-reports') loadComparisonHistory();
                if (targetTab === 'analytics') loadAnalytics();
            });
        });
    }

    // System Status Call
    async function checkSystemStatus() {
        try {
            const res = await fetch(`${API_BASE}/api/status`);
            const data = await res.json();
            if (data.database_connected) {
                dbEngineText.textContent = `${data.database_engine} Active`;
                statusIndicator.className = 'status-indicator online';
            } else {
                dbEngineText.textContent = 'DB Disconnected';
                statusIndicator.className = 'status-indicator';
            }
        } catch (e) {
            dbEngineText.textContent = 'Server Offline';
            statusIndicator.className = 'status-indicator';
        }
    }

    // Input Listeners
    function setupInputListeners() {
        textInput1.addEventListener('input', updateWordCounts);
        textInput2.addEventListener('input', updateWordCounts);

        fileInput1.addEventListener('change', (e) => handleFileUpload(e, textInput1));
        fileInput2.addEventListener('change', (e) => handleFileUpload(e, textInput2));

        btnQuickDemo.addEventListener('click', loadSampleDemoText);
        btnRunAnalysis.addEventListener('click', executeLiveAnalysis);
        toggleHighlighterBtn.addEventListener('click', toggleHighlightView);

        // Pairwise & One-to-Many forms
        document.getElementById('formPairwise').addEventListener('submit', handlePairwiseCompare);
        document.getElementById('formOneToMany').addEventListener('submit', handleOneToManyCompare);

        // User & Doc Upload forms
        document.getElementById('formRegisterUser').addEventListener('submit', handleRegisterUser);
        document.getElementById('formUploadDoc').addEventListener('submit', handleUploadDoc);

        // Modal Close
        btnCloseModal.addEventListener('click', () => reportModal.classList.add('hidden'));
    }

    function updateWordCounts() {
        const count1 = countWords(textInput1.value);
        const count2 = countWords(textInput2.value);
        wordCount1.textContent = `${count1} words`;
        wordCount2.textContent = `${count2} words`;
    }

    function countWords(str) {
        if (!str || !str.trim()) return 0;
        return str.trim().split(/\s+/).length;
    }

    function handleFileUpload(e, targetTextarea) {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (evt) => {
            targetTextarea.value = evt.target.result;
            updateWordCounts();
        };
        reader.readAsText(file);
    }

    // Demo Data
    function loadSampleDemoText() {
        textInput1.value = `Artificial intelligence and machine learning are revolutionizing modern computer science. Machine learning is a subset of artificial intelligence that focuses on building systems that learn from data. Machine learning algorithms construct a mathematical model based on sample training data to make predictions or decisions.`;
        
        textInput2.value = `Computer science has evolved rapidly in recent years. Machine learning is a subset of artificial intelligence that focuses on building systems that learn from data. It uses statistics to discover patterns in training data to make predictions without explicit programming instructions.`;

        updateWordCounts();
        executeLiveAnalysis();
    }

    // Core Live Analysis Execution
    async function executeLiveAnalysis() {
        const text1 = textInput1.value.trim();
        const text2 = textInput2.value.trim();

        if (!text1 || !text2) {
            alert('Please enter or upload content into both Document 1 and Document 2.');
            return;
        }

        btnRunAnalysis.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing...';
        btnRunAnalysis.disabled = true;

        try {
            const windowSize = parseInt(windowSizeSelect.value);
            const response = await fetch(`${API_BASE}/api/compare`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    text1: text1,
                    text2: text2,
                    doc1_name: 'Document 1',
                    doc2_name: 'Document 2',
                    window_size: windowSize
                })
            });

            const data = await response.json();
            if (!data.success) {
                alert(`Analysis Error: ${data.error}`);
                return;
            }

            currentAnalysis = data.result;
            renderResults(data.result);
            renderAlgorithmBreakdown(data.result);

        } catch (err) {
            alert(`Server Request Failed: ${err.message}`);
        } finally {
            btnRunAnalysis.innerHTML = '<i class="fa-solid fa-magnifying-glass"></i> Analyze Plagiarism';
            btnRunAnalysis.disabled = false;
        }
    }

    // Render Analysis Results
    function renderResults(res) {
        resultsDashboard.classList.remove('hidden');

        // Circular Gauge Calculation (perimeter ~ 314)
        const score = res.similarity_score;
        scoreVal.textContent = `${score.toFixed(1)}%`;

        const offset = 314 - (314 * (score / 100));
        gaugeCircle.style.strokeDashoffset = offset;

        // Risk Level Badge Styling
        riskBadge.textContent = res.status;
        riskBadge.className = 'risk-badge ';
        if (res.status === 'HIGH') {
            riskBadge.classList.add('risk-high');
            gaugeCircle.style.stroke = '#ef4444';
        } else if (res.status === 'MEDIUM') {
            riskBadge.classList.add('risk-medium');
            gaugeCircle.style.stroke = '#f59e0b';
        } else {
            riskBadge.classList.add('risk-low');
            gaugeCircle.style.stroke = '#10b981';
        }

        // Stat Pills
        statMatches.textContent = res.total_matches;
        statLongest.textContent = `${res.longest_match} words`;

        // Render Match List
        matchesList.innerHTML = '';
        if (!res.matches || res.matches.length === 0) {
            matchesList.innerHTML = '<div class="text-muted p-3">No duplicate sequences detected between these documents.</div>';
        } else {
            res.matches.forEach((m, idx) => {
                const item = document.createElement('div');
                item.className = 'match-item';
                item.innerHTML = `
                    <div class="match-phrase">
                        <i class="fa-solid fa-quote-left text-indigo me-2"></i>
                        "${escapeHtml(m.phrase)}"
                    </div>
                    <div class="match-meta">
                        <span class="badge badge-subtle">${m.match_length} words</span>
                        <span class="kmp-tag"><i class="fa-solid fa-check-double"></i> KMP Verified</span>
                    </div>
                `;
                matchesList.appendChild(item);
            });
        }

        // Render Highlighting
        updateHighlightViewers(res);
    }

    // Synchronized Highlight Viewer Rendering
    function updateHighlightViewers(res) {
        if (!res || !res.matches) return;

        let content1 = res.doc1_content;
        let content2 = res.doc2_content;

        // Create highlighted HTML for text 1 & text 2
        let hlHtml1 = escapeHtml(content1);
        let hlHtml2 = escapeHtml(content2);

        res.matches.forEach((m, idx) => {
            const phraseEsc = escapeHtml(m.phrase);
            const regex = new RegExp(escapeRegExp(phraseEsc), 'gi');
            
            hlHtml1 = hlHtml1.replace(regex, () => `<mark class="hl-match" data-idx="${idx}">${phraseEsc}</mark>`);
            hlHtml2 = hlHtml2.replace(regex, () => `<mark class="hl-match" data-idx="${idx}">${phraseEsc}</mark>`);
        });

        highlightViewer1.innerHTML = hlHtml1;
        highlightViewer2.innerHTML = hlHtml2;

        // Add interactive linked highlight hover listener
        document.querySelectorAll('.hl-match').forEach(el => {
            el.addEventListener('mouseenter', (e) => {
                const idx = e.target.getAttribute('data-idx');
                document.querySelectorAll(`.hl-match[data-idx="${idx}"]`).forEach(m => {
                    m.style.background = '#f59e0b';
                    m.style.boxShadow = '0 0 12px #f59e0b';
                });
            });
            el.addEventListener('mouseleave', (e) => {
                const idx = e.target.getAttribute('data-idx');
                document.querySelectorAll(`.hl-match[data-idx="${idx}"]`).forEach(m => {
                    m.style.background = '';
                    m.style.boxShadow = '';
                });
            });
        });
    }

    function toggleHighlightView() {
        isHighlightingMode = !isHighlightingMode;
        if (isHighlightingMode) {
            textInput1.classList.add('hidden');
            textInput2.classList.add('hidden');
            highlightViewer1.classList.remove('hidden');
            highlightViewer2.classList.remove('hidden');
            toggleHighlighterBtn.innerHTML = '<i class="fa-solid fa-pen-to-square"></i> Switch to Edit Mode';
        } else {
            textInput1.classList.remove('hidden');
            textInput2.classList.remove('hidden');
            highlightViewer1.classList.add('hidden');
            highlightViewer2.classList.add('hidden');
            toggleHighlighterBtn.innerHTML = '<i class="fa-solid fa-highlighter"></i> Toggle Highlighting View';
        }
    }

    // Render Algorithm Breakdown (Tab 2)
    function renderAlgorithmBreakdown(res) {
        if (!res || !res.algorithm_breakdown) return;
        const ab = res.algorithm_breakdown;

        valWindow.textContent = ab.window_size;
        document.getElementById('valBase').textContent = ab.hash_base;
        document.getElementById('valMod').textContent = ab.hash_mod.toLocaleString();

        // Hash samples
        hashSamplesGrid.innerHTML = '';
        if (ab.rk_samples && ab.rk_samples.length > 0) {
            ab.rk_samples.forEach(s => {
                const card = document.createElement('div');
                card.className = 'hash-sample-card';
                card.innerHTML = `
                    <div class="small text-muted mb-1">Window Index #${s.index}</div>
                    <div class="mb-2">"${escapeHtml(s.window)}"</div>
                    <div>Hash Value: <strong>${s.hash_val}</strong></div>
                `;
                hashSamplesGrid.appendChild(card);
            });
        }

        // KMP LPS Table
        lpsContainer.innerHTML = '';
        if (ab.kmp_lps_sample && ab.kmp_lps_sample.length > 0) {
            let tableHtml = `
                <table class="lps-table">
                    <thead>
                        <tr>
                            <th>Token / Word</th>
                            ${ab.kmp_lps_sample.map(x => `<th>${escapeHtml(x.token)}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>LPS Value</td>
                            ${ab.kmp_lps_sample.map(x => `<td>${x.lps}</td>`).join('')}
                        </tr>
                    </tbody>
                </table>
            `;
            lpsContainer.innerHTML = tableHtml;
        } else {
            lpsContainer.innerHTML = '<div class="empty-state">No matching phrase found for KMP LPS pattern array display.</div>';
        }
    }

    // Load Users & Docs
    async function loadUsersAndDocs() {
        try {
            const [usersRes, docsRes] = await Promise.all([
                fetch(`${API_BASE}/api/users`),
                fetch(`${API_BASE}/api/documents`)
            ]);

            const usersData = await usersRes.json();
            const docsData = await docsRes.json();

            if (usersData.success) {
                storedUsersList = usersData.users;
                renderUsersTable(storedUsersList);
            }
            if (docsData.success) {
                storedDocsList = docsData.documents;
                renderDocsTable(storedDocsList);
            }
        } catch (e) {
            console.error('Failed to load users/docs:', e);
        }
    }

    function renderUsersTable(users) {
        const tbody = document.querySelector('#usersTable tbody');
        const uploadSelect = document.getElementById('selectUploadUser');
        
        tbody.innerHTML = '';
        uploadSelect.innerHTML = '<option value="">-- Select Owner --</option>';

        users.forEach(u => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>#${u.user_id}</td><td><strong>${escapeHtml(u.name)}</strong></td><td>${escapeHtml(u.email)}</td>`;
            tbody.appendChild(tr);

            const opt = document.createElement('option');
            opt.value = u.user_id;
            opt.textContent = `${u.name} (ID: ${u.user_id})`;
            uploadSelect.appendChild(opt);
        });
    }

    function renderDocsTable(docs) {
        const tbody = document.querySelector('#docsTable tbody');
        tbody.innerHTML = '';

        docs.forEach(d => {
            const tr = document.createElement('tr');
            tr.innerHTML = `<td>#${d.document_id}</td><td><strong>${escapeHtml(d.file_name)}</strong></td><td>${escapeHtml(d.owner_name || 'N/A')}</td><td>${d.word_count} words</td>`;
            tbody.appendChild(tr);
        });
    }

    function loadRepoSelectors() {
        const select1 = document.getElementById('selectDoc1');
        const select2 = document.getElementById('selectDoc2');
        const selectTarget = document.getElementById('selectTargetDoc');

        const fillOpts = (selectEl) => {
            selectEl.innerHTML = '<option value="">-- Select Document --</option>';
            storedDocsList.forEach(d => {
                const opt = document.createElement('option');
                opt.value = d.document_id;
                opt.textContent = `#${d.document_id} - ${d.file_name} (${d.owner_name})`;
                selectEl.appendChild(opt);
            });
        };

        fillOpts(select1);
        fillOpts(select2);
        fillOpts(selectTarget);
    }

    // Handlers for Repo Compare
    async function handlePairwiseCompare(e) {
        e.preventDefault();
        const doc1_id = document.getElementById('selectDoc1').value;
        const doc2_id = document.getElementById('selectDoc2').value;

        if (!doc1_id || !doc2_id) {
            alert('Please select both Document 1 and Document 2.');
            return;
        }

        try {
            const res = await fetch(`${API_BASE}/api/compare`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ doc1_id, doc2_id, window_size: 5 })
            });

            const data = await res.json();
            if (!data.success) {
                alert(`Comparison Error: ${data.error}`);
                return;
            }

            renderRepoResultsCard([data.result], `Pairwise Comparison: Doc #${doc1_id} vs Doc #${doc2_id}`);
        } catch (err) {
            alert(`Failed: ${err.message}`);
        }
    }

    async function handleOneToManyCompare(e) {
        e.preventDefault();
        const target_doc_id = document.getElementById('selectTargetDoc').value;
        if (!target_doc_id) {
            alert('Please select a target document.');
            return;
        }

        try {
            const res = await fetch(`${API_BASE}/api/compare/one-to-many`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ target_doc_id, window_size: 5 })
            });

            const data = await res.json();
            if (!data.success) {
                alert(`1-to-Many Scan Error: ${data.error}`);
                return;
            }

            renderRepoResultsCard(data.results, `1-to-Many Scan Results for Document #${target_doc_id}`);
        } catch (err) {
            alert(`Failed: ${err.message}`);
        }
    }

    function renderRepoResultsCard(resultsList, title) {
        const repoResultsCard = document.getElementById('repoResultsCard');
        const repoResultsTitle = document.getElementById('repoResultsTitle');
        const repoResultsBody = document.getElementById('repoResultsBody');

        repoResultsTitle.textContent = title;
        repoResultsCard.classList.remove('hidden');

        let html = `
            <table class="table">
                <thead>
                    <tr>
                        <th>Doc 1</th>
                        <th>Doc 2</th>
                        <th>Similarity</th>
                        <th>Risk Status</th>
                        <th>Total Matches</th>
                        <th>Longest Match</th>
                    </tr>
                </thead>
                <tbody>
        `;

        resultsList.forEach(r => {
            const riskClass = r.status === 'HIGH' ? 'risk-high' : (r.status === 'MEDIUM' ? 'risk-medium' : 'risk-low');
            html += `
                <tr>
                    <td><strong>${escapeHtml(r.doc1_name || 'Doc ' + r.doc1_id)}</strong></td>
                    <td><strong>${escapeHtml(r.doc2_name || 'Doc ' + r.doc2_id)}</strong></td>
                    <td><strong class="text-indigo">${r.similarity_score}%</strong></td>
                    <td><span class="risk-badge ${riskClass}">${r.status}</span></td>
                    <td>${r.total_matches}</td>
                    <td>${r.longest_match} words</td>
                </tr>
            `;
        });

        html += '</tbody></table>';
        repoResultsBody.innerHTML = html;
    }

    // Registration and Upload Handlers
    async function handleRegisterUser(e) {
        e.preventDefault();
        const name = document.getElementById('inputUserName').value;
        const email = document.getElementById('inputUserEmail').value;

        try {
            const res = await fetch(`${API_BASE}/api/users`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, email })
            });
            const data = await res.json();
            if (data.success) {
                alert(`User registered successfully! Assigned User ID: #${data.user.user_id}`);
                document.getElementById('inputUserName').value = '';
                document.getElementById('inputUserEmail').value = '';
                loadUsersAndDocs();
            } else {
                alert(`Registration failed: ${data.error}`);
            }
        } catch (err) {
            alert(`Failed: ${err.message}`);
        }
    }

    async function handleUploadDoc(e) {
        e.preventDefault();
        const user_id = document.getElementById('selectUploadUser').value;
        const file_name = document.getElementById('inputDocName').value;
        const content = document.getElementById('inputDocContent').value;

        try {
            const res = await fetch(`${API_BASE}/api/documents/upload`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ user_id, file_name, content })
            });
            const data = await res.json();
            if (data.success) {
                alert(`Document uploaded successfully! Assigned Doc ID: #${data.document.document_id}`);
                document.getElementById('inputDocName').value = '';
                document.getElementById('inputDocContent').value = '';
                loadUsersAndDocs();
            } else {
                alert(`Upload failed: ${data.error}`);
            }
        } catch (err) {
            alert(`Failed: ${err.message}`);
        }
    }

    // Comparison History
    async function loadComparisonHistory() {
        try {
            const res = await fetch(`${API_BASE}/api/history`);
            const data = await res.json();

            const tbody = document.querySelector('#historyTable tbody');
            tbody.innerHTML = '';

            if (data.success && data.history.length > 0) {
                data.history.forEach(c => {
                    const riskClass = c.status === 'HIGH' ? 'risk-high' : (c.status === 'MEDIUM' ? 'risk-medium' : 'risk-low');
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td>#${c.comparison_id}</td>
                        <td><strong>${escapeHtml(c.doc1_name)}</strong> <span class="small text-muted">(${escapeHtml(c.u1_name)})</span></td>
                        <td><strong>${escapeHtml(c.doc2_name)}</strong> <span class="small text-muted">(${escapeHtml(c.u2_name)})</span></td>
                        <td><strong class="text-indigo">${c.similarity_score}%</strong></td>
                        <td><span class="risk-badge ${riskClass}">${c.status}</span></td>
                        <td>${c.compared_at}</td>
                        <td>
                            <button class="btn btn-xs btn-outline btn-view-report" data-id="${c.comparison_id}">
                                <i class="fa-solid fa-file-text"></i> View Report
                            </button>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });

                document.querySelectorAll('.btn-view-report').forEach(b => {
                    b.addEventListener('click', (evt) => {
                        const compId = evt.currentTarget.getAttribute('data-id');
                        openReportModal(compId);
                    });
                });
            } else {
                tbody.innerHTML = '<tr><td colspan="7" class="text-muted text-center p-3">No comparison history available yet.</td></tr>';
            }
        } catch (e) {
            console.error('History load error:', e);
        }
    }

    async function openReportModal(compId) {
        try {
            const res = await fetch(`${API_BASE}/api/reports/${compId}`);
            const data = await res.json();
            if (!data.success) {
                alert(`Report error: ${data.error}`);
                return;
            }

            const r = data.report;
            let text = `======================================================================\n`;
            text += `                       PLAGIARISM DETECTION REPORT                   \n`;
            text += `======================================================================\n`;
            text += `Report ID / Comparison ID : #${r.comparison_id}\n`;
            text += `Generated Date           : ${r.compared_at}\n`;
            text += `Document 1 (Target)      : ${r.doc1_name} (Owner: ${r.owner1_name})\n`;
            text += `Document 2 (Compared With): ${r.doc2_name} (Owner: ${r.owner2_name})\n`;
            text += `----------------------------------------------------------------------\n`;
            text += `SIMILARITY SCORE         : ${r.similarity_score}%\n`;
            text += `RISK ASSESSMENT LEVEL    : ${r.status}\n`;
            text += `Total Matched Sections   : ${r.total_matches}\n`;
            text += `Longest Sequence Match   : ${r.longest_match} words\n`;
            text += `======================================================================\n\n`;
            text += `## DETAILED MATCHING SECTIONS / PHRASES:\n\n`;

            if (r.matching_sections && r.matching_sections.length > 0) {
                r.matching_sections.forEach((m, idx) => {
                    text += `  Match #${idx + 1}:\n`;
                    text += `    Phrase        : "${m.phrase}"\n`;
                    text += `    Doc 1 Position: Word index ${m.position_doc1}\n`;
                    text += `    Doc 2 Position: Word index ${m.position_doc2}\n`;
                    text += `    Word Length   : ${m.match_length} words\n\n`;
                });
            } else {
                text += `  [No matching sequence phrases detected]\n`;
            }

            reportModalBody.textContent = text;
            btnDownloadReportFile.href = `${API_BASE}/api/reports/download/${compId}`;
            reportModal.classList.remove('hidden');

        } catch (err) {
            alert(`Failed to load report: ${err.message}`);
        }
    }

    // Analytics Dashboard
    async function loadAnalytics() {
        try {
            const res = await fetch(`${API_BASE}/api/analytics`);
            const data = await res.json();
            if (!data.success) return;

            const st = data.stats;
            document.getElementById('anTotalUsers').textContent = st.total_users;
            document.getElementById('anTotalDocs').textContent = st.total_documents;
            document.getElementById('anTotalComps').textContent = st.total_comparisons;
            document.getElementById('anAvgSim').textContent = `${st.avg_similarity}%`;

            // High Risk Users Table
            const tbodyHigh = document.querySelector('#highRiskUsersTable tbody');
            tbodyHigh.innerHTML = '';
            if (data.high_risk_users && data.high_risk_users.length > 0) {
                data.high_risk_users.forEach(u => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `<td>#${u.user_id}</td><td><strong>${escapeHtml(u.name)}</strong></td><td>${escapeHtml(u.email)}</td><td><span class="risk-badge risk-high">${u.high_risk_count} High Risk</span></td>`;
                    tbodyHigh.appendChild(tr);
                });
            } else {
                tbodyHigh.innerHTML = '<tr><td colspan="4" class="text-muted p-3">No high risk users detected yet.</td></tr>';
            }

            // Above Average Comparisons Table
            const tbodyAvg = document.querySelector('#aboveAvgTable tbody');
            tbodyAvg.innerHTML = '';
            if (data.above_average_comparisons && data.above_average_comparisons.length > 0) {
                data.above_average_comparisons.forEach(c => {
                    const riskClass = c.status === 'HIGH' ? 'risk-high' : (c.status === 'MEDIUM' ? 'risk-medium' : 'risk-low');
                    const tr = document.createElement('tr');
                    tr.innerHTML = `<td>#${c.comparison_id}</td><td>${escapeHtml(c.doc1_name)}</td><td>${escapeHtml(c.doc2_name)}</td><td><strong class="text-indigo">${c.similarity_score}%</strong></td><td><span class="risk-badge ${riskClass}">${c.status}</span></td>`;
                    tbodyAvg.appendChild(tr);
                });
            } else {
                tbodyAvg.innerHTML = '<tr><td colspan="5" class="text-muted p-3">No above-average comparisons available.</td></tr>';
            }

        } catch (e) {
            console.error('Analytics load error:', e);
        }
    }

    // Helper functions
    function escapeHtml(str) {
        if (!str) return '';
        return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
    }

    function escapeRegExp(str) {
        return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }
});
