import os
import re

def update_file(file_path):
    # Skip navigation.html and login/register related files
    skip_files = ['navigation.html', 'login.html', 'register.html', 'forgot_password.html', 'reset_password.html', 'two_factor.html', 'verify_email.html']
    if any(skip_file.lower() in file_path.lower() for skip_file in skip_files):
        # For login pages, ensure no navigation is included
        if any(page in file_path.lower() for page in ['login.html', 'register.html', 'forgot_password.html', 'reset_password.html', 'two_factor.html', 'verify_email.html']):
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            # Remove any navigation related code
            content = re.sub(r'<link[^>]*navigation\.css[^>]*>', '', content)
            content = re.sub(r'<div id="nav-placeholder">[\s\S]*?<\/div>', '', content)
            content = re.sub(r'<script[^>]*navigation\.html[\s\S]*?<\/script>', '', content)
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(content)
        return False

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Remove any existing navigation/sidebar code
    content = re.sub(r'<div class="sidebar">[\s\S]*?<\/div>', '', content)
    content = re.sub(r'<nav class="sidebar">[\s\S]*?<\/nav>', '', content)
    content = re.sub(r'<!-- navigation\.html -->[\s\S]*?<\/nav>', '', content)
    
    # Add navigation placeholder after body tag
    if '<body' in content and 'id="nav-placeholder"' not in content:
        content = content.replace(
            '<body>',
            '''<body>
            <!-- Navigation will be loaded here -->
            <div id="nav-placeholder"></div>'''
        )
    
    # Add CSS and JS includes before </head>
    if '</head>' in content:
        # Remove any existing navigation CSS/JS
        content = re.sub(r'<link[^>]*navigation\.css[^>]*>', '', content)
        content = re.sub(r'<script[^>]*navigation\.js[^>]*><\/script>', '', content)
        
        # Add required CSS
        css_links = '''
    <!-- Navigation CSS -->
    <link rel="stylesheet" href="css/navigation.css">
    <!-- Font Awesome for icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
'''
        content = content.replace('</head>', f'{css_links}</head>')
    
    # Add navigation script before </body>
    if '</body>' in content and not any(page in file_path.lower() for page in ['login.html', 'register.html', 'forgot_password.html', 'reset_password.html', 'two_factor.html', 'verify_email.html']):
        nav_script = '''
    <!-- Load navigation -->
    <script>
        // Load navigation
        fetch('navigation.html')
            .then(response => response.text())
            .then(data => {
                const navPlaceholder = document.getElementById('nav-placeholder');
                if (navPlaceholder) {
                    navPlaceholder.innerHTML = data;
                    
                    // Initialize main content margin
                    const mainContent = document.querySelector('.main-content, main, .container');
                    if (mainContent) {
                        mainContent.style.marginLeft = '250px';
                        mainContent.style.padding = '20px';
                        mainContent.style.transition = 'margin-left 0.3s ease';
                    }
                    
                    // Add click event for menu toggle
                    const menuToggle = document.getElementById('menuToggle');
                    const sidebar = document.querySelector('.sidebar');
                    if (menuToggle && sidebar) {
                        menuToggle.addEventListener('click', function() {
                            sidebar.classList.toggle('active');
                            const mainContent = document.querySelector('.main-content, main, .container');
                            if (mainContent) {
                                mainContent.style.marginLeft = sidebar.classList.contains('active') ? '250px' : '0';
                            }
                        });
                    }
                }
            });
    </script>
'''
        content = content.replace('</body>', f'{nav_script}</body>')
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    return True

def main():
    templates_dir = os.path.dirname(os.path.abspath(__file__))
    updated_count = 0
    
    # Process all HTML files in the templates directory and subdirectories
    for root, _, files in os.walk(templates_dir):
        for filename in files:
            if filename.endswith('.html'):
                file_path = os.path.join(root, filename)
                try:
                    if update_file(file_path):
                        print(f'Updated: {file_path}')
                        updated_count += 1
                except Exception as e:
                    print(f'Error updating {file_path}: {str(e)}')
    
    print(f'\nNavigation update complete! Updated {updated_count} files.')

if __name__ == "__main__":
    main()
