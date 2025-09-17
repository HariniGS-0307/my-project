// Charts JavaScript for AI Elderly Medicare System

// DOM Ready Function
document.addEventListener('DOMContentLoaded', function() {
  // Initialize chart components
  initializeHealthCharts();
  initializeAnalyticsCharts();
  initializeReportCharts();
  
  console.log('Charts JavaScript loaded');
});

// Initialize Health Charts
function initializeHealthCharts() {
  // Initialize patient vitals chart
  initializePatientVitalsChart();
  
  // Initialize medication adherence chart
  initializeMedicationAdherenceChart();
  
  // Initialize health trends chart
  initializeHealthTrendsChart();
}

// Initialize Patient Vitals Chart
function initializePatientVitalsChart() {
  const ctx = document.getElementById('patientVitalsChart');
  if (!ctx) return;
  
  const patientVitalsChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      datasets: [
        {
          label: 'Blood Pressure (Systolic)',
          data: [135, 142, 138, 132, 128, 125],
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.1)',
          tension: 0.3,
          fill: true
        },
        {
          label: 'Cholesterol',
          data: [220, 215, 210, 205, 200, 195],
          borderColor: 'rgb(54, 162, 235)',
          backgroundColor: 'rgba(54, 162, 235, 0.1)',
          tension: 0.3,
          fill: true
        },
        {
          label: 'Glucose',
          data: [145, 150, 148, 142, 138, 135],
          borderColor: 'rgb(255, 205, 86)',
          backgroundColor: 'rgba(255, 205, 86, 0.1)',
          tension: 0.3,
          fill: true
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: false
        }
      }
    }
  });
}

// Initialize Medication Adherence Chart
function initializeMedicationAdherenceChart() {
  const ctx = document.getElementById('medicationAdherenceChart');
  if (!ctx) return;
  
  const medicationAdherenceChart = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Adherent', 'Non-Adherent', 'Pending'],
      datasets: [{
        data: [78, 12, 10],
        backgroundColor: [
          'rgb(25, 135, 84)',
          'rgb(220, 53, 69)',
          'rgb(255, 193, 7)'
        ]
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    }
  });
}

// Initialize Health Trends Chart
function initializeHealthTrendsChart() {
  const ctx = document.getElementById('healthTrendsChart');
  if (!ctx) return;
  
  const healthTrendsChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Diabetes', 'Hypertension', 'Arthritis', 'Osteoporosis', 'Other'],
      datasets: [{
        label: 'Patient Count',
        data: [120, 95, 80, 65, 40],
        backgroundColor: [
          'rgba(255, 99, 132, 0.7)',
          'rgba(54, 162, 235, 0.7)',
          'rgba(255, 205, 86, 0.7)',
          'rgba(75, 192, 192, 0.7)',
          'rgba(153, 102, 255, 0.7)'
        ],
        borderColor: [
          'rgb(255, 99, 132)',
          'rgb(54, 162, 235)',
          'rgb(255, 205, 86)',
          'rgb(75, 192, 192)',
          'rgb(153, 102, 255)'
        ],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
}

// Initialize Analytics Charts
function initializeAnalyticsCharts() {
  // Initialize patient engagement chart
  initializePatientEngagementChart();
  
  // Initialize service distribution chart
  initializeServiceDistributionChart();
  
  // Initialize caregiver performance chart
  initializeCaregiverPerformanceChart();
}

// Initialize Patient Engagement Chart
function initializePatientEngagementChart() {
  const ctx = document.getElementById('patientEngagementChart');
  if (!ctx) return;
  
  const patientEngagementChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4'],
      datasets: [
        {
          label: 'App Usage',
          data: [65, 78, 82, 90],
          borderColor: 'rgb(54, 162, 235)',
          backgroundColor: 'rgba(54, 162, 235, 0.1)',
          tension: 0.3,
          fill: true
        },
        {
          label: 'Medication Adherence',
          data: [72, 79, 85, 92],
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.1)',
          tension: 0.3,
          fill: true
        },
        {
          label: 'Appointment Attendance',
          data: [80, 85, 88, 94],
          borderColor: 'rgb(153, 102, 255)',
          backgroundColor: 'rgba(153, 102, 255, 0.1)',
          tension: 0.3,
          fill: true
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 100
        }
      }
    }
  });
}

// Initialize Service Distribution Chart
function initializeServiceDistributionChart() {
  const ctx = document.getElementById('serviceDistributionChart');
  if (!ctx) return;
  
  const serviceDistributionChart = new Chart(ctx, {
    type: 'pie',
    data: {
      labels: ['Medication Delivery', 'Health Monitoring', 'Care Visits', 'Teleconsultations', 'Emergency Response'],
      datasets: [{
        data: [40, 25, 15, 12, 8],
        backgroundColor: [
          'rgb(255, 99, 132)',
          'rgb(54, 162, 235)',
          'rgb(255, 205, 86)',
          'rgb(75, 192, 192)',
          'rgb(153, 102, 255)'
        ]
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'bottom'
        }
      }
    }
  });
}

// Initialize Caregiver Performance Chart
function initializeCaregiverPerformanceChart() {
  const ctx = document.getElementById('caregiverPerformanceChart');
  if (!ctx) return;
  
  const caregiverPerformanceChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['John Doe', 'Sarah Smith', 'Michael Brown', 'Emily Davis', 'Robert Wilson'],
      datasets: [{
        label: 'Patient Satisfaction',
        data: [4.9, 4.7, 4.6, 4.8, 4.5],
        backgroundColor: 'rgba(13, 202, 240, 0.7)',
        borderColor: 'rgb(13, 202, 240)',
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true,
          max: 5
        }
      }
    }
  });
}

// Initialize Report Charts
function initializeReportCharts() {
  // Initialize compliance chart
  initializeComplianceChart();
  
  // Initialize billing chart
  initializeBillingChart();
  
  // Initialize operational performance chart
  initializeOperationalPerformanceChart();
}

// Initialize Compliance Chart
function initializeComplianceChart() {
  const ctx = document.getElementById('complianceChart');
  if (!ctx) return;
  
  const complianceChart = new Chart(ctx, {
    type: 'radar',
    data: {
      labels: ['HIPAA', 'FDA', 'CMS', 'OSHA', 'Privacy', 'Security'],
      datasets: [{
        label: 'Compliance Score',
        data: [98, 95, 97, 92, 96, 94],
        fill: true,
        backgroundColor: 'rgba(25, 135, 84, 0.2)',
        borderColor: 'rgb(25, 135, 84)',
        pointBackgroundColor: 'rgb(25, 135, 84)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgb(25, 135, 84)'
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        r: {
          angleLines: {
            display: true
          },
          suggestedMin: 80,
          suggestedMax: 100
        }
      }
    }
  });
}

// Initialize Billing Chart
function initializeBillingChart() {
  const ctx = document.getElementById('billingChart');
  if (!ctx) return;
  
  const billingChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      datasets: [
        {
          label: 'Revenue',
          data: [120000, 135000, 128000, 142000, 156000, 162000],
          borderColor: 'rgb(13, 110, 253)',
          backgroundColor: 'rgba(13, 110, 253, 0.1)',
          tension: 0.3,
          fill: true
        },
        {
          label: 'Claims Processed',
          data: [850, 920, 890, 980, 1050, 1120],
          borderColor: 'rgb(255, 193, 7)',
          backgroundColor: 'rgba(255, 193, 7, 0.1)',
          tension: 0.3,
          fill: true
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: {
        y: {
          beginAtZero: true
        }
      }
    }
  });
}

// Initialize Operational Performance Chart
function initializeOperationalPerformanceChart() {
  const ctx = document.getElementById('operationalPerformanceChart');
  if (!ctx) return;
  
  const operationalPerformanceChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['On-time Deliveries', 'Care Quality', 'Response Time', 'Readmission Rate'],
      datasets: [{
        label: 'Performance',
        data: [98.2, 94.5, 18, 3.2],
        backgroundColor: [
          'rgba(40, 167, 69, 0.7)',
          'rgba(23, 162, 184, 0.7)',
          'rgba(108, 117, 125, 0.7)',
          'rgba(220, 53, 69, 0.7)'
        ],
        borderColor: [
          'rgb(40, 167, 69)',
          'rgb(23, 162, 184)',
          'rgb(108, 117, 125)',
          'rgb(220, 53, 69)'
        ],
        borderWidth: 1
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      indexAxis: 'y',
      scales: {
        x: {
          beginAtZero: true
        }
      }
    }
  });
}

// Update Chart Data
function updateChartData(chartId, newData) {
  const chart = Chart.getChart(chartId);
  if (chart) {
    chart.data.datasets[0].data = newData;
    chart.update();
  }
}

// Export functions for global use
window.updateChartData = updateChartData;