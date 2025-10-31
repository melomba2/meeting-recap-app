console.log('main.js loading...');
const { invoke } = window.__TAURI__.core;
const { listen } = window.__TAURI__.event;

console.log('Tauri API loaded');

// Try to import dialog, with error handling
let dialogOpen = null;
try {
  if (window.__TAURI__ && window.__TAURI__.dialog) {
    dialogOpen = window.__TAURI__.dialog.open;
    console.log('Dialog API loaded successfully');
  } else {
    console.error('Tauri dialog API not available');
  }
} catch (error) {
  console.error('Error loading dialog API:', error);
}

// State
let selectedFile = null;

// DOM Elements
const uploadArea = document.getElementById('upload-area');
const selectedFileDiv = document.getElementById('selected-file');
const fileNameSpan = document.getElementById('file-name');
const removeFileBtn = document.getElementById('remove-file');
const startBtn = document.getElementById('start-btn');

const whisperModelSelect = document.getElementById('whisper-model');
const transcriptionModeSelect = document.getElementById('transcription-mode');
const recapStyleSelect = document.getElementById('recap-style');
const runAnalysisCheckbox = document.getElementById('run-analysis');
const generateRecapCheckbox = document.getElementById('generate-recap');

// Remote Whisper Elements
const remoteWhisperConfig = document.getElementById('remote-whisper-config');
const whisperHostInput = document.getElementById('whisper-host');
const testWhisperConnectionBtn = document.getElementById('test-whisper-connection');
const whisperConnectionStatus = document.getElementById('whisper-connection-status');

// Remote Ollama Elements
const remoteOllamaConfig = document.getElementById('remote-ollama-config');
const ollamaHostInput = document.getElementById('ollama-host');
const testOllamaConnectionBtn = document.getElementById('test-ollama-connection');
const ollamaConnectionStatus = document.getElementById('ollama-connection-status');

const progressSection = document.getElementById('progress-section');
const currentStageSpan = document.getElementById('current-stage');
const progressPercentSpan = document.getElementById('progress-percent');
const progressFill = document.getElementById('progress-fill');
const progressMessage = document.getElementById('progress-message');
const resultsSection = document.getElementById('results-section');
const resultsList = document.getElementById('results-list');

// File Upload Handlers
uploadArea.addEventListener('click', async () => {
  console.log('Upload area clicked');
  console.log('Dialog API available:', dialogOpen !== null);

  if (!dialogOpen) {
    console.error('Dialog API not available, trying to load it...');
    alert('File dialog not available. The app may need to restart.');
    return;
  }

  try {
    console.log('Opening file dialog...');
    const selected = await dialogOpen({
      multiple: false,
      filters: [{
        name: 'Media Files',
        extensions: ['mp4', 'mp3', 'wav', 'm4a', 'mkv']
      }]
    });

    console.log('File selected:', selected);

    if (selected && selected !== null) {
      handleFileSelect(selected);
    } else {
      console.log('No file selected (user cancelled)');
    }
  } catch (error) {
    console.error('Error opening file dialog:', error);
    alert(`Error selecting file: ${error}`);
  }
});

// HTML5 drag-and-drop
uploadArea.addEventListener('dragover', (e) => {
  console.log('DRAGOVER event fired');
  e.preventDefault();
  uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
  console.log('DRAGLEAVE event fired');
  uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', async (e) => {
  console.log('DROP event fired');
  e.preventDefault();
  uploadArea.classList.remove('drag-over');

  console.log('File(s) dropped:', e.dataTransfer.files);
  console.log('dataTransfer.types:', e.dataTransfer.types);
  console.log('dataTransfer.items:', e.dataTransfer.items);

  if (e.dataTransfer.files.length > 0) {
    const file = e.dataTransfer.files[0];
    console.log('Dropped file:', file);

    // For drag and drop, we need to read the file path differently in Tauri
    // The file object from drag/drop should have the path property in Tauri
    if (file.path) {
      console.log('File path from drag/drop:', file.path);
      handleFileSelect(file.path, file.name);
    } else {
      console.error('File path not available from drag/drop');
      alert('Could not get file path. Please use the file browser instead.');
    }
  }
});

// Transcription Mode Selection Handler
transcriptionModeSelect.addEventListener('change', (e) => {
  const mode = e.target.value;
  console.log('Transcription mode changed to:', mode);

  if (mode === 'remote') {
    remoteWhisperConfig.style.display = 'block';
    // Load saved whisper host from localStorage if available
    const savedHost = localStorage.getItem('whisper_host');
    if (savedHost) {
      whisperHostInput.value = savedHost;
    }
  } else {
    remoteWhisperConfig.style.display = 'none';
  }

  // Save to localStorage
  localStorage.setItem('transcription_mode', mode);
});

// Test Remote Whisper Connection
testWhisperConnectionBtn.addEventListener('click', async () => {
  const host = whisperHostInput.value || 'http://localhost:9000';
  console.log('Testing Whisper connection to:', host);

  whisperConnectionStatus.textContent = 'Testing connection...';
  whisperConnectionStatus.style.color = '#6b7280';

  try {
    const result = await invoke('check_whisper_health', {
      whisperHost: host
    });

    if (result && result.status === 'online') {
      whisperConnectionStatus.innerHTML = `✅ Connected to ${host}<br>Models: ${(result.models || []).join(', ')}`;
      whisperConnectionStatus.style.color = '#10b981';
      localStorage.setItem('whisper_host', host);
    } else {
      whisperConnectionStatus.textContent = `❌ Server did not respond correctly`;
      whisperConnectionStatus.style.color = '#ef4444';
    }
  } catch (error) {
    whisperConnectionStatus.textContent = `❌ Connection failed: ${error}`;
    whisperConnectionStatus.style.color = '#ef4444';
    console.error('Whisper health check error:', error);
  }
});

// Test Remote Ollama Connection
testOllamaConnectionBtn.addEventListener('click', async () => {
  const host = ollamaHostInput.value || 'http://localhost:11434';
  console.log('Testing Ollama connection to:', host);

  ollamaConnectionStatus.textContent = 'Testing connection...';
  ollamaConnectionStatus.style.color = '#6b7280';

  try {
    const result = await invoke('check_ollama_health', {
      ollamaHost: host
    });

    if (result && result.status === 'online') {
      ollamaConnectionStatus.innerHTML = `✅ Connected to ${host}<br>Models: ${(result.models || []).join(', ')}`;
      ollamaConnectionStatus.style.color = '#10b981';
      localStorage.setItem('ollama_host', host);
    } else {
      ollamaConnectionStatus.textContent = `❌ Server did not respond correctly`;
      ollamaConnectionStatus.style.color = '#ef4444';
    }
  } catch (error) {
    ollamaConnectionStatus.textContent = `❌ Connection failed: ${error}`;
    ollamaConnectionStatus.style.color = '#ef4444';
    console.error('Ollama health check error:', error);
  }
});

// Analysis Checkbox Handler - show/hide Ollama config
runAnalysisCheckbox.addEventListener('change', (e) => {
  const isChecked = e.target.checked;
  console.log('Run analysis changed to:', isChecked);

  if (isChecked) {
    remoteOllamaConfig.style.display = 'block';
    // Load saved Ollama host from localStorage if available
    const savedHost = localStorage.getItem('ollama_host');
    if (savedHost) {
      ollamaHostInput.value = savedHost;
    }
  } else {
    remoteOllamaConfig.style.display = 'none';
  }

  // Save to localStorage
  localStorage.setItem('run_analysis', isChecked);
});

removeFileBtn.addEventListener('click', (e) => {
  e.stopPropagation();
  clearSelectedFile();
});

function handleFileSelect(filePath, fileName = null) {
  console.log('handleFileSelect called with:', filePath, fileName);

  selectedFile = filePath;

  // Extract file name from path if not provided
  if (!fileName) {
    fileName = filePath.split('/').pop().split('\\').pop();
  }

  fileNameSpan.textContent = fileName;

  document.querySelector('.upload-content').style.display = 'none';
  selectedFileDiv.style.display = 'flex';
  startBtn.disabled = false;

  console.log('File selected successfully:', selectedFile);
}

function clearSelectedFile() {
  console.log('Clearing selected file');
  selectedFile = null;
  document.querySelector('.upload-content').style.display = 'block';
  selectedFileDiv.style.display = 'none';
  startBtn.disabled = true;
}

// Start Processing
startBtn.addEventListener('click', async () => {
  console.log('Start Processing button clicked');
  console.log('Selected file:', selectedFile);

  if (!selectedFile) {
    console.error('No file selected!');
    alert('Please select a file first');
    return;
  }

  // Reset UI
  progressSection.style.display = 'block';
  resultsSection.style.display = 'none';
  resultsList.innerHTML = '';
  startBtn.disabled = true;

  const mode = transcriptionModeSelect.value;
  const whisperHost = whisperHostInput.value || 'http://localhost:9000';
  const ollamaHost = ollamaHostInput.value || 'http://localhost:11434';

  const options = {
    file: selectedFile,
    whisperModel: whisperModelSelect.value,
    transcriptionMode: mode,
    whisperHost: whisperHost,
    ollamaHost: ollamaHost,
    recapStyle: recapStyleSelect.value,
    runAnalysis: runAnalysisCheckbox.checked,
    generateRecap: generateRecapCheckbox.checked,
  };

  console.log('Processing options:', options);

  try {
    // Step 1: Transcription
    console.log('Starting transcription...');
    updateProgress('Transcription', 0, 'Starting transcription...');

    console.log('Calling transcribe_audio with:', {
      filePath: options.file,
      model: options.whisperModel,
      mode: options.transcriptionMode,
      whisperHost: options.whisperHost,
    });

    const transcriptResult = await invoke('transcribe_audio', {
      filePath: options.file,
      model: options.whisperModel,
      mode: options.transcriptionMode,
      whisperHost: options.whisperHost,
    });

    console.log('Transcription result:', transcriptResult);
    addResult(`📝 Transcript: ${transcriptResult}`);
    updateProgress('Transcription', 100, 'Transcription complete!');

    // Step 2: Analysis (if enabled)
    if (options.runAnalysis) {
      console.log('Starting analysis...');
      updateProgress('Analysis', 0, 'Analyzing transcript...');

      const analysisResult = await invoke('analyze_transcript', {
        filePath: transcriptResult,
        ollamaHost: options.ollamaHost,
      });

      console.log('Analysis result:', analysisResult);
      addResult(`📊 Analysis: ${analysisResult}`);
      updateProgress('Analysis', 100, 'Analysis complete!');

      // Step 3: Recap Generation (if enabled)
      if (options.generateRecap) {
        console.log('Starting recap generation...');
        updateProgress('Recap Generation', 0, 'Generating recap...');

        const recapResult = await invoke('generate_recap', {
          filePath: analysisResult,
          style: options.recapStyle,
        });

        console.log('Recap result:', recapResult);
        addResult(`🎬 Recap: ${recapResult}`);
        updateProgress('Recap Generation', 100, 'Recap complete!');
      }
    }

    // Show results
    console.log('Processing complete!');
    resultsSection.style.display = 'block';
    startBtn.disabled = false;

  } catch (error) {
    console.error('Processing error:', error);
    alert(`Error: ${error}`);
    startBtn.disabled = false;
    progressSection.style.display = 'none';
  }
});

function updateProgress(stage, percent, message) {
  currentStageSpan.textContent = stage;
  progressPercentSpan.textContent = `${percent}%`;
  progressFill.style.width = `${percent}%`;
  progressMessage.textContent = message;
}

function addResult(text) {
  const p = document.createElement('p');
  p.textContent = text;
  resultsList.appendChild(p);
}

// Listen for progress events from backend
listen('progress', (event) => {
  const { stage, progress, message } = event.payload;
  updateProgress(stage, progress, message);
});

// Initialize - Restore saved preferences
const savedMode = localStorage.getItem('transcription_mode') || 'local';
const savedWhisperHost = localStorage.getItem('whisper_host') || 'http://localhost:9000';
const savedOllamaHost = localStorage.getItem('ollama_host') || 'http://localhost:11434';
const savedRunAnalysis = localStorage.getItem('run_analysis') !== 'false'; // Default to true

transcriptionModeSelect.value = savedMode;
whisperHostInput.value = savedWhisperHost;
ollamaHostInput.value = savedOllamaHost;
runAnalysisCheckbox.checked = savedRunAnalysis;

// Show/hide remote config based on saved mode
if (savedMode === 'remote') {
  remoteWhisperConfig.style.display = 'block';
} else {
  remoteWhisperConfig.style.display = 'none';
}

// Show/hide Ollama config based on analysis checkbox
if (savedRunAnalysis) {
  remoteOllamaConfig.style.display = 'block';
} else {
  remoteOllamaConfig.style.display = 'none';
}

console.log('Meeting Recap Processor initialized');
console.log('Tauri API available:', typeof window.__TAURI__ !== 'undefined');
console.log('Tauri.core available:', typeof window.__TAURI__?.core !== 'undefined');
console.log('Tauri.event available:', typeof window.__TAURI__?.event !== 'undefined');
console.log('Tauri.dialog available:', typeof window.__TAURI__?.dialog !== 'undefined');
console.log('Dialog open function:', dialogOpen !== null);
console.log('Transcription mode loaded:', savedMode);
