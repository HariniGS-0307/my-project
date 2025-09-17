// Notifications JavaScript for AI Elderly Medicare System

// DOM Ready Function
document.addEventListener('DOMContentLoaded', function() {
  // Initialize notification components
  initializeNotifications();
  initializeNotificationSettings();
  initializeEmergencyAlerts();
  initializeReminderSettings();
  
  console.log('Notifications JavaScript loaded');
});

// Initialize Notifications
function initializeNotifications() {
  // Mark notifications as read when clicked
  const notificationItems = document.querySelectorAll('.notification-item');
  
  notificationItems.forEach(item => {
    item.addEventListener('click', function() {
      markNotificationAsRead(this);
    });
  });
  
  // Handle notification actions
  const actionButtons = document.querySelectorAll('.notification-action-btn');
  
  actionButtons.forEach(button => {
    button.addEventListener('click', function(event) {
      event.stopPropagation();
      handleNotificationAction(this);
    });
  });
}

// Mark Notification as Read
function markNotificationAsRead(notificationItem) {
  if (notificationItem.classList.contains('unread')) {
    notificationItem.classList.remove('unread');
    
    // Update notification count
    updateNotificationCount(-1);
    
    // Send AJAX request to mark as read on server
    const notificationId = notificationItem.getAttribute('data-notification-id');
    if (notificationId) {
      markNotificationAsReadOnServer(notificationId);
    }
  }
}

// Mark Notification as Read on Server
function markNotificationAsReadOnServer(notificationId) {
  // This would typically send an AJAX request to the server
  console.log('Marking notification as read on server:', notificationId);
  
  // Example fetch request:
  /*
  fetch(`/api/notifications/${notificationId}/read`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
    }
  })
  .then(response => response.json())
  .then(data => {
    console.log('Notification marked as read:', data);
  })
  .catch(error => {
    console.error('Error marking notification as read:', error);
  });
  */
}

// Handle Notification Action
function handleNotificationAction(button) {
  const action = button.getAttribute('data-action');
  const notificationId = button.closest('.notification-item').getAttribute('data-notification-id');
  
  switch (action) {
    case 'view':
      viewNotificationDetails(notificationId);
      break;
    case 'dismiss':
      dismissNotification(notificationId);
      break;
    case 'snooze':
      snoozeNotification(notificationId);
      break;
    default:
      console.log('Unknown notification action:', action);
  }
}

// View Notification Details
function viewNotificationDetails(notificationId) {
  // This would typically open a modal or navigate to notification details page
  console.log('Viewing notification details:', notificationId);
  window.location.href = `/notifications/${notificationId}`;
}

// Dismiss Notification
function dismissNotification(notificationId) {
  const notificationItem = document.querySelector(`[data-notification-id="${notificationId}"]`);
  if (notificationItem) {
    notificationItem.style.opacity = '0';
    setTimeout(() => {
      notificationItem.remove();
      updateNotificationCount(-1);
    }, 300);
  }
  
  // Send AJAX request to dismiss on server
  console.log('Dismissing notification on server:', notificationId);
}

// Snooze Notification
function snoozeNotification(notificationId) {
  // This would typically open a snooze modal or show snooze options
  console.log('Snoozing notification:', notificationId);
  showNotification('Notification snoozed for 1 hour', 'success');
}

// Update Notification Count
function updateNotificationCount(change) {
  const countElement = document.querySelector('.notification-count');
  if (countElement) {
    let count = parseInt(countElement.textContent) || 0;
    count += change;
    count = Math.max(0, count); // Ensure count doesn't go below 0
    countElement.textContent = count;
    
    // Hide count badge if zero
    if (count === 0) {
      countElement.style.display = 'none';
    } else {
      countElement.style.display = 'inline-block';
    }
  }
}

// Initialize Notification Settings
function initializeNotificationSettings() {
  // Handle toggle switches for notification settings
  const toggleSwitches = document.querySelectorAll('.setting-toggle input[type="checkbox"]');
  
  toggleSwitches.forEach(toggle => {
    toggle.addEventListener('change', function() {
      updateNotificationSetting(this);
    });
  });
}

// Update Notification Setting
function updateNotificationSetting(toggle) {
  const settingName = toggle.getAttribute('data-setting');
  const isEnabled = toggle.checked;
  
  // Send AJAX request to update setting on server
  console.log('Updating notification setting:', settingName, isEnabled);
  
  // Example fetch request:
  /*
  fetch('/api/notification-settings', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-TOKEN': document.querySelector('meta[name="csrf-token"]').getAttribute('content')
    },
    body: JSON.stringify({
      setting: settingName,
      enabled: isEnabled
    })
  })
  .then(response => response.json())
  .then(data => {
    showNotification('Notification settings updated', 'success');
  })
  .catch(error => {
    console.error('Error updating notification setting:', error);
    // Revert toggle state on error
    toggle.checked = !isEnabled;
    showNotification('Error updating settings', 'danger');
  });
  */
}

// Initialize Emergency Alerts
function initializeEmergencyAlerts() {
  // Handle emergency alert actions
  const alertActionButtons = document.querySelectorAll('.alert-action-btn');
  
  alertActionButtons.forEach(button => {
    button.addEventListener('click', function() {
      handleEmergencyAlertAction(this);
    });
  });
}

// Handle Emergency Alert Action
function handleEmergencyAlertAction(button) {
  const action = button.getAttribute('data-action');
  const alertId = button.closest('.alert-card').getAttribute('data-alert-id');
  
  switch (action) {
    case 'acknowledge':
      acknowledgeEmergencyAlert(alertId);
      break;
    case 'escalate':
      escalateEmergencyAlert(alertId);
      break;
    case 'resolve':
      resolveEmergencyAlert(alertId);
      break;
    default:
      console.log('Unknown emergency alert action:', action);
  }
}

// Acknowledge Emergency Alert
function acknowledgeEmergencyAlert(alertId) {
  console.log('Acknowledging emergency alert:', alertId);
  showNotification('Emergency alert acknowledged', 'success');
  
  // Update UI
  const alertCard = document.querySelector(`[data-alert-id="${alertId}"]`);
  if (alertCard) {
    const statusBadge = alertCard.querySelector('.alert-status');
    if (statusBadge) {
      statusBadge.textContent = 'Acknowledged';
      statusBadge.className = 'badge bg-warning alert-status';
    }
  }
}

// Escalate Emergency Alert
function escalateEmergencyAlert(alertId) {
  console.log('Escalating emergency alert:', alertId);
  showNotification('Emergency alert escalated to supervisor', 'warning');
}

// Resolve Emergency Alert
function resolveEmergencyAlert(alertId) {
  console.log('Resolving emergency alert:', alertId);
  showNotification('Emergency alert resolved', 'success');
  
  // Remove alert from UI
  const alertCard = document.querySelector(`[data-alert-id="${alertId}"]`);
  if (alertCard) {
    alertCard.style.opacity = '0';
    setTimeout(() => {
      alertCard.remove();
    }, 300);
  }
}

// Initialize Reminder Settings
function initializeReminderSettings() {
  // Handle reminder setting changes
  const reminderToggles = document.querySelectorAll('.reminder-toggle');
  
  reminderToggles.forEach(toggle => {
    toggle.addEventListener('change', function() {
      updateReminderSetting(this);
    });
  });
}

// Update Reminder Setting
function updateReminderSetting(toggle) {
  const reminderType = toggle.getAttribute('data-reminder-type');
  const isEnabled = toggle.checked;
  
  console.log('Updating reminder setting:', reminderType, isEnabled);
  showNotification(`Reminder setting for ${reminderType} updated`, 'success');
}

// Show Toast Notification
function showToastNotification(message, type = 'info') {
  const toastContainer = document.querySelector('.toast-container');
  if (!toastContainer) {
    console.warn('Toast container not found');
    return;
  }
  
  const toast = document.createElement('div');
  toast.className = `toast align-items-center text-white bg-${type} border-0`;
  toast.setAttribute('role', 'alert');
  toast.setAttribute('aria-live', 'assertive');
  toast.setAttribute('aria-atomic', 'true');
  
  toast.innerHTML = `
    <div class="d-flex">
      <div class="toast-body">
        ${message}
      </div>
      <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
    </div>
  `;
  
  toastContainer.appendChild(toast);
  
  // Initialize and show toast
  const bsToast = new bootstrap.Toast(toast);
  bsToast.show();
  
  // Remove toast after it's hidden
  toast.addEventListener('hidden.bs.toast', function() {
    toast.remove();
  });
}

// Export functions for global use
window.showToastNotification = showToastNotification;