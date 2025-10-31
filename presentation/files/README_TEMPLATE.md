# Meeting Recap Processor 🎙️→📝

> Transform meeting recordings into transcripts, analysis, and engaging narrative recaps—from professional summaries to epic fantasy tales.

[![Demo Video](https://img.shields.io/badge/▶️-Watch%20Demo-red?style=for-the-badge)](LINK_TO_YOUR_VIDEO)

---

## 🎯 The Problem

We've all been there:
- Back-to-back meetings with scattered notes
- Struggling to remember what was decided
- Boring documentation no one wants to read
- Teammates missing context from meetings they couldn't attend

**What if your meeting notes could be... actually entertaining?**

---

## ✨ The Solution

Meeting Recap Processor is a desktop application that transforms audio/video recordings through three intelligent stages:

### 1. 📝 Transcription
- OpenAI Whisper with GPU acceleration
- Support for local or remote GPU servers
- Multiple model sizes (tiny → large)
- Fast and accurate

### 2. 🔍 Analysis  
- Powered by Ollama (Gemma3n LLM)
- Extracts key decisions and action items
- Identifies discussion themes
- Structures information clearly

### 3. 🎭 Recap Generation
Choose from **four unique styles**:

| Style | Best For | Tone |
|-------|----------|------|
| **📋 Narrative** | Stakeholder updates, professional summaries | Past tense, comprehensive, business-appropriate |
| **🎬 Dramatic** | Team entertainment, creative presentations | "Previously on..." TV style, present tense, cinematic |
| **💬 Casual** | Slack updates, quick team catch-ups | Brief, punchy, straightforward |
| **⚔️ Epic (Bard)** | D&D sessions, creative meetings, fun team updates | Fantasy grand scale, heroic tone, legendary |

---

## 🎪 The Magic: Epic Bard Style

**Before** (boring standup note):
> Team discussed login bug. Sarah will fix by Friday. Mike will test on staging.

**After** (Epic Bard transformation):
> Previously on the Engineering Quest...
> 
> In the sacred halls of the Development Fellowship, a grave matter was brought forth. The dreaded Login Beast, long thought dormant, had risen once more to plague the realm. Lady Sarah, Keeper of the Backend Code, took oath to vanquish this foe before the fifth dawn. Sir Michael of Quality Assurance pledged to verify the beast's demise within the Staging Realm, lest it return to haunt the production lands...

**Make your meetings memorable.** 🎭

---

## 🚀 Key Features

- ✅ **Three-Stage Pipeline**: Transcription → Analysis → Recap
- ✅ **GPU Acceleration**: CUDA-powered Whisper transcription
- ✅ **Flexible Deployment**: Local processing or remote GPU offloading
- ✅ **Four Distinct Styles**: Professional, Dramatic, Casual, or Epic
- ✅ **Desktop Application**: Built with Tauri (Rust + WebView)
- ✅ **AI-Powered**: Whisper for speech-to-text, Ollama for analysis
- ✅ **Cross-Platform**: Works on macOS, Linux, and Windows
- ✅ **Production-Ready**: Multi-tier architecture with error handling

---

## 🏗️ Architecture

![System Architecture](Technical-Diagrams/01_system_architecture.png)

**Multi-Tier Design:**
- **Frontend**: Tauri desktop UI (HTML/CSS/JavaScript)
- **Backend**: Rust process management and Python bridge
- **Processing**: Python modules for transcription, analysis, and recap generation
- **AI Services**: Whisper (transcription), Ollama (analysis & recap)

**See [Technical-Diagrams/](Technical-Diagrams/) for detailed architecture visualizations.**

---

## 🛠️ Technology Stack

**Frontend & Application**
- Tauri (Rust + WebView)
- HTML5, CSS3, Vanilla JavaScript

**Backend & Processing**
- Rust (process orchestration)
- Python 3.10+ (AI integration)

**AI/ML**
- OpenAI Whisper (speech-to-text)
- Ollama (Gemma3n LLM)
- CUDA 12.1+ & cuDNN 9.1+ (GPU acceleration)

**External Services**
- FastAPI (optional remote Whisper server)
- FFmpeg (audio extraction)

**Full tech stack visualization**: [06_technology_stack.png](Technical-Diagrams/06_technology_stack.png)

---

## 💡 Use Cases

### 🏢 Corporate
- Executive meeting summaries
- Stakeholder updates (Narrative style)
- Remote team catch-ups (Casual style)
- Decision documentation

### 🎨 Creative Teams
- Content workshops with personality (Dramatic style)
- Client meeting recaps with flair
- Brainstorming session archives
- Team entertainment

### 🎲 Gaming & Hobbies
- D&D session recaps (Epic Bard style!) ⭐
- Game development meetings
- Tournament summaries
- Community event documentation

### 📚 Education
- Lecture transcription
- Study group notes
- Workshop summaries
- Research meeting documentation

---

## 📊 How It Works

![Processing Pipeline](Technical-Diagrams/02_processing_pipeline.png)

**Stage 1: Transcription** (30 seconds - 2 minutes)
- Upload audio/video file
- Choose Whisper model size
- Select local or remote processing
- Get complete text transcript

**Stage 2: Analysis** (15-30 seconds)
- Feed transcript to Ollama
- Extract decisions, action items, themes
- Structure key information
- Generate analysis document

**Stage 3: Recap Generation** (10-20 seconds)
- Choose your preferred style
- AI generates engaging narrative
- Receive styled recap ready to share

**Total time for 30-minute meeting**: ~2-3 minutes

---

## 🎯 Why This Matters

1. **Solves Real Pain**: Meeting documentation is time-consuming and boring
2. **Accessibility**: Team members who missed meetings can catch up quickly
3. **Engagement**: Fun styles make documentation people actually want to read
4. **Flexibility**: Different styles for different audiences and contexts
5. **Creativity**: Transforms mundane updates into memorable narratives

---

## 🔮 Future Roadmap

- [ ] Real-time transcription during live meetings
- [ ] Speaker diarization (identify who said what)
- [ ] Multi-language support
- [ ] Custom style builder with user templates
- [ ] Web version with cloud deployment
- [ ] Integration APIs (Slack, Teams, Discord bots)
- [ ] Text-to-speech playback with voice acting
- [ ] Meeting highlights video generation

---

## 📚 Documentation

- **Technical Overview**: [TECHNICAL_OVERVIEW.md](Documentation/TECHNICAL_OVERVIEW.md)
- **Architecture Details**: [ARCHITECTURE.md](Documentation/ARCHITECTURE.md)
- **Diagram Guide**: [DIAGRAM_USAGE_GUIDE.md](Technical-Diagrams/DIAGRAM_USAGE_GUIDE.md)
- **Example Outputs**: [DEMO_EXAMPLES.pdf](Examples/DEMO_EXAMPLES.pdf)

---

## 🎬 Demo & Examples

**[▶️ Watch the 90-second demo video](LINK_TO_VIDEO)**

**Screenshots:**
- [Upload Interface](Screenshots/ui_upload_screen.png)
- [Processing View](Screenshots/ui_processing.png)
- [Transcript Output](Screenshots/output_transcript_sample.png)
- [Analysis Output](Screenshots/output_analysis_sample.png)
- [Epic Bard Recap](Screenshots/output_recap_epic.png) ⭐

---

## 🏆 Built For

**Lonely Octopus 1M Livestream X Hackathon**  
*October 2024*

**Team**: [Your Name / Team Name]  
**Contact**: [Your Email]  
**GitHub**: [Your GitHub if applicable]

---

## 🙏 Acknowledgments

- **OpenAI** - Whisper speech recognition
- **Ollama** - Local LLM inference
- **Tauri** - Desktop application framework
- **Lonely Octopus** - For hosting this amazing hackathon

---

## 📄 License

[Your chosen license - MIT recommended for hackathons]

---

## 💬 Why "Meeting Recap Processor"?

Because meetings don't have to be boring—even when you're catching up on them later.

Whether you need a professional stakeholder update or want to turn your standup into an epic quest to vanquish the Login Beast, we've got you covered.

**Transform your meetings from mundane to magical.** ✨

---

*Built with ❤️ and a bit of fantasy flair*
