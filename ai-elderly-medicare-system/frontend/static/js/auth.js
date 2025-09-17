// API Base URL - Update this to match your backend
const API_BASE_URL = 'http://localhost:5000/api/v1';

// Check authentication status
function checkAuth() {
    return localStorage.getItem('access_token') !== null;
}

// Update UI based on authentication status
function updateAuthUI() {
    const authButtons = document.getElementById('authButtons');
    const userData = JSON.parse(localStorage.getItem('user_data') || '{}');
    
    if (checkAuth()) {
        // User is logged in
        authButtons.innerHTML = `
            <div class="dropdown">
                <button class="btn btn-outline-primary dropdown-toggle" type="button" id="userDropdown" data-bs-toggle="dropdown" aria-expanded="false">
                    <i class="fas fa-user me-2"></i>${userData.first_name || 'User'}
                </button>
                <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
                    <li><a class="dropdown-item" href="dashboard.html"><i class="fas fa-tachometer-alt me-2"></i>Dashboard</a></li>
                    <li><a class="dropdown-item" href="profile.html"><i class="fas fa-user me-2"></i>Profile</a></li>
                    <li><hr class="dropdown-divider"></li>
                    <li><a class="dropdown-item text-danger" href="#" id="logoutBtn"><i class="fas fa-sign-out-alt me-2"></i>Logout</a></li>
                </ul>
            </div>
        `;
        
        // Add logout handler
        document.getElementById('logoutBtn')?.addEventListener('click', handleLogout);
    } else {
        // User is not logged in
        authButtons.innerHTML = `
            <button class="btn btn-outline-primary me-2" data-bs-toggle="modal" data-bs-target="#loginModal">
                Login
            </button>
            <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#registerModal">
                Register
            </button>
        `;
    }
}

// Handle logout
function handleLogout(e) {
    e.preventDefault();
    localStorage.removeItem('access_token');
    localStorage.removeItem('user_data');
    window.location.href = 'index.html';
}

// Protect routes that require authentication
function protectRoute() {
    if (!checkAuth() && !window.location.href.includes('index.html')) {
        window.location.href = 'index.html';
    }
}

// Initialize auth when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    updateAuthUI();
    
    // Check if we're on a protected page
    if (!window.location.href.includes('index.html')) {
        protectRoute();
    }
});

// Make functions available globally
window.auth = {
    checkAuth,
    updateAuthUI,
    handleLogout,
    protectRoute
};
