// Calendar JavaScript for AI Elderly Medicare System

// DOM Ready Function
document.addEventListener('DOMContentLoaded', function() {
  // Initialize calendar components
  initializeCalendar();
  initializeCalendarControls();
  initializeEventModal();
  
  console.log('Calendar JavaScript loaded');
});

// Initialize Calendar
function initializeCalendar() {
  // This would typically initialize a full calendar library like FullCalendar
  // For now, we'll create a simple calendar UI
  
  renderCalendar();
  loadCalendarEvents();
}

// Render Calendar
function renderCalendar() {
  const calendarContainer = document.getElementById('calendar-container');
  if (!calendarContainer) return;
  
  const today = new Date();
  const currentMonth = today.getMonth();
  const currentYear = today.getFullYear();
  
  // Create calendar header
  const calendarHeader = document.createElement('div');
  calendarHeader.className = 'calendar-header d-flex justify-content-between align-items-center mb-3';
  calendarHeader.innerHTML = `
    <h5 class="mb-0">${getMonthName(currentMonth)} ${currentYear}</h5>
    <div class="btn-group">
      <button class="btn btn-outline-primary btn-sm" id="prev-month">
        <i class="fas fa-chevron-left"></i>
      </button>
      <button class="btn btn-outline-primary btn-sm" id="next-month">
        <i class="fas fa-chevron-right"></i>
      </button>
    </div>
  `;
  
  // Create calendar grid
  const calendarGrid = document.createElement('div');
  calendarGrid.className = 'calendar-grid';
  calendarGrid.innerHTML = `
    <div class="calendar-days-header d-flex">
      <div class="calendar-day-header">Sun</div>
      <div class="calendar-day-header">Mon</div>
      <div class="calendar-day-header">Tue</div>
      <div class="calendar-day-header">Wed</div>
      <div class="calendar-day-header">Thu</div>
      <div class="calendar-day-header">Fri</div>
      <div class="calendar-day-header">Sat</div>
    </div>
    <div class="calendar-days-grid d-flex flex-wrap" id="calendar-days"></div>
  `;
  
  calendarContainer.innerHTML = '';
  calendarContainer.appendChild(calendarHeader);
  calendarContainer.appendChild(calendarGrid);
  
  // Add event listeners for navigation
  document.getElementById('prev-month').addEventListener('click', function() {
    navigateCalendar(-1);
  });
  
  document.getElementById('next-month').addEventListener('click', function() {
    navigateCalendar(1);
  });
  
  renderCalendarDays(currentMonth, currentYear);
}

// Render Calendar Days
function renderCalendarDays(month, year) {
  const daysContainer = document.getElementById('calendar-days');
  if (!daysContainer) return;
  
  // Clear existing days
  daysContainer.innerHTML = '';
  
  // Get first day of month and number of days
  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  
  // Add empty cells for days before the first day of the month
  for (let i = 0; i < firstDay; i++) {
    const emptyDay = document.createElement('div');
    emptyDay.className = 'calendar-day empty';
    daysContainer.appendChild(emptyDay);
  }
  
  // Add cells for each day of the month
  const today = new Date();
  for (let day = 1; day <= daysInMonth; day++) {
    const dayElement = document.createElement('div');
    dayElement.className = 'calendar-day';
    dayElement.textContent = day;
    
    // Highlight today
    if (day === today.getDate() && month === today.getMonth() && year === today.getFullYear()) {
      dayElement.classList.add('today');
    }
    
    // Add click event to show events for the day
    dayElement.addEventListener('click', function() {
      showDayEvents(year, month, day);
    });
    
    daysContainer.appendChild(dayElement);
  }
}

// Navigate Calendar
function navigateCalendar(direction) {
  // This would typically update the calendar view
  // For now, we'll just show a notification
  const action = direction > 0 ? 'next' : 'previous';
  console.log(`Navigating to ${action} month`);
  showNotification(`Showing ${action} month`, 'info');
}

// Load Calendar Events
function loadCalendarEvents() {
  // This would typically load events from the server
  console.log('Loading calendar events');
  
  // Simulate loading events
  setTimeout(() => {
    console.log('Calendar events loaded');
  }, 500);
}

// Show Day Events
function showDayEvents(year, month, day) {
  // This would typically show events for the selected day
  console.log(`Showing events for ${year}-${month + 1}-${day}`);
  
  // For now, we'll just show a notification
  showNotification(`Showing events for ${getMonthName(month)} ${day}, ${year}`, 'info');
}

// Initialize Calendar Controls
function initializeCalendarControls() {
  // Handle view change buttons
  const viewButtons = document.querySelectorAll('[data-calendar-view]');
  
  viewButtons.forEach(button => {
    button.addEventListener('click', function() {
      const view = this.getAttribute('data-calendar-view');
      changeCalendarView(view);
    });
  });
  
  // Handle filter buttons
  const filterButtons = document.querySelectorAll('[data-calendar-filter]');
  
  filterButtons.forEach(button => {
    button.addEventListener('click', function() {
      const filter = this.getAttribute('data-calendar-filter');
      filterCalendarEvents(filter);
    });
  });
}

// Change Calendar View
function changeCalendarView(view) {
  console.log('Changing calendar view to:', view);
  
  // Remove active class from all view buttons
  document.querySelectorAll('[data-calendar-view]').forEach(btn => {
    btn.classList.remove('active');
  });
  
  // Add active class to clicked button
  event.target.classList.add('active');
  
  showNotification(`Calendar view changed to ${view}`, 'success');
}

// Filter Calendar Events
function filterCalendarEvents(filter) {
  console.log('Filtering calendar events by:', filter);
  showNotification(`Filtering events by ${filter}`, 'info');
}

// Initialize Event Modal
function initializeEventModal() {
  // Handle create event button
  const createEventBtn = document.getElementById('create-event-btn');
  if (createEventBtn) {
    createEventBtn.addEventListener('click', function() {
      showCreateEventModal();
    });
  }
  
  // Handle event form submission
  const eventForm = document.getElementById('event-form');
  if (eventForm) {
    eventForm.addEventListener('submit', function(event) {
      event.preventDefault();
      saveEvent();
    });
  }
}

// Show Create Event Modal
function showCreateEventModal() {
  // This would typically show a modal for creating events
  console.log('Showing create event modal');
  
  // For now, we'll just show a notification
  showNotification('Create event modal would open here', 'info');
}

// Save Event
function saveEvent() {
  // This would typically save an event to the server
  console.log('Saving event');
  
  // Show loading state
  const saveBtn = document.querySelector('#event-form button[type="submit"]');
  if (saveBtn) {
    saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Saving...';
    saveBtn.disabled = true;
  }
  
  // Simulate API call
  setTimeout(() => {
    // Reset button
    if (saveBtn) {
      saveBtn.innerHTML = 'Save Event';
      saveBtn.disabled = false;
    }
    
    // Show success notification
    showNotification('Event saved successfully', 'success');
  }, 1000);
}

// Get Month Name
function getMonthName(monthIndex) {
  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];
  return months[monthIndex];
}

// Format Time for Calendar
function formatCalendarTime(date) {
  const hours = date.getHours();
  const minutes = date.getMinutes();
  const ampm = hours >= 12 ? 'PM' : 'AM';
  const formattedHours = hours % 12 || 12;
  const formattedMinutes = minutes < 10 ? '0' + minutes : minutes;
  return `${formattedHours}:${formattedMinutes} ${ampm}`;
}

// Export functions for global use
window.formatCalendarTime = formatCalendarTime;