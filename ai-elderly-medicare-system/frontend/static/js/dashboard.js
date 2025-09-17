// Dashboard JavaScript for AI Elderly Medicare System

// DOM Ready Function
document.addEventListener('DOMContentLoaded', function() {
  // Initialize dashboard components
  initializeDashboardCharts();
  initializeQuickActions();
  initializeRecentActivity();
  initializeUpcomingAppointments();
  
  console.log('Dashboard JavaScript loaded');
});

// Initialize Dashboard Charts
function initializeDashboardCharts() {
  // Initialize patient trends chart
  initializePatientTrendsChart();
  
  // Initialize medication adherence chart
  initializeMedicationAdherenceChart();
  
  // Initialize appointment trends chart
  initializeAppointmentTrendsChart();
}

// Initialize Patient Trends Chart
function initializePatientTrendsChart() {
  const ctx = document.getElementById('patientTrendsChart');
  if (!ctx) return;
  
  const patientTrendsChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
      datasets: [{
        label: 'Active Patients',
        data: [120, 145, 138, 162, 178, 195],
        borderColor: 'rgb(13, 110, 253)',
        backgroundColor: 'rgba(13, 110, 253, 0.1)',
        tension: 0.3,
        fill: true
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

// Initialize Appointment Trends Chart
function initializeAppointmentTrendsChart() {
  const ctx = document.getElementById('appointmentTrendsChart');
  if (!ctx) return;
  
  const appointmentTrendsChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
      datasets: [{
        label: 'Appointments',
        data: [24, 32, 28, 35, 30, 18],
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
          beginAtZero: true
        }
      }
    }
  });
}

// Initialize Quick Actions
function initializeQuickActions() {
  const quickActionCards = document.querySelectorAll('.quick-action-card');
  
  quickActionCards.forEach(card => {
    card.addEventListener('click', function() {
      const action = this.getAttribute('data-action');
      handleQuickAction(action);
    });
  });
}

// Handle Quick Action
function handleQuickAction(action) {
  switch(action) {
    case 'add-patient':
      window.location.href = '/patients/new';
      break;
    case 'schedule-appointment':
      window.location.href = '/appointments/new';
      break;
    case 'view-reports':
      window.location.href = '/reports';
      break;
    case 'manage-medications':
      window.location.href = '/medications';
      break;
    case 'send-notification':
      showNotificationModal();
      break;
    case 'view-calendar':
      window.location.href = '/appointments/calendar';
      break;
    default:
      console.log('Unknown action:', action);
  }
}

// Show Notification Modal
function showNotificationModal() {
  // This would typically open a modal for sending notifications
  alert('Notification modal would open here');
}

// Initialize Recent Activity
function initializeRecentActivity() {
  // This would typically fetch recent activity from the server
  console.log('Recent activity initialized');
}

// Initialize Upcoming Appointments
function initializeUpcomingAppointments() {
  // This would typically fetch upcoming appointments from the server
  console.log('Upcoming appointments initialized');
}

// Refresh Dashboard Data
function refreshDashboardData() {
  // Show loading indicator
  const refreshBtn = document.querySelector('.refresh-dashboard');
  if (refreshBtn) {
    refreshBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>';
    refreshBtn.disabled = true;
  }
  
  // Simulate API call
  setTimeout(() => {
    // Hide loading indicator
    if (refreshBtn) {
      refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i> Refresh';
      refreshBtn.disabled = false;
    }
    
    // Show success notification
    showNotification('Dashboard data refreshed successfully', 'success');
  }, 1500);
}

// Export functions for global use
window.refreshDashboardData = refreshDashboardData;