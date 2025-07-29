// Admin Portal JavaScript Functions

// Utility function to show floating alerts
function showAlert(message, type = 'success') {
    // Create alert container if it doesn't exist
    let alertContainer = document.getElementById('floating-alerts');
    if (!alertContainer) {
        alertContainer = document.createElement('div');
        alertContainer.id = 'floating-alerts';
        alertContainer.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            max-width: 400px;
        `;
        document.body.appendChild(alertContainer);
    }

    // Create the alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show mb-3 shadow`;
    alertDiv.style.cssText = `
        animation: slideInRight 0.3s ease-out;
        margin-bottom: 10px !important;
    `;
    alertDiv.innerHTML = `
        <i class="fas fa-${getAlertIcon(type)} me-2"></i>
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    // Add to container
    alertContainer.appendChild(alertDiv);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alertDiv.style.animation = 'slideOutRight 0.3s ease-in';
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 300);
    }, 5000);

    // Manual dismiss
    alertDiv.querySelector('.btn-close').addEventListener('click', () => {
        alertDiv.style.animation = 'slideOutRight 0.3s ease-in';
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 300);
    });
}

// Helper function to get appropriate icon for alert type
function getAlertIcon(type) {
    switch(type) {
        case 'success': return 'check-circle';
        case 'danger': return 'exclamation-triangle';
        case 'warning': return 'exclamation-circle';
        case 'info': return 'info-circle';
        default: return 'info-circle';
    }
}

// Initialize Database
async function initDatabase() {
    if (!confirm('Are you sure you want to initialize the database? This will create tables and add sample data.')) {
        return;
    }

    try {
        const response = await fetch('/api/v1/init-db', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const result = await response.json();

        if (result.success) {
            showAlert(`Database initialized successfully! Added ${result.total_countries} countries.`, 'success');
            loadStatistics();
        } else {
            showAlert(`Error: ${result.error}`, 'danger');
        }
    } catch (error) {
        showAlert(`Error: ${error.message}`, 'danger');
    }
}

// Clean Database
async function cleanDatabase() {
    if (!confirm('Are you sure you want to clean the database? This will remove ALL countries data!')) {
        return;
    }

    try {
        const response = await fetch('/admin/clean-db', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const result = await response.json();

        if (result.success) {
            showAlert(result.message, 'success');
            loadStatistics();
            document.getElementById('countries-section').style.display = 'none';
        } else {
            showAlert(`Error: ${result.error}`, 'danger');
        }
    } catch (error) {
        showAlert(`Error: ${error.message}`, 'danger');
    }
}

// Initialize Admin Table
async function initAdmins() {
    if (!confirm('Are you sure you want to initialize the admin table? This will create the admins table and add a default admin.')) {
        return;
    }

    try {
        const response = await fetch('/admin/init-admins', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const result = await response.json();

        if (result.success) {
            showAlert(result.message, 'success');
            if (result.default_admin) {
                showAlert(`Default admin created - Username: ${result.default_admin.username}, Password: ${result.default_admin.password}`, 'info');
            }
        } else {
            showAlert(`Error: ${result.error}`, 'danger');
        }
    } catch (error) {
        showAlert(`Error: ${error.message}`, 'danger');
    }
}

// Load Countries
async function loadCountries() {
    try {
        const response = await fetch('/api/v1/countries');
        const result = await response.json();

        const countriesSection = document.getElementById('countries-section');
        const countriesList = document.getElementById('countries-list');

        if (result.success && result.data.length > 0) {
            let html = '<div class="row">';

            result.data.forEach(country => {
                html += `
                    <div class="col-md-6 col-lg-4 mb-3">
                        <div class="country-item">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <span class="country-code">${country.country_code}</span>
                                    <br>
                                    <span class="country-name">${country.country_name}</span>
                                    <br>
                                    <small class="text-muted">ID: ${country.id}</small>
                                </div>
                                <button class="btn btn-sm btn-outline-danger" onclick="removeCountry('${country.country_code}')">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                `;
            });

            html += '</div>';
            countriesList.innerHTML = html;
            countriesSection.style.display = 'block';
        } else {
            countriesList.innerHTML = '<p class="text-muted text-center">No countries found.</p>';
            countriesSection.style.display = 'block';
        }
    } catch (error) {
        showAlert(`Error loading countries: ${error.message}`, 'danger');
    }
}

// Add Country
async function addCountry() {
    const countryCode = document.getElementById('countryCode').value.trim().toUpperCase();
    const countryName = document.getElementById('countryName').value.trim();
    const polygonData = document.getElementById('polygonData').value.trim();

    if (!countryCode || !countryName || !polygonData) {
        showAlert('Please fill in all required fields.', 'warning');
        return;
    }

    // Validate JSON
    try {
        JSON.parse(polygonData);
    } catch (e) {
        showAlert('Invalid JSON format for polygon data.', 'danger');
        return;
    }

    try {
        const response = await fetch('/admin/add-country', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                country_code: countryCode,
                country_name: countryName,
                polygon_data: polygonData
            })
        });

        const result = await response.json();

        if (result.success) {
            showAlert(`Country ${countryCode} added successfully!`, 'success');
            document.getElementById('addCountryForm').reset();
            bootstrap.Modal.getInstance(document.getElementById('addCountryModal')).hide();
            loadStatistics();
            loadCountries();
        } else {
            showAlert(`Error: ${result.error}`, 'danger');
        }
    } catch (error) {
        showAlert(`Error: ${error.message}`, 'danger');
    }
}

// Remove Country
async function removeCountry(countryCode) {
    if (!confirm(`Are you sure you want to remove ${countryCode}?`)) {
        return;
    }

    try {
        const response = await fetch('/admin/remove-country', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                country_code: countryCode
            })
        });

        const result = await response.json();

        if (result.success) {
            showAlert(`Country ${countryCode} removed successfully!`, 'success');
            loadStatistics();
            loadCountries();
        } else {
            showAlert(`Error: ${result.error}`, 'danger');
        }
    } catch (error) {
        showAlert(`Error: ${error.message}`, 'danger');
    }
}

// Add Admin
async function addAdmin() {
    const username = document.getElementById('adminUsername').value.trim();
    const password = document.getElementById('adminPassword').value;
    const email = document.getElementById('adminEmail').value.trim();

    if (!username || !password) {
        showAlert('Username and password are required.', 'warning');
        return;
    }

    try {
        const response = await fetch('/admin/add-admin', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username,
                password: password,
                email: email
            })
        });

        const result = await response.json();

        if (result.success) {
            showAlert(`Admin ${username} added successfully!`, 'success');
            document.getElementById('addAdminForm').reset();
            bootstrap.Modal.getInstance(document.getElementById('addAdminModal')).hide();
        } else {
            showAlert(`Error: ${result.error}`, 'danger');
        }
    } catch (error) {
        showAlert(`Error: ${error.message}`, 'danger');
    }
}

// Load Statistics
async function loadStatistics() {
    try {
        const response = await fetch('/admin/stats');
        const result = await response.json();

        const statsContent = document.getElementById('stats-content');

        if (result.success) {
            statsContent.innerHTML = `
                <div class="row">
                    <div class="col-6">
                        <div class="stats-item">
                            <div class="stats-number">${result.data.countries_count}</div>
                            <div class="stats-label">Countries</div>
                        </div>
                    </div>
                    <div class="col-6">
                        <div class="stats-item">
                            <div class="stats-number">${result.data.admins_count}</div>
                            <div class="stats-label">Admins</div>
                        </div>
                    </div>
                </div>
            `;
        } else {
            statsContent.innerHTML = '<p class="text-muted">Unable to load statistics.</p>';
        }
    } catch (error) {
        document.getElementById('stats-content').innerHTML = '<p class="text-muted">Error loading statistics.</p>';
    }
}

// Load Admins
async function loadAdmins() {
    try {
        const response = await fetch('/admin/admins');
        const result = await response.json();

        const adminsSection = document.getElementById('admins-section');
        const adminsList = document.getElementById('admins-list');

        if (result.success && result.data.length > 0) {
            let html = '<div class="row">';

            result.data.forEach(admin => {
                const isCurrentUser = admin.username === getCurrentUsername();
                html += `
                    <div class="col-md-6 col-lg-4 mb-3">
                        <div class="admin-item">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <span class="admin-username">${admin.username}</span>
                                    ${isCurrentUser ? '<span class="badge bg-primary ms-2">You</span>' : ''}
                                    <br>
                                    <span class="admin-email text-muted">${admin.email || 'No email'}</span>
                                    <br>
                                    <small class="text-muted">ID: ${admin.id}</small>
                                    <br>
                                    <small class="text-muted">Created: ${new Date(admin.created_at).toLocaleDateString()}</small>
                                </div>
                                ${!isCurrentUser ? `
                                    <button class="btn btn-sm btn-outline-danger" onclick="removeAdmin('${admin.username}')">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                `;
            });

            html += '</div>';
            adminsList.innerHTML = html;
            adminsSection.style.display = 'block';
        } else {
            adminsList.innerHTML = '<p class="text-muted text-center">No admin users found.</p>';
            adminsSection.style.display = 'block';
        }
    } catch (error) {
        showAlert(`Error loading admins: ${error.message}`, 'danger');
    }
}

// Remove Admin
async function removeAdmin(username) {
    if (!confirm(`Are you sure you want to remove admin "${username}"?`)) {
        return;
    }

    try {
        const response = await fetch('/admin/remove-admin', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                username: username
            })
        });

        const result = await response.json();

        if (result.success) {
            showAlert(`Admin ${username} removed successfully!`, 'success');
            loadStatistics();
            loadAdmins();
        } else {
            showAlert(`Error: ${result.error}`, 'danger');
        }
    } catch (error) {
        showAlert(`Error: ${error.message}`, 'danger');
    }
}

// Helper function to get current username (you might need to pass this from the server)
function getCurrentUsername() {
    // This is a placeholder - you might want to pass the current username from the server
    // For now, we'll return null and rely on the server-side check
    return null;
}

// Form validation
document.addEventListener('DOMContentLoaded', function() {
    // Country code input formatting
    const countryCodeInput = document.getElementById('countryCode');
    if (countryCodeInput) {
        countryCodeInput.addEventListener('input', function() {
            this.value = this.value.toUpperCase();
        });
    }

    // Auto-resize textarea
    const polygonDataTextarea = document.getElementById('polygonData');
    if (polygonDataTextarea) {
        polygonDataTextarea.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight) + 'px';
        });
    }
});
