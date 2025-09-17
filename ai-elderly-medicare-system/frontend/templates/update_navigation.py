import os
import re

def update_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Remove existing navigation and sidebar code
    content = re.sub(r'<!-- navigation\.html -->[\s\S]*?<\/nav>', '', content)
    content = re.sub(r'<div class="sidebar">[\s\S]*?<\/div>\s*<\/div>', '', content)
    
    # Add navigation include at the beginning of the body
    if '<body' in content:
        content = content.replace(
            '<body>',
            '''<body>
            <!-- Navigation will be loaded here -->
            <div id="nav-placeholder"></div>'''
        )
    
    # Add CSS and JS includes before </head>
    if '</head>' in content:
        content = content.replace(
            '</head>',
            '''    <!-- Navigation CSS -->
    <link rel="stylesheet" href="css/navigation.css">
    <!-- Font Awesome for icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css">
</head>'''
        )
    
    # Add navigation script before </body>
    if '</body>' in content:
        content = content.replace(
            '</body>',
            '''    <!-- Load navigation -->
    <script>
        fetch('navigation.html')
            .then(response => response.text())
            .then(data => {
                document.getElementById('nav-placeholder').innerHTML = data;
                // Initialize main content margin
                const mainContent = document.querySelector('.main-content');
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
                        const mainContent = document.querySelector('.main-content');
                        if (mainContent) {
                            mainContent.style.marginLeft = sidebar.classList.contains('active') ? '250px' : '0';
                        }
                    });
                }
            });
    </script>
</body>'''
        )
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)

def main():
    templates_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Process all HTML files in the templates directory
    for filename in os.listdir(templates_dir):
        if filename.endswith('.html') and filename != 'navigation.html':
            file_path = os.path.join(templates_dir, filename)
            print(f'Updating {filename}...')
            update_file(file_path)
    
    print('Navigation update complete!')

if __name__ == "__main__":
    main()
