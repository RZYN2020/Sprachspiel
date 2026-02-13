/**
 * Sprachspiel Obsidian Plugin
 *
 * Enables creating Anki vocabulary cards directly from Obsidian notes.
 * Communicates with the Sprachspiel HTTP server.
 */

import {
  App,
  Editor,
  MarkdownView,
  Modal,
  Notice,
  Plugin,
  PluginSettingTab,
  Setting,
  TFile,
  Menu,
  Platform
} from 'obsidian';

interface SprachspielSettings {
  serverUrl: string;
  apiKey: string;
  autoSend: boolean;
  showNotifications: boolean;
  wordMarkerPath: string;
}

const DEFAULT_SETTINGS: SprachspielSettings = {
  serverUrl: 'http://localhost:8000',
  apiKey: '',
  autoSend: false,
  showNotifications: true,
  wordMarkerPath: '.sprachspiel/words.json'
};

export default class SprachspielPlugin extends Plugin {
  settings: SprachspielSettings;

  async onload() {
    await this.loadSettings();

    // Add ribbon icon
    this.addRibbonIcon('languages', 'Send to Sprachspiel', (evt: MouseEvent) => {
      this.sendCurrentSelection();
    });

    // Add command to send selection
    this.addCommand({
      id: 'send-to-sprachspiel',
      name: 'Send selection to Sprachspiel',
      editorCallback: (editor: Editor, view: MarkdownView) => {
        this.sendSelection(editor.getSelection(), view.file);
      }
    });

    // Add command to send word under cursor
    this.addCommand({
      id: 'send-word-under-cursor',
      name: 'Send word under cursor to Sprachspiel',
      editorCallback: (editor: Editor, view: MarkdownView) => {
        const word = this.getWordUnderCursor(editor);
        if (word) {
          this.sendSelection(word, view.file);
        } else {
          new Notice('No word under cursor');
        }
      }
    });

    // Add settings tab
    this.addSettingTab(new SprachspielSettingTab(this.app, this));

    // Register event for right-click context menu
    this.registerEvent(
      this.app.workspace.on('editor-menu', (menu: Menu, editor: Editor, view: MarkdownView) => {
        const selection = editor.getSelection();
        if (selection) {
          menu.addItem((item) => {
            item
              .setTitle('Send to Sprachspiel')
              .setIcon('languages')
              .onClick(() => {
                this.sendSelection(selection, view.file);
              });
          });
        }
      })
    );

    // Check server connection on load
    this.checkConnection();

    console.log('Sprachspiel plugin loaded');
  }

  onunload() {
    console.log('Sprachspiel plugin unloaded');
  }

  async loadSettings() {
    this.settings = Object.assign({}, DEFAULT_SETTINGS, await this.loadData());
  }

  async saveSettings() {
    await this.saveData(this.settings);
  }

  /**
   * Get the currently selected text from the active editor
   */
  private getCurrentSelection(): string | null {
    const activeView = this.app.workspace.getActiveViewOfType(MarkdownView);
    if (activeView) {
      return activeView.editor.getSelection();
    }
    return null;
  }

  /**
   * Send the current selection to Sprachspiel
   */
  private async sendCurrentSelection() {
    const selection = this.getCurrentSelection();
    if (!selection) {
      new Notice('No text selected');
      return;
    }

    const activeFile = this.app.workspace.getActiveFile();
    await this.sendSelection(selection, activeFile);
  }

  /**
   * Send selection to Sprachspiel server
   */
  private async sendSelection(selection: string, file: TFile | null) {
    if (this.settings.showNotifications) {
      new Notice(`Sending "${selection.substring(0, 30)}${selection.length > 30 ? '...' : ''}" to Sprachspiel...`);
    }

    try {
      const payload = {
        word: selection,
        source: 'obsidian',
        source_file: file?.path || '',
        url: '',
        context: {
          note_title: file?.basename || ''
        }
      };

      // Also write to marker file for file-based communication
      await this.writeToMarkerFile(payload);

      // If auto-send is enabled, also send via HTTP
      if (this.settings.autoSend) {
        await this.sendViaHttp(payload);
      }

      if (this.settings.showNotifications) {
        new Notice('Word sent to Sprachspiel successfully!');
      }

    } catch (error) {
      console.error('Error sending to Sprachspiel:', error);
      new Notice(`Error: ${error instanceof Error ? error.message : 'Failed to send'}`, 5000);
    }
  }

  /**
   * Write word data to marker file for file-based communication
   */
  private async writeToMarkerFile(data: Record<string, unknown>) {
    const markerPath = this.settings.wordMarkerPath;
    const adapter = this.app.vault.adapter;

    // Ensure directory exists
    const dir = markerPath.substring(0, markerPath.lastIndexOf('/'));
    if (dir && !(await adapter.exists(dir))) {
      await adapter.mkdir(dir);
    }

    // Read existing data
    let words: unknown[] = [];
    try {
      if (await adapter.exists(markerPath)) {
        const content = await adapter.read(markerPath);
        words = JSON.parse(content);
      }
    } catch (error) {
      console.log('No existing words file or parse error');
    }

    // Add new word
    words.push({
      ...data,
      timestamp: Date.now()
    });

    // Write back
    await adapter.write(markerPath, JSON.stringify(words, null, 2));
  }

  /**
   * Send data via HTTP to Sprachspiel server
   */
  private async sendViaHttp(payload: Record<string, unknown>) {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json'
    };

    if (this.settings.apiKey) {
      headers['X-API-Key'] = this.settings.apiKey;
    }

    const response = await fetch(`${this.settings.serverUrl}/api/v1/word`, {
      method: 'POST',
      headers,
      body: JSON.stringify(payload)
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(error);
    }

    return response.json();
  }

  /**
   * Get word under cursor
   */
  private getWordUnderCursor(editor: Editor): string | null {
    const cursor = editor.getCursor();
    const line = editor.getLine(cursor.line);

    // Find word boundaries
    let start = cursor.ch;
    let end = cursor.ch;

    // Expand to word boundaries
    while (start > 0 && /\w/.test(line[start - 1])) {
      start--;
    }
    while (end < line.length && /\w/.test(line[end])) {
      end++;
    }

    const word = line.substring(start, end);
    return word || null;
  }

  /**
   * Check connection to Sprachspiel server
   */
  private async checkConnection() {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 3000);

      const response = await fetch(`${this.settings.serverUrl}/api/v1/health`, {
        method: 'GET',
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      if (response.ok) {
        console.log('Sprachspiel server connected');
      } else {
        console.log('Sprachspiel server returned error');
      }
    } catch (error) {
      console.log('Sprachspiel server not reachable');
    }
  }
}

/**
 * Settings Tab
 */
class SprachspielSettingTab extends PluginSettingTab {
  plugin: SprachspielPlugin;

  constructor(app: App, plugin: SprachspielPlugin) {
    super(app, plugin);
    this.plugin = plugin;
  }

  display(): void {
    const { containerEl } = this;

    containerEl.empty();

    containerEl.createEl('h2', { text: 'Sprachspiel Settings' });

    // Server URL
    new Setting(containerEl)
      .setName('Server URL')
      .setDesc('The URL of your Sprachspiel HTTP server')
      .addText(text => text
        .setPlaceholder('http://localhost:8000')
        .setValue(this.plugin.settings.serverUrl)
        .onChange(async (value) => {
          this.plugin.settings.serverUrl = value;
          await this.plugin.saveSettings();
        }));

    // API Key
    new Setting(containerEl)
      .setName('API Key')
      .setDesc('Optional API key for authentication')
      .addText(text => text
        .setPlaceholder('Enter API key')
        .setValue(this.plugin.settings.apiKey)
        .onChange(async (value) => {
          this.plugin.settings.apiKey = value;
          await this.plugin.saveSettings();
        }));

    // Auto Send
    new Setting(containerEl)
      .setName('Auto-send via HTTP')
      .setDesc('Automatically send words to the HTTP server (otherwise only writes to file)')
      .addToggle(toggle => toggle
        .setValue(this.plugin.settings.autoSend)
        .onChange(async (value) => {
          this.plugin.settings.autoSend = value;
          await this.plugin.saveSettings();
        }));

    // Word Marker Path
    new Setting(containerEl)
      .setName('Word marker file path')
      .setDesc('Path to the JSON file where words are stored')
      .addText(text => text
        .setPlaceholder('.sprachspiel/words.json')
        .setValue(this.plugin.settings.wordMarkerPath)
        .onChange(async (value) => {
          this.plugin.settings.wordMarkerPath = value;
          await this.plugin.saveSettings();
        }));

    // Notifications
    new Setting(containerEl)
      .setName('Show notifications')
      .setDesc('Show notifications when sending words')
      .addToggle(toggle => toggle
        .setValue(this.plugin.settings.showNotifications)
        .onChange(async (value) => {
          this.plugin.settings.showNotifications = value;
          await this.plugin.saveSettings();
        }));

    // Instructions
    containerEl.createEl('h3', { text: 'Usage', cls: 'setting-item' });
    const usageEl = containerEl.createEl('div', { cls: 'setting-item-description' });
    usageEl.innerHTML = `
      <ol>
        <li>Start your Sprachspiel HTTP server (<code>sprachspiel start</code>)</li>
        <li>Select text in any note</li>
        <li>Right-click and choose "Send to Sprachspiel" or use the command palette</li>
        <li>The word will be added to your Sprachspiel queue</li>
      </ol>
    `;
  }
}
