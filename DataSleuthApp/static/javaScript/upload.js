// Function to close dropdowns when clicking outside
function closeDropdowns(event) {
    const dropdowns = document.querySelectorAll('.agent-checkbox-dropdown');
    dropdowns.forEach(dropdown => {
        if (event.target.closest('.dropdown-container') === null) {
            dropdown.style.display = 'none';
        }
    });
}

// Add event listener for clicking outside
document.addEventListener('click', closeDropdowns);

// JavaScript to toggle the dropdown and select/deselect agents
function toggleAgentSelection() {
    const isMultiple = document.getElementById('multipleAgent').checked;

    // Save the previous values
    const selectedSingleAgent = document.querySelector('input[name="singleAgent"]:checked');
    const selectedMultipleAgents = Array.from(document.querySelectorAll('.agent-checkbox:checked')).map(cb => cb.value);

    // Show/hide dropdowns based on selection
    document.getElementById('singleAgentDropdown').style.display = isMultiple ? 'none' : 'block';
    document.getElementById('multipleAgentDropdown').style.display = isMultiple ? 'block' : 'none';

    // Restore previous values after toggle
    if (!isMultiple && selectedSingleAgent) {
        document.getElementById(selectedSingleAgent.id).checked = true;
    }

    if (isMultiple) {
        selectedMultipleAgents.forEach(agent => {
            document.getElementById(agent).checked = true;
        });
        updateSelectedCount();
    }
}

// Function to toggle dropdown visibility
function toggleDropdown(dropdownId) {
    const dropdown = document.getElementById(dropdownId);
    dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
}

// Function to select or deselect all agents
function toggleSelectAll(checked) {
    const checkboxes = document.querySelectorAll('.agent-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.checked = checked;
    });
    updateSelectedCount();
}

// Function to update selected count
function updateSelectedCount() {
    const selectedCount = document.querySelectorAll('.agent-checkbox:checked').length;
    document.getElementById('selectedCount').textContent = `${selectedCount} agent(s) selected`;
}

// Function to filter agents in the dropdown
function filterAgents(type) {
    const searchTerm = type === 'single' ? document.getElementById('searchSingle').value.toLowerCase() : document.getElementById('searchMultiple').value.toLowerCase();
    const agents = type === 'single' ? document.querySelectorAll('.single-agent') : document.querySelectorAll('.multiple-agent');

    let anyVisible = false;

    agents.forEach(agent => {
        const agentName = agent.textContent.trim().toLowerCase();
        const isVisible = agentName.includes(searchTerm);
        agent.style.display = isVisible ? 'block' : 'none';
        if (isVisible) anyVisible = true;
    });

    // Open the dropdown if any agent matches the search
    const dropdownId = type === 'single' ? 'singleAgentOptions' : 'multipleAgentOptions';
    const dropdown = document.getElementById(dropdownId);
    dropdown.style.display = anyVisible ? 'block' : 'none';
}

// Automatically open dropdown when typing in search input
function handleSearchFocus(type) {
    const dropdownId = type === 'single' ? 'singleAgentOptions' : 'multipleAgentOptions';
    document.getElementById(dropdownId).style.display = 'block';
}

// Function to collect selected agents
function collectSelectedAgents() {
    const selectedAgents = [];
    const singleAgentSelected = document.querySelector('input[name="singleAgent"]:checked');

    // If single agent is selected
    if (singleAgentSelected) {
        selectedAgents.push(singleAgentSelected.value);
    } else {
        // If multiple agents are selected
        const checkboxes = document.querySelectorAll('.agent-checkbox:checked');
        checkboxes.forEach(checkbox => {
            selectedAgents.push(checkbox.value);
        });
    }

    // Store selected agent IDs in hidden input
    document.getElementById('agent_ids').value = JSON.stringify(selectedAgents);
}