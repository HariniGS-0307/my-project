/**
 * AI Elderly Medicare System - Main JavaScript
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Handle logout
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            // Clear user session
            localStorage.removeItem('user');
            sessionStorage.clear();
            // Redirect to login page
            window.location.href = 'login.html';
        });
    }

    // Highlight active navigation item
    function highlightActiveNav() {
        const currentPage = window.location.pathname.split('/').pop() || 'dashboard.html';
        document.querySelectorAll('.nav-link').forEach(link => {
            const linkHref = link.getAttribute('href');
            if (linkHref === currentPage) {
                link.classList.add('active');
                // Also highlight parent dropdown if exists
                const parentDropdown = link.closest('.dropdown-menu');
                if (parentDropdown) {
                    const dropdownToggle = parentDropdown.previousElementSibling;
                    if (dropdownToggle) {
                        dropdownToggle.classList.add('active');
                    }
                }
            }
        });
    }

    // Initialize active navigation highlighting
    highlightActiveNav();

    // Handle dropdown submenu on mobile
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            if (window.innerWidth <= 991.98) { // Bootstrap's lg breakpoint
                e.preventDefault();
                e.stopPropagation();
                const parent = this.parentElement;
                const isOpen = this.getAttribute('aria-expanded') === 'true';
                
                // Close all other open dropdowns
                document.querySelectorAll('.dropdown-menu').forEach(menu => {
                    if (menu !== this.nextElementSibling) {
                        menu.classList.remove('show');
                    }
                });
                
                // Toggle current dropdown
                if (!isOpen) {
                    this.nextElementSibling.classList.add('show');
                    this.setAttribute('aria-expanded', 'true');
                } else {
                    this.nextElementSibling.classList.remove('show');
                    this.setAttribute('aria-expanded', 'false');
                }
            }
        });
    });

    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.matches('.dropdown-toggle')) {
            document.querySelectorAll('.dropdown-menu').forEach(menu => {
                menu.classList.remove('show');
            });
            document.querySelectorAll('.dropdown-toggle').forEach(toggle => {
                toggle.setAttribute('aria-expanded', 'false');
            });
        }
    });

    // Handle mobile menu close when clicking on a nav link
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function() {
            if (window.innerWidth <= 991.98) {
                const navbarToggler = document.querySelector('.navbar-toggler');
                const navbarCollapse = document.querySelector('.navbar-collapse');
                if (navbarCollapse.classList.contains('show')) {
                    navbarCollapse.classList.remove('show');
                    navbarToggler.setAttribute('aria-expanded', 'false');
                }
            }
        });
    });

    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 100, // Account for fixed header
                    behavior: 'smooth'
                });
            }
        });
    });

    // Add active class to nav links on scroll
    const sections = document.querySelectorAll('section[id]');
    window.addEventListener('scroll', function() {
        let current = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop - 150;
            const sectionHeight = section.offsetHeight;
            if (window.pageYOffset >= sectionTop && window.pageYOffset < sectionTop + sectionHeight) {
                current = '#' + section.getAttribute('id');
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === current) {
                link.classList.add('active');
            }
        });
    });

    // Handle page load with hash in URL
    if (window.location.hash) {
        const targetElement = document.querySelector(window.location.hash);
        if (targetElement) {
            setTimeout(() => {
                window.scrollTo({
                    top: targetElement.offsetTop - 100,
                    behavior: 'smooth'
                });
            }, 100);
        }
    }

    // Initialize Bootstrap components
    initBootstrapComponents();
    
    // Initialize sidebar functionality
    initSidebar();
    
    // Initialize form validation
    initFormValidation();
    
    // Initialize AJAX forms
    initAjaxForms();
    
    // Initialize tooltips and popovers
    initTooltipsAndPopovers();
});

/**
 * Initialize all Bootstrap components
 */
function initBootstrapComponents() {
    // Tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(el => new bootstrap.Tooltip(el));

    // Popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(el => new bootstrap.Popover(el));

    // Dropdowns
    const dropdownElementList = [].slice.call(document.querySelectorAll('.dropdown-toggle'));
    dropdownElementList.map(el => new bootstrap.Dropdown(el));
}

/**
 * Initialize sidebar functionality
 */
function initSidebar() {
    const sidebarToggler = document.querySelector('.sidebar-toggler');
    const sidebar = document.querySelector('.sidebar');
    const sidebarOverlay = document.querySelector('.sidebar-overlay');
    
    if (sidebarToggler && sidebar) {
        sidebarToggler.addEventListener('click', () => {
            document.body.classList.toggle('sidebar-collapsed');
            sidebar.classList.toggle('show');
            if (sidebarOverlay) {
                sidebarOverlay.classList.toggle('show');
            }
            
            // Save sidebar state to localStorage
            const isCollapsed = document.body.classList.contains('sidebar-collapsed');
            localStorage.setItem('sidebarCollapsed', isCollapsed);
        });
    }

    // Close sidebar when clicking on overlay
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', () => {
            document.body.classList.remove('sidebar-collapsed');
            if (sidebar) sidebar.classList.remove('show');
            sidebarOverlay.classList.remove('show');
            
            // Save sidebar state to localStorage
            localStorage.setItem('sidebarCollapsed', false);
        });
    }

    // Toggle submenu in sidebar
    const hasSubmenu = document.querySelectorAll('.has-submenu > a');
    hasSubmenu.forEach(element => {
        element.addEventListener('click', function(e) {
            // Only prevent default on desktop, allow on mobile
            if (window.innerWidth > 992) {
                e.preventDefault();
            }
            
            const submenu = this.nextElementSibling;
            const parent = this.parentElement;
            
            // On mobile, let the link work normally
            if (window.innerWidth <= 992) {
                return;
            }
            
            // Close other open submenus
            document.querySelectorAll('.has-submenu').forEach(item => {
                if (item !== parent) {
                    item.classList.remove('open');
                    const otherSubmenu = item.querySelector('.submenu');
                    if (otherSubmenu) {
                        otherSubmenu.style.display = 'none';
                        otherSubmenu.classList.remove('show');
                    }
                }
            });
            
            // Toggle current submenu
            parent.classList.toggle('open');
            if (submenu) {
                submenu.classList.toggle('show');
                submenu.style.display = submenu.style.display === 'block' ? 'none' : 'block';
            }
        });
    });
    
    // Handle hover for collapsed sidebar on desktop
    if (sidebar) {
        sidebar.addEventListener('mouseenter', function() {
            if (document.body.classList.contains('sidebar-collapsed') && window.innerWidth > 992) {
                document.body.classList.add('sidebar-hover');
            }
        });
        
        sidebar.addEventListener('mouseleave', function() {
            document.body.classList.remove('sidebar-hover');
        });
    }
    
    // Restore sidebar state from localStorage
    const savedCollapsedState = localStorage.getItem('sidebarCollapsed') === 'true';
    if (savedCollapsedState) {
        document.body.classList.add('sidebar-collapsed');
    }
}

/**
 * Initialize form validation
 */
function initFormValidation() {
    // Validate forms with .needs-validation class
    const forms = document.querySelectorAll('.needs-validation');
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // File input preview
    const fileInputs = document.querySelectorAll('.custom-file-input');
    fileInputs.forEach(input => {
        input.addEventListener('change', function() {
            const fileName = this.files[0]?.name || 'Choose file';
            const label = this.nextElementSibling;
            if (label) label.textContent = fileName;
        });
    });
}

/**
 * Initialize AJAX forms
 */
function initAjaxForms() {
    const ajaxForms = document.querySelectorAll('.ajax-form');
    ajaxForms.forEach(form => {
        form.addEventListener('submit', handleAjaxFormSubmit);
    });
}

/**
 * Handle AJAX form submission
 */
function handleAjaxFormSubmit(e) {
    e.preventDefault();
    
    const form = e.target;
    const formData = new FormData(form);
    const submitBtn = form.querySelector('[type="submit"]');
    const originalBtnText = submitBtn?.innerHTML || '';
    
    // Show loading state
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Processing...';
    }
    
    fetch(form.action, {
        method: form.method,
        body: formData,
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.redirect) {
            window.location.href = data.redirect;
        } else if (data.success) {
            showAlert('success', data.message || 'Operation completed successfully');
            if (data.reset_form) form.reset();
            if (data.reload) setTimeout(() => window.location.reload(), 1500);
        } else {
            showAlert('danger', data.message || 'An error occurred');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showAlert('danger', 'An error occurred. Please try again.');
    })
    .finally(() => {
        if (submitBtn) {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalBtnText;
        }
    });
}

/**
 * Initialize tooltips and popovers
 */
function initTooltipsAndPopovers() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(el => new bootstrap.Tooltip(el));

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(el => new bootstrap.Popover(el));
}

/**
 * Show alert message
 */
window.showAlert = function(type, message, duration = 5000) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    const alertContainer = document.getElementById('alert-container') || document.querySelector('.alert-container');
    if (alertContainer) {
        alertContainer.prepend(alertDiv);
    } else {
        document.body.prepend(alertDiv);
    }
    
    // Auto-remove alert after duration
    setTimeout(() => {
        const alert = bootstrap.Alert.getOrCreateInstance(alertDiv);
        alert.close();
    }, duration);
};

/**
 * Helper function to get CSRF token
 */
function getCsrfToken() {
    return document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') || '';
}

/**
 * Helper function for AJAX requests
 */
window.ajaxRequest = function(url, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRF-TOKEN': getCsrfToken()
        },
        credentials: 'same-origin'
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    return fetch(url, options)
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        });
};

// Window resize handler
window.addEventListener('resize', function() {
    // Close sidebar on mobile when resizing to desktop
    if (window.innerWidth > 992) {
        document.body.classList.remove('sidebar-mobile-open');
        const sidebar = document.querySelector('.sidebar');
        if (sidebar) sidebar.classList.remove('show');
        const overlay = document.querySelector('.sidebar-overlay');
        if (overlay) overlay.classList.remove('show');
    }
});