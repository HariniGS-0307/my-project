// WebSocket JavaScript for AI Elderly Medicare System

// WebSocket connection variables
let websocket = null;
let reconnectInterval = 1000; // Initial reconnect interval (1 second)
let maxReconnectInterval = 30000; // Maximum reconnect interval (30 seconds)
let reconnectDecay = 1.5; // Reconnect interval decay factor
let reconnectAttempts = 0;
let isConnected = false;

// DOM Ready Function
document.addEventListener('DOMContentLoaded', function() {
  // Initialize WebSocket connection
  initializeWebSocket();
  
  // Set up event listeners for WebSocket controls
  setupWebSocketControls();
  
  console.log('WebSocket JavaScript loaded');
});

// Initialize WebSocket Connection
function initializeWebSocket() {
  // Check if WebSocket is supported
  if (!window.WebSocket) {
    console.error('WebSocket is not supported by this browser');
    showNotification('Real-time updates are not supported in your browser', 'warning');
    return;
  }
  
  // Construct WebSocket URL (assuming same host as current page)
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsUrl = `${protocol}//${window.location.host}/ws`;
  
  try {
    // Create WebSocket connection
    websocket = new WebSocket(wsUrl);
    
    // Set up WebSocket event handlers
    websocket.onopen = handleWebSocketOpen;
    websocket.onmessage = handleWebSocketMessage;
    websocket.onclose = handleWebSocketClose;
    websocket.onerror = handleWebSocketError;
    
    console.log('WebSocket connection initiated to:', wsUrl);
  } catch (error) {
    console.error('Failed to create WebSocket connection:', error);
    showNotification('Failed to establish real-time connection', 'danger');
  }
}

// Handle WebSocket Open Event
function handleWebSocketOpen(event) {
  console.log('WebSocket connection opened');
  isConnected = true;
  reconnectAttempts = 0;
  reconnectInterval = 1000; // Reset reconnect interval
  
  // Update UI to show connected status
  updateWebSocketStatus('connected');
  
  // Send authentication message if needed
  sendAuthenticationMessage();
  
  showNotification('Real-time connection established', 'success');
}

// Handle WebSocket Message Event
function handleWebSocketMessage(event) {
  try {
    // Parse the received message
    const message = JSON.parse(event.data);
    console.log('WebSocket message received:', message);
    
    // Handle different message types
    switch (message.type) {
      case 'notification':
        handleNotificationMessage(message);
        break;
      case 'alert':
        handleAlertMessage(message);
        break;
      case 'update':
        handleUpdateMessage(message);
        break;
      case 'delivery_status':
        handleDeliveryStatusMessage(message);
        break;
      case 'appointment_reminder':
        handleAppointmentReminderMessage(message);
        break;
      case 'medication_reminder':
        handleMedicationReminderMessage(message);
        break;
      case 'health_data':
        handleHealthDataMessage(message);
        break;
      default:
        console.log('Unknown message type:', message.type);
    }
  } catch (error) {
    console.error('Error parsing WebSocket message:', error);
  }
}

// Handle WebSocket Close Event
function handleWebSocketClose(event) {
  console.log('WebSocket connection closed', event);
  isConnected = false;
  
  // Update UI to show disconnected status
  updateWebSocketStatus('disconnected');
  
  // Attempt to reconnect if not closed intentionally
  if (!event.wasClean) {
    showNotification('Real-time connection lost. Attempting to reconnect...', 'warning');
    scheduleReconnect();
  }
}

// Handle WebSocket Error Event
function handleWebSocketError(event) {
  console.error('WebSocket error:', event);
  showNotification('Real-time connection error occurred', 'danger');
}

// Schedule Reconnection
function scheduleReconnect() {
  if (reconnectAttempts === 0) {
    reconnectInterval = 1000; // Reset to initial interval
  }
  
  // Calculate next reconnect interval with exponential backoff
  const nextInterval = Math.min(reconnectInterval * reconnectDecay, maxReconnectInterval);
  reconnectInterval = nextInterval;
  reconnectAttempts++;
  
  console.log(`Scheduling reconnect attempt #${reconnectAttempts} in ${reconnectInterval}ms`);
  
  // Schedule reconnect
  setTimeout(() => {
    if (!isConnected) {
      console.log('Attempting to reconnect...');
      initializeWebSocket();
    }
  }, reconnectInterval);
}

// Send Authentication Message
function sendAuthenticationMessage() {
  // This would typically send user authentication details
  // For now, we'll send a simple authentication message
  const authMessage = {
    type: 'authenticate',
    token: localStorage.getItem('authToken') || 'guest'
  };
  
  sendMessage(authMessage);
}

// Handle Notification Message
function handleNotificationMessage(message) {
  console.log('Handling notification message:', message);
  
  // Show notification to user
  showNotification(message.content, message.level || 'info');
  
  // Update notification count if UI element exists
  updateNotificationCount(1);
}

// Handle Alert Message
function handleAlertMessage(message) {
  console.log('Handling alert message:', message);
  
  // Show alert notification
  showNotification(message.content, 'danger');
  
  // Play alert sound if available
  playAlertSound();
}

// Handle Update Message
function handleUpdateMessage(message) {
  console.log('Handling update message:', message);
  
  // Update relevant UI components based on the update type
  switch (message.entity) {
    case 'patient':
      updatePatientInfo(message.data);
      break;
    case 'appointment':
      updateAppointmentInfo(message.data);
      break;
    case 'medication':
      updateMedicationInfo(message.data);
      break;
    default:
      console.log('Unknown update entity:', message.entity);
  }
}

// Handle Delivery Status Message
function handleDeliveryStatusMessage(message) {
  console.log('Handling delivery status message:', message);
  
  // Update delivery status UI
  updateDeliveryStatus(message.deliveryId, message.status, message.location);
  
  // Show notification
  showNotification(`Delivery status updated: ${message.status}`, 'info');
}

// Handle Appointment Reminder Message
function handleAppointmentReminderMessage(message) {
  console.log('Handling appointment reminder message:', message);
  
  // Show reminder notification
  showNotification(`Appointment reminder: ${message.appointmentType} with ${message.doctor} at ${message.time}`, 'info');
  
  // Play reminder sound
  playReminderSound();
}

// Handle Medication Reminder Message
function handleMedicationReminderMessage(message) {
  console.log('Handling medication reminder message:', message);
  
  // Show reminder notification
  showNotification(`Medication reminder: Take ${message.medication} as prescribed`, 'info');
  
  // Play reminder sound
  playReminderSound();
}

// Handle Health Data Message
function handleHealthDataMessage(message) {
  console.log('Handling health data message:', message);
  
  // Update health data charts or displays
  updateHealthDataDisplay(message.dataType, message.data);
}

// Send Message Through WebSocket
function sendMessage(message) {
  if (websocket && websocket.readyState === WebSocket.OPEN) {
    try {
      websocket.send(JSON.stringify(message));
      console.log('Message sent:', message);
      return true;
    } catch (error) {
      console.error('Error sending message:', error);
      return false;
    }
  } else {
    console.warn('WebSocket is not open. Message not sent:', message);
    return false;
  }
}

// Update WebSocket Status in UI
function updateWebSocketStatus(status) {
  const statusElement = document.getElementById('websocket-status');
  if (statusElement) {
    statusElement.className = `websocket-status websocket-status-${status}`;
    statusElement.textContent = status.charAt(0).toUpperCase() + status.slice(1);
  }
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

// Update Patient Info
function updatePatientInfo(patientData) {
  // This would update patient information in the UI
  console.log('Updating patient info:', patientData);
}

// Update Appointment Info
function updateAppointmentInfo(appointmentData) {
  // This would update appointment information in the UI
  console.log('Updating appointment info:', appointmentData);
}

// Update Medication Info
function updateMedicationInfo(medicationData) {
  // This would update medication information in the UI
  console.log('Updating medication info:', medicationData);
}

// Update Delivery Status
function updateDeliveryStatus(deliveryId, status, location) {
  // This would update delivery status in the UI
  console.log(`Updating delivery ${deliveryId} status to ${status} at ${location}`);
}

// Update Health Data Display
function updateHealthDataDisplay(dataType, data) {
  // This would update health data displays (charts, graphs, etc.)
  console.log(`Updating health data display for ${dataType}:`, data);
}

// Play Alert Sound
function playAlertSound() {
  // This would play an alert sound
  console.log('Playing alert sound');
  
  // Example using Web Audio API:
  /*
  try {
    const context = new (window.AudioContext || window.webkitAudioContext)();
    const oscillator = context.createOscillator();
    const gainNode = context.createGain();
    
    oscillator.connect(gainNode);
    gainNode.connect(context.destination);
    
    oscillator.type = 'sine';
    oscillator.frequency.value = 880; // A5 note
    gainNode.gain.value = 0.5;
    
    oscillator.start();
    setTimeout(() => {
      oscillator.stop();
    }, 500);
  } catch (error) {
    console.error('Error playing alert sound:', error);
  }
  */
}

// Play Reminder Sound
function playReminderSound() {
  // This would play a reminder sound
  console.log('Playing reminder sound');
}

// Setup WebSocket Controls
function setupWebSocketControls() {
  // Handle manual reconnect button
  const reconnectBtn = document.getElementById('websocket-reconnect');
  if (reconnectBtn) {
    reconnectBtn.addEventListener('click', function() {
      if (!isConnected) {
        reconnectBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Connecting...';
        reconnectBtn.disabled = true;
        
        initializeWebSocket();
        
        // Reset button after a delay
        setTimeout(() => {
          reconnectBtn.innerHTML = '<i class="fas fa-sync"></i> Reconnect';
          reconnectBtn.disabled = false;
        }, 3000);
      }
    });
  }
  
  // Handle disconnect button
  const disconnectBtn = document.getElementById('websocket-disconnect');
  if (disconnectBtn) {
    disconnectBtn.addEventListener('click', function() {
      if (websocket) {
        websocket.close();
        isConnected = false;
        updateWebSocketStatus('disconnected');
        showNotification('Disconnected from real-time service', 'info');
      }
    });
  }
}

// Close WebSocket Connection
function closeWebSocket() {
  if (websocket) {
    websocket.close();
    isConnected = false;
    console.log('WebSocket connection closed manually');
  }
}

// Export functions for global use
window.sendMessage = sendMessage;
window.closeWebSocket = closeWebSocket;