// Core script for documentation interactions

document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initMobileMenu();
  initCopyCodeButtons();
  highlightActiveLink();
});

/**
 * Theme Controller (Dark/Light mode support)
 */
function initTheme() {
  const themeToggleBtn = document.getElementById('theme-toggle');
  if (!themeToggleBtn) return;

  // Read stored preference, or fall back to system dark-mode preference
  const storedTheme = localStorage.getItem('theme');
  const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
  
  const activeTheme = storedTheme || (systemPrefersDark ? 'dark' : 'light');
  document.documentElement.setAttribute('data-theme', activeTheme);

  themeToggleBtn.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
  });
}

/**
 * Mobile Navigation Drawer Toggle
 */
function initMobileMenu() {
  const hamburgerBtn = document.getElementById('mobile-menu-toggle');
  const sidebar = document.querySelector('.app-sidebar');

  if (!hamburgerBtn || !sidebar) return;

  hamburgerBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    sidebar.classList.toggle('open');
  });

  // Close sidebar when clicking outside on mobile
  document.addEventListener('click', (e) => {
    if (sidebar.classList.contains('open') && !sidebar.contains(e.target) && e.target !== hamburgerBtn) {
      sidebar.classList.remove('open');
    }
  });
}

/**
 * Dynamically setup Copy buttons for Prism code containers
 */
function initCopyCodeButtons() {
  const codeContainers = document.querySelectorAll('.code-container');
  
  codeContainers.forEach(container => {
    const pre = container.querySelector('pre');
    if (!pre) return;
    
    const copyBtn = container.querySelector('.code-copy-btn');
    if (!copyBtn) return;

    copyBtn.addEventListener('click', () => {
      // Extract raw code, removing line numbers or custom formatting if applicable
      const codeText = pre.innerText.trim();

      navigator.clipboard.writeText(codeText).then(() => {
        copyBtn.classList.add('copied');
        const iconSpan = copyBtn.querySelector('.btn-label') || copyBtn;
        const originalText = iconSpan.innerText;
        
        iconSpan.innerText = 'Copied!';
        
        setTimeout(() => {
          copyBtn.classList.remove('copied');
          iconSpan.innerText = originalText;
        }, 2000);
      }).catch(err => {
        console.error('Failed to copy text: ', err);
      });
    });
  });
}

/**
 * Highlight active page in sidebar
 */
function highlightActiveLink() {
  const currentPath = window.location.pathname;
  const currentFilename = currentPath.substring(currentPath.lastIndexOf('/') + 1);
  const navLinks = document.querySelectorAll('.nav-link');

  navLinks.forEach(link => {
    const href = link.getAttribute('href');
    
    // Exact match, or default to index.html if root path
    if (href === currentFilename || (href === 'index.html' && (currentFilename === '' || currentFilename === '/'))) {
      link.classList.add('active');
    } else {
      link.classList.remove('active');
    }
  });
}
