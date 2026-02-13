/**
 * Sprachspiel Browser Extension - Background Script
 *
 * Handles context menu integration, keyboard shortcuts, and communication
 * with the Sprachspiel HTTP server.
 */

// Configuration
const DEFAULT_SERVER_URL = 'http://localhost:8000';

/**
 * Initialize the extension
 */
chrome.runtime.onInstalled.addListener(() => {
  // Create context menu items
  chrome.contextMenus.create({
    id: 'send-to-sprachspiel',
    title: 'Send to Sprachspiel',
    contexts: ['selection']
  });

  chrome.contextMenus.create({
    id: 'send-with-context',
    title: 'Send with Page Context',
    contexts: ['selection'],
    parentId: 'send-to-sprachspiel'
  });

  // Initialize default settings
  chrome.storage.local.set({
    serverUrl: DEFAULT_SERVER_URL,
    apiKey: ''
  });
});

/**
 * Handle context menu clicks
 */
chrome.contextMenus.onClicked.addListener(async (info, tab) => {
  if (info.menuItemId === 'send-to-sprachspiel' ||
      info.parentMenuItemId === 'send-to-sprachspiel') {
    const selectedText = info.selectionText?.trim();

    if (!selectedText) {
      console.log('No text selected');
      return;
    }

    // Store the selected text and context
    const data = {
      selectedText,
      url: tab?.url || '',
      title: tab?.title || '',
      timestamp: Date.now()
    };

    await chrome.storage.local.set(data);

    // Send directly to server if context menu was used
    if (info.menuItemId === 'send-with-context' ||
        info.parentMenuItemId === 'send-to-sprachspiel') {
      await sendToServer(data);
    }

    // Open popup to show confirmation
    chrome.action.openPopup();
  }
});

/**
 * Handle keyboard shortcuts
 */
chrome.commands.onCommand.addListener(async (command) => {
  if (command === 'send-to-sprachspiel') {
    // Get the active tab
    const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

    if (!tab?.id) {
      console.error('No active tab');
      return;
    }

    // Execute script to get selected text
    try {
      const results = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        func: () => window.getSelection()?.toString().trim() || ''
      });

      const selectedText = results[0]?.result || '';

      if (!selectedText) {
        console.log('No text selected');
        // Show notification
        chrome.notifications.create({
          type: 'basic',
          iconUrl: 'icons/icon48.png',
          title: 'Sprachspiel',
          message: 'Please select some text first'
        });
        return;
      }

      // Store and send
      const data = {
        selectedText,
        url: tab.url || '',
        title: tab.title || '',
        timestamp: Date.now()
      };

      await chrome.storage.local.set(data);
      await sendToServer(data);

    } catch (error) {
      console.error('Error executing script:', error);
    }
  }
});

/**
 * Send word data to Sprachspiel server
 */
async function sendToServer(data: { selectedText: string; url: string; title: string; timestamp: number }) {
  try {
    // Get settings
    const settings = await chrome.storage.local.get(['serverUrl', 'apiKey']);
    const serverUrl = settings.serverUrl || DEFAULT_SERVER_URL;

    // Prepare headers
    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    };

    if (settings.apiKey) {
      headers['X-API-Key'] = settings.apiKey;
    }

    // Send request
    const response = await fetch(`${serverUrl}/api/v1/word`, {
      method: 'POST',
      headers,
      body: JSON.stringify({
        word: data.selectedText,
        source: 'browser',
        url: data.url,
        context: {
          page_title: data.title
        }
      })
    });

    if (response.ok) {
      const result = await response.json();

      // Show success notification
      chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icons/icon48.png',
        title: 'Sprachspiel',
        message: `Sent "${data.selectedText.substring(0, 30)}${data.selectedText.length > 30 ? '...' : ''}" to Sprachspiel`
      });

      return result;
    } else {
      const error = await response.text();
      throw new Error(error);
    }
  } catch (error) {
    console.error('Error sending to server:', error);

    // Show error notification
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icons/icon48.png',
      title: 'Sprachspiel Error',
      message: error instanceof Error ? error.message : 'Failed to connect to Sprachspiel server. Is it running?'
    });

    throw error;
  }
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'sendWord') {
    sendToServer(request.data)
      .then(result => sendResponse({ success: true, result }))
      .catch(error => sendResponse({ success: false, error: error.message }));
    return true; // Keep channel open for async
  }
});
