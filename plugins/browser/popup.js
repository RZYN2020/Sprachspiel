/**
 * Sprachspiel Browser Extension - Popup Script
 *
 * Handles the popup UI interactions and communication with the Sprachspiel server.
 */

// State
let selectedText = '';
let isConnected = false;

// DOM Elements
const statusEl = document.getElementById('status');
const statusTextEl = document.getElementById('status-text');
const selectedWordEl = document.getElementById('selected-word');
const serverUrlEl = document.getElementById('server-url');
const apiKeyEl = document.getElementById('api-key');
const btnSettings = document.getElementById('btn-settings');
const btnSend = document.getElementById('btn-send');

/**
 * Initialize the popup
 */
async function init() {
  // Load saved settings
  const settings = await chrome.storage.local.get([
    'serverUrl',
    'apiKey',
    'selectedText'
  ]);

  if (settings.serverUrl) {
    serverUrlEl.value = settings.serverUrl;
  }

  if (settings.apiKey) {
    apiKeyEl.value = settings.apiKey;
  }

  // Get selected text from storage or query active tab
  if (settings.selectedText) {
    selectedText = settings.selectedText;
    updateSelectedWordDisplay();
  } else {
    await getSelectedTextFromTab();
  }

  // Check server connection
  await checkConnection();

  // Set up event listeners
  setupEventListeners();
}

/**
 * Get selected text from the active tab
 */
async function getSelectedTextFromTab() {
  try {
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    if (!tab || !tab.id) {
      selectedWordEl.textContent = 'No active tab';
      return;
    }

    // Execute script to get selected text
    const results = await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => window.getSelection()?.toString().trim() || ''
    });

    selectedText = results[0]?.result || '';
    updateSelectedWordDisplay();

    // Save to storage
    await chrome.storage.local.set({ selectedText });
  } catch (error) {
    console.error('Error getting selected text:', error);
    selectedWordEl.textContent = 'Error reading selection';
  }
}

/**
 * Update the selected word display
 */
function updateSelectedWordDisplay() {
  if (selectedText) {
    // Truncate if too long
    const displayText = selectedText.length > 50
      ? selectedText.substring(0, 50) + '...'
      : selectedText;
    selectedWordEl.textContent = displayText;
    btnSend.disabled = false;
  } else {
    selectedWordEl.textContent = 'Select text on any page';
    btnSend.disabled = true;
  }
}

/**
 * Check connection to Sprachspiel server
 */
async function checkConnection() {
  const serverUrl = serverUrlEl.value.trim();

  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000);

    const response = await fetch(`${serverUrl}/api/v1/health`, {
      method: 'GET',
      signal: controller.signal
    });

    clearTimeout(timeoutId);

    if (response.ok) {
      setConnectionStatus(true);
    } else {
      setConnectionStatus(false);
    }
  } catch (error) {
    console.log('Connection check failed:', error);
    setConnectionStatus(false);
  }
}

/**
 * Set connection status UI
 */
function setConnectionStatus(connected: boolean) {
  isConnected = connected;

  if (connected) {
    statusEl.classList.remove('disconnected');
    statusEl.classList.add('connected');
    statusTextEl.textContent = 'Connected';
  } else {
    statusEl.classList.remove('connected');
    statusEl.classList.add('disconnected');
    statusTextEl.textContent = 'Disconnected - Start sprachspiel server';
  }
}

/**
 * Send selected word to Sprachspiel server
 */
async function sendWord() {
  if (!selectedText) return;

  const serverUrl = serverUrlEl.value.trim();
  const apiKey = apiKeyEl.value.trim();

  btnSend.disabled = true;
  btnSend.textContent = 'Sending...';

  try {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    };

    if (apiKey) {
      headers['X-API-Key'] = apiKey;
    }

    const response = await fetch(`${serverUrl}/api/v1/word`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        word: selectedText,
        source: 'browser',
        url: (await chrome.tabs.query({ active: true, currentWindow: true }))[0]?.url || ''
      })
    });

    if (response.ok) {
      const result = await response.json();
      btnSend.textContent = 'Sent!';
      btnSend.style.background = '#28a745';

      // Clear selection after successful send
      selectedText = '';
      await chrome.storage.local.remove('selectedText');

      setTimeout(() => {
        window.close();
      }, 1000);
    } else {
      const error = await response.text();
      throw new Error(error);
    }
  } catch (error) {
    console.error('Error sending word:', error);
    btnSend.textContent = 'Failed - Retry';
    btnSend.style.background = '#dc3545';
    btnSend.disabled = false;
  }
}

/**
 * Open settings page
 */
function openSettings() {
  // Save current settings first
  const settings = {
    serverUrl: serverUrlEl.value.trim(),
    apiKey: apiKeyEl.value.trim()
  };
  chrome.storage.local.set(settings);

  // For now, just show a simple alert with settings info
  // In a full implementation, this would open a settings page
  alert('Settings saved!\n\nServer URL: ' + settings.serverUrl);
}

/**
 * Set up event listeners
 */
function setupEventListeners() {
  btnSend.addEventListener('click', sendWord);
  btnSettings.addEventListener('click', openSettings);

  // Auto-save settings on change
  serverUrlEl.addEventListener('change', () => {
    chrome.storage.local.set({ serverUrl: serverUrlEl.value.trim() });
    checkConnection();
  });

  apiKeyEl.addEventListener('change', () => {
    chrome.storage.local.set({ apiKey: apiKeyEl.value.trim() });
  });
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', init);
