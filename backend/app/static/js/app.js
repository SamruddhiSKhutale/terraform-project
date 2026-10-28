// Sidebar toggle for mobile
document.addEventListener('DOMContentLoaded', function() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('sidebar');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('show');
        });
        
        // Close sidebar when clicking outside on mobile
        document.addEventListener('click', function(e) {
            if (window.innerWidth < 992 && 
                !sidebar.contains(e.target) && 
                !sidebarToggle.contains(e.target) &&
                sidebar.classList.contains('show')) {
                sidebar.classList.remove('show');
            }
        });
    }
    
    // Auto-dismiss alerts after 5s
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });
});

// Toggle task completion via AJAX
function toggleTask(taskId, checkbox) {
    fetch(`/tasks/${taskId}/toggle`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.error) {
            alert(data.error);
            return;
        }
        
        const taskItem = checkbox.closest('.task-item');
        if (data.status === 'completed') {
            checkbox.classList.add('checked');
            checkbox.innerHTML = '<i class="bi bi-check"></i>';
            taskItem.classList.add('completed');
        } else {
            checkbox.classList.remove('checked');
            checkbox.innerHTML = '';
            taskItem.classList.remove('completed');
        }
        
        // Update progress if present
        const progressBar = document.querySelector(`[data-project-progress]`);
        if (progressBar && data.progress !== undefined) {
            progressBar.style.width = data.progress + '%';
            progressBar.setAttribute('aria-valuenow', data.progress);
            const progressText = document.querySelector('[data-progress-text]');
            if (progressText) progressText.textContent = data.progress + '%';
        }
    })
    .catch(err => console.error(err));
}
