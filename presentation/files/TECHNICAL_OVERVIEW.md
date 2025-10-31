# Meeting Recap Processor - Technical Overview

*An AI-powered desktop application that transforms meeting recordings into transcriptions, analysis, and engaging narrative recaps*

---

## System Architecture

![System Architecture](Technical-Diagrams/01_system_architecture.png)

The Meeting Recap Processor is built on a modern multi-tier architecture:

**Frontend Layer**: Tauri-based desktop application providing an intuitive interface for file upload, configuration, and results display.

**Application Layer**: Rust backend manages process orchestration, Python bridge communication, and environment setup. Uses JSON-over-stdin/stdout for clean IPC.

**Processing Layer**: Python-based orchestration layer routes commands to specialized processors:
- **Whisper Processor**: Local GPU transcription with CUDA acceleration
- **Remote Whisper Client**: HTTP-based transcription offloading to remote GPU servers
- **Transcript Analyzer**: Ollama-powered analysis extracting key points, decisions, and action items
- **Recap Generator**: Style-specific narrative generation using fine-tuned prompts

---

## The Three-Stage Pipeline

![Processing Pipeline](Technical-Diagrams/02_processing_pipeline.png)

### Stage 1: Transcription
**Input**: Audio/Video file  
**Processing**: OpenAI Whisper model with GPU acceleration  
**Output**: Complete text transcript (.txt)

Options:
- Local processing with CUDA-enabled GPU
- Remote server offloading via FastAPI endpoint
- Multiple model sizes (tiny, base, small, medium, large)

### Stage 2: Analysis
**Input**: Transcript file  
**Processing**: Ollama with Gemma3n LLM model  
**Output**: Structured analysis document (.txt)

Analysis extracts:
- Key discussion points and themes
- Decisions made during the meeting
- Action items with assignees
- Important questions raised
- Context and background information

### Stage 3: Recap Generation
**Input**: Analysis file  
**Processing**: Style-specific prompt engineering with Ollama  
**Output**: Narrative recap in selected style (.txt)

---

## The Differentiator: Four Recap Styles

![Recap Styles](Technical-Diagrams/05_recap_styles.png)

What sets Meeting Recap Processor apart is the ability to transform the same meeting into four distinct narrative styles:

### 1. **NARRATIVE** - Professional & Comprehensive
- Past tense storytelling
- Character development and emotional beats
- Epic fantasy tone
- **Use case**: Stakeholder updates, executive summaries

### 2. **DRAMATIC** - TV Show "Previously On..."
- Present tense for immediacy
- Tension, cliffhangers, and cinematic language
- Fast-paced with dramatic conclusions
- **Use case**: Team entertainment, creative presentations

### 3. **CASUAL** - Brief & Punchy
- Concise (< 200 words)
- Essential plot beats only
- Straightforward language
- **Use case**: Slack updates, quick team catch-ups

### 4. **EPIC (Bard)** - Fantasy Grand Scale
- Grand, heroic tone with rich descriptions
- Fantasy novel opening style
- Emphasis on stakes and legendary moments
- **Use case**: D&D session recaps, creative team meetings, making standups memorable

**Example transformation**:

*Regular meeting note*: "Team discussed login bug. Sarah will fix by Friday. Mike will test on staging."

*Epic Bard style*: "In the sacred halls of the Engineering Fellowship, a grave matter was brought forth. The dreaded Login Beast, long thought dormant, had risen once more to plague the realm. Lady Sarah, Keeper of the Backend Code, took oath to vanquish this foe before the fifth dawn. Sir Michael of Quality Assurance pledged to verify the beast's demise within the Staging Realm, lest it return to haunt the production lands..."

---

## Network Architecture & Deployment Flexibility

![Network Topology](Technical-Diagrams/04_network_topology.png)

The system supports two deployment modes:

### Mode 1: Fully Local Processing
- All processing on single machine
- Requires CUDA-capable GPU
- Fastest for powerful workstations
- No network dependencies

### Mode 2: Hybrid with Remote Transcription
- UI and analysis run locally
- Transcription offloaded to remote GPU server
- Ideal for laptops or machines without powerful GPUs
- FastAPI server handles remote Whisper processing

**Ollama Server**: Runs on local network (192.168.x.x:11434) for LLM inference, shared across all modes.

---

## Technology Stack

![Tech Stack](Technical-Diagrams/06_technology_stack.png)

### Core Technologies
**Frontend**: Tauri (Rust + WebView), HTML5, CSS3, Vanilla JavaScript  
**Backend**: Rust (process management, IPC), Python 3.10+ (AI orchestration)  
**AI/ML**: OpenAI Whisper, Ollama, Gemma3n LLM  
**GPU**: CUDA 12.1+, cuDNN 9.1+  
**External**: FastAPI (remote server), FFmpeg (audio extraction)

### Key Libraries
**Python**: `openai-whisper`, `torch`, `requests`  
**Rust**: `serde_json`, `tauri`, `tauri-plugin-dialog`

---

## Component Communication

![Communication Flow](Technical-Diagrams/03_communication_flow.png)

**IPC Architecture**: Clean separation between layers using JSON-based command/response protocol

**Command Flow**:
1. User interacts with Tauri frontend
2. JavaScript invokes Tauri commands
3. Rust backend spawns Python process with environment setup
4. Python command router directs to appropriate processor
5. Results returned through response chain
6. Frontend updates with completion status and output paths

**Benefits**:
- Modular and maintainable
- Easy to add new commands and processors
- Clear error boundaries
- Language-agnostic communication protocol

---

## Key Technical Achievements

1. **Sophisticated Multi-Tier Architecture**: Clean separation of concerns across UI, backend, and processing layers

2. **Flexible GPU Strategy**: Support for both local and remote GPU processing makes the tool accessible across different hardware configurations

3. **Style-Specific Prompt Engineering**: Four distinct recap styles achieved through carefully crafted prompts and model configuration

4. **Production-Quality Error Handling**: Comprehensive error capture and reporting across the entire stack

5. **Cross-Platform Desktop App**: Native performance with web technologies through Tauri

6. **Extensible Design**: Command routing pattern makes adding new features straightforward

---

## Performance Characteristics

**Analysis Time**: 
- Typically 15-30 seconds for 30-minute meeting transcript
- Depends on transcript length and Ollama model size

**Recap Generation**: 
- 10-20 seconds per style
- Temperature: 0.7 (balanced creativity)
- Context window: 32,768 tokens
- Max output: 2,048 tokens (250-400 words)

---

## Future Roadmap

- **Real-time Processing**: Stream transcription during live meetings
- **Speaker Diarization**: Identify and label different speakers
- **Multi-Language Support**: Transcription and recap in multiple languages
- **Custom Style Builder**: User-defined recap styles with template system
- **Cloud Deployment**: Web-based version with authenticated user accounts
- **Integration APIs**: Slack, Teams, Discord bot integrations
- **Audio Generation**: Text-to-speech for recap playback with dramatic voice acting

---

## Use Cases

**Corporate**: 
- Executive meeting summaries
- Stakeholder updates
- Remote worker catch-up
- Compliance documentation

**Creative**:
- Content creation workshops
- Brainstorming session archives
- Client meeting recaps with personality
- Creative brief documentation

**Gaming**:
- D&D session recaps
- Game development meeting notes
- Community event summaries
- Tournament recaps

**Education**:
- Lecture transcription
- Study group notes
- Workshop documentation
- Thesis defense records

---

## Conclusion

The Meeting Recap Processor combines technical sophistication with creative delight. The architecture is production-ready and extensible, while the four-style recap system brings personality and engagement to typically mundane meeting documentation.

By solving both the practical problem of meeting documentation AND the creative challenge of making that documentation engaging, we've built a tool that spans professional utility and entertainment value.

**The result**: Meetings don't have to be boring—even when you're catching up on them later.

---

*For detailed architectural documentation, see ARCHITECTURE.md*  
*For diagram usage in presentations, see DIAGRAM_USAGE_GUIDE.md*
