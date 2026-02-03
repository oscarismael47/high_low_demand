// app.js - simple static app to load consumption_issues.json and display table + details
let ISSUES = [];
let FILTERED = [];

const statusSelect = document.getElementById('filter-status');
const severitySelect = document.getElementById('filter-severity');
const typeSelect = document.getElementById('filter-type');
const tableInfo = document.getElementById('table-info');
const tableBody = document.querySelector('#issues-table tbody');
const issueSelect = document.getElementById('issue-select');
const issueDetails = document.getElementById('issue-details');
const exportBtn = document.getElementById('export-json');

async function loadData(){
  try{
    // load from same folder (root)
    const res = await fetch('consumption_issues.json');
    if(!res.ok) throw new Error('Failed to fetch JSON: '+res.status);
    ISSUES = await res.json();
  }catch(err){
    console.error('Could not load consumption_issues.json. Run a static server and ensure the file is accessible.');
    tableInfo.textContent = 'Error: could not load consumption_issues.json. See console.';
    return;
  }
  FILTERED = ISSUES.slice();
  renderFilters();
  renderTable();
  populateIssueSelect();
}

function renderFilters(){
  [statusSelect,severitySelect,typeSelect].forEach(el=>el.addEventListener('change',applyFilters));
}

function applyFilters(){
  const status = statusSelect.value;
  const severity = severitySelect.value;
  const type = typeSelect.value;

  FILTERED = ISSUES.filter(i=>{
    if(status !== 'All' && i.status !== status) return false;
    if(severity !== 'All' && i.severity !== severity) return false;
    if(type !== 'All' && i.issue_type !== type) return false;
    return true;
  });
  renderTable();
  populateIssueSelect();
}

function formatDeviation(dev){
  return (dev === undefined || dev === null) ? 'N/A' : (Number(dev).toFixed(1)+'%');
}

function renderTable(){
  tableBody.innerHTML = '';
  tableInfo.textContent = `Found ${FILTERED.length} issue(s)`;
  FILTERED.forEach(issue=>{
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${issue.id}</td>
      <td>${issue.location}</td>
      <td>${issue.issue_type}</td>
      <td>${issue.severity}</td>
      <td>${issue.current_usage || ''}</td>
      <td>${issue.expected_usage || ''}</td>
      <td>${formatDeviation(issue.energy_deviation_percentage)}</td>
      <td>${issue.status}</td>
      <td>${issue.reported_date || ''}</td>
      <td>${issue.solution ? issue.solution.substring(0, 50) + (issue.solution.length > 50 ? '...' : '') : ''}</td>
    `;
    tableBody.appendChild(tr);
  });
}

function populateIssueSelect(){
  issueSelect.innerHTML = '';

  FILTERED.forEach(issue=>{
    const opt = document.createElement('option');
    opt.value = issue.id;
    opt.textContent = `Issue #${issue.id}`;
    issueSelect.appendChild(opt);
  });

  // Show first item by default
  if(FILTERED.length > 0){
    issueSelect.value = FILTERED[0].id;
    showDetails(FILTERED[0].id);
  }

  issueSelect.addEventListener('change',()=>{
    const val = issueSelect.value;
    if(!val){
      issueDetails.classList.add('hidden');
      issueDetails.innerHTML = '';
      return;
    }
    showDetails(Number(val));
  });
}

function showDetails(id){
  const issue = ISSUES.find(x=>x.id === id) || FILTERED.find(x=>x.id === id);
  if(!issue) return;
  issueDetails.classList.remove('hidden');
  
  // Generate monthly history table
  let historyHTML = '';
  if(issue.monthly_history && Object.keys(issue.monthly_history).length > 0){
    historyHTML = '<h4 style="margin-top:16px">Monthly History:</h4><table style="width:100%;border-collapse:collapse;margin-top:8px"><tr style="background-color:#f0f0f0"><th style="border:1px solid #ccc;padding:8px">Month</th><th style="border:1px solid #ccc;padding:8px">Usage</th><th style="border:1px solid #ccc;padding:8px">Status</th></tr>';
    for(const [month, data] of Object.entries(issue.monthly_history)){
      historyHTML += `<tr><td style="border:1px solid #ccc;padding:8px">${month}</td><td style="border:1px solid #ccc;padding:8px">${data.usage}</td><td style="border:1px solid #ccc;padding:8px">${data.status}</td></tr>`;
    }
    historyHTML += '</table>';
  }
  
  issueDetails.innerHTML = `
    <table class="details-table" id="issue-details-table">
      <tbody>
        <tr>
          <td id="issue-detail-title" class="details-block">
            <h3>Issue #${issue.id} — ${issue.location}</h3>
            <p class="muted">Type: ${issue.issue_type} • Severity: ${issue.severity} • Status: ${issue.status}</p>
            <p><strong>Reported:</strong> ${issue.reported_date || 'N/A'}</p>
            <p><strong>Current Usage:</strong> ${issue.current_usage || 'N/A'}</p>
            <p><strong>Expected Usage:</strong> ${issue.expected_usage || 'N/A'}</p>
            <p><strong>Deviation:</strong> ${formatDeviation(issue.energy_deviation_percentage)}</p>
            <p><strong>Description:</strong> ${issue.description || ''}</p>
            <p><strong>Pattern Analysis:</strong> ${issue.pattern_analysis || 'N/A'}</p>
            <p><strong>Last Maintenance:</strong> ${issue.last_maintenance || 'N/A'}</p>
            <p><strong>External Factors:</strong> ${issue.external_factors || 'N/A'}</p>
          </td>
        </tr>
        <tr>
          <td id="monthly-history" class="details-block">
            ${historyHTML}
          </td>
        </tr>
        <tr>
          <td id="chart-wrapper" class="details-block"></td>
        </tr>
        <tr>
          <td id="status-dropdown" class="details-block">
            <table class="edit-row">
              <tbody>
                <tr>
                  <td><label for="status-edit">Status:</label></td>
                  <td>
                    <select id="status-edit">
                      <option>Open</option>
                      <option>In Progress</option>
                      <option>Resolved</option>
                    </select>
                  </td>
                </tr>
              </tbody>
            </table>
          </td>
        </tr>
        <tr>
          <td id="solution-notes" class="details-block">
            <table class="edit-row">
              <tbody>
                <tr>
                  <td><label for="solution-edit">Solution / Notes:</label></td>
                </tr>
                <tr>
                  <td>
                    <textarea id="solution-edit" rows="4" style="width:100%">${issue.solution ? issue.solution : ''}</textarea>
                  </td>
                </tr>
              </tbody>
            </table>
          </td>
        </tr>
        <tr>
          <td id="save-button" class="details-block">
            <button id="save-issue" class="btn">Save (in-memory)</button>
          </td>
        </tr>
      </tbody>
    </table>
  `;

  // set current status
  const statusEdit = document.getElementById('status-edit');
  statusEdit.value = issue.status || 'Open';

  document.getElementById('save-issue').addEventListener('click', ()=>{
    issue.status = statusEdit.value;
    issue.solution = document.getElementById('solution-edit').value;
    applyFilters();
    populateIssueSelect();
    alert('Saved in memory. Use Export JSON to download changes.');
  });

  // Generate chart if monthly_history exists
  if(issue.monthly_history && Object.keys(issue.monthly_history).length > 0){
    setTimeout(() => renderChart(issue.monthly_history), 0);
  }
}

function renderChart(monthlyHistory){
  const chartWrapper = document.getElementById('chart-wrapper');
  
  // Extract data
  const months = Object.keys(monthlyHistory);
  const usages = months.map(month => {
    const usage = monthlyHistory[month].usage;
    return parseInt(usage) || 0;
  });
  
  // Create canvas element
  if(!document.getElementById('monthly-chart')){
    const canvas = document.createElement('canvas');
    canvas.id = 'monthly-chart';
    chartWrapper.innerHTML = '<h4 style="margin-top:16px">Usage Trend</h4>';
    chartWrapper.appendChild(canvas);
  }
  
  // Destroy existing chart if it exists
  if(window.currentChart){
    window.currentChart.destroy();
  }
  
  // Create new chart
  const canvas = document.getElementById('monthly-chart');
  const ctx = canvas.getContext('2d');
  window.currentChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: months,
      datasets: [{
        label: 'Energy Usage (kWh)',
        data: usages,
        borderColor: '#ff6b6b',
        backgroundColor: 'rgba(255, 107, 107, 0.1)',
        borderWidth: 2,
        fill: true,
        tension: 0.4
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: true,
      plugins: {
        legend: {
          display: true
        }
      },
      scales: {
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Usage (kWh)'
          }
        }
      }
    }
  });
}


function exportJSON(){
  const blob = new Blob([JSON.stringify(ISSUES, null, 2)], {type:'application/json'});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'consumption_issues_updated.json';
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

exportBtn.addEventListener('click', exportJSON);

window.addEventListener('load', loadData);
