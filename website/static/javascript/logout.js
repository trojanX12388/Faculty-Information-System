function logout() {
    // ... (your existing logout code)

    localStorage.setItem('entry', 3);  // Reset entry count to 3 in local storage
    // ... (any additional code for logging out)
}