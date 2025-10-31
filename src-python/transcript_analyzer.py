import requests
import json
from pathlib import Path
from datetime import datetime

class OllamaTranscriptAnalyzer:
    def __init__(self, ollama_host="http://192.168.68.10:11434", base_dir=None):
        self.ollama_host = ollama_host
        
        # Set base directory (default to script's parent directory)
        if base_dir is None:
            self.base_dir = Path(__file__).parent.parent
        else:
            self.base_dir = Path(base_dir)
        
        # Define folder structure
        self.transcripts_dir = self.base_dir / "transcripts"
        self.analysis_dir = self.base_dir / "analysis"
        
        # Ensure directories exist
        self.transcripts_dir.mkdir(exist_ok=True)
        self.analysis_dir.mkdir(exist_ok=True)
    
    def check_model_availability(self, model="gemma3n:latest"):
        """Check if the specified model is available"""
        try:
            available_models = self.check_ollama_connection()
            
            # Check for exact match or base name match
            model_base = model.split(':')[0]
            matching_models = [m for m in available_models if m.startswith(model_base)]
            
            if model in available_models or matching_models:
                print(f"✅ Model available: {model if model in available_models else matching_models[0]}")
                return True
            else:
                print(f"❌ {model} not found")
                print(f"Install with: ollama pull {model}")
                
                # Suggest alternatives
                alternatives = [m for m in available_models if 'gemma' in m.lower()]
                if alternatives:
                    print(f"Available Gemma models: {alternatives}")
                else:
                    print("Fallback options: llama3:latest, llama3.2:3b")
                return False
        except:
            return False
    
    def check_ollama_connection(self):
        """Check if Ollama is running and what models are available"""
        try:
            response = requests.get(f"{self.ollama_host}/api/tags")
            if response.status_code == 200:
                models = response.json()
                model_names = [model['name'] for model in models.get('models', [])]
                print("✅ Ollama is running")
                print("\nAvailable models:")
                for model in model_names:
                    print(f"  - {model}")
                return model_names
            else:
                print("❌ Could not connect to Ollama")
                return []
        except Exception as e:
            print(f"❌ Error connecting to Ollama: {e}")
            print("Make sure Ollama is running: ollama serve")
            return []
    
    def chunk_transcript(self, content, max_chars=25000):
        """Chunk transcript into smaller pieces if too large"""
        if len(content) <= max_chars:
            return [content]
        
        print(f"📦 Chunking transcript (too large for single analysis)...")
        
        # Split by paragraphs/lines first
        lines = content.split('\n')
        chunks = []
        current_chunk = []
        current_size = 0
        
        for line in lines:
            line_size = len(line) + 1  # +1 for newline
            if current_size + line_size > max_chars and current_chunk:
                chunks.append('\n'.join(current_chunk))
                current_chunk = [line]
                current_size = line_size
            else:
                current_chunk.append(line)
                current_size += line_size
        
        if current_chunk:
            chunks.append('\n'.join(current_chunk))
        
        print(f"✅ Split into {len(chunks)} chunks")
        return chunks
    
    def analyze_transcript(self, transcript_file, model="gemma3n:latest", analysis_type="summary", output_path=None):
        """Analyze transcript using Ollama with Gemma3n - with chunking support"""

        # Read transcript
        transcript_path = Path(transcript_file)

        # Check if file exists in specified location or transcripts directory
        if not transcript_path.exists():
            transcript_path = self.transcripts_dir / transcript_path.name
            if not transcript_path.exists():
                print(f"❌ Transcript not found: {transcript_file}")
                print(f"❌ Also checked: {transcript_path}")
                return None

        with open(transcript_path, 'r', encoding='utf-8') as f:
            transcript_content = f.read()

        # Check transcript size
        char_count = len(transcript_content)
        print(f"📊 Transcript size: {char_count:,} characters")

        # Variable to store the analysis result
        result = None

        # If transcript is very large, chunk it
        if char_count > 25000:
            print(f"⚠️  Large transcript detected. Processing in chunks...")
            chunks = self.chunk_transcript(transcript_content)

            # Analyze each chunk
            chunk_results = []
            for i, chunk in enumerate(chunks, 1):
                print(f"\n   📝 Analyzing chunk {i}/{len(chunks)}...")
                chunk_result = self._analyze_single(chunk, model, analysis_type)
                if chunk_result:
                    chunk_results.append(chunk_result)
                else:
                    print(f"   ⚠️  Chunk {i} failed, continuing...")

            # Combine results if multiple chunks
            if not chunk_results:
                print("❌ All chunks failed")
                return None
            elif len(chunk_results) == 1:
                result = chunk_results[0]
            else:
                # Synthesize multiple chunks
                print(f"\n🔄 Combining {len(chunk_results)} chunk analyses...")
                result = self._combine_chunk_results(chunk_results, analysis_type)
        else:
            # Single chunk analysis for smaller transcripts
            result = self._analyze_single(transcript_content, model, analysis_type)
            if result is None:
                print("❌ Analysis failed")
                return None

        # Save to output file if path is provided
        if output_path:
            try:
                output_file = Path(output_path)
                output_file.parent.mkdir(parents=True, exist_ok=True)
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result)
                print(f"✅ Analysis saved to: {output_file}")
                return str(output_file)
            except Exception as e:
                print(f"❌ Error saving analysis: {e}")
                return result
        else:
            return result
    
    def _analyze_single(self, transcript_content, model, analysis_type):
        """Analyze a single chunk of transcript"""
        
        # Prepare prompts for different analysis types
        prompts = {
            "summary": """Please provide a concise summary of this meeting transcript. Include:
1. Main topics discussed
2. Key decisions made
3. Action items (if any)
4. Important points raised by participants

Transcript:
""",
            "action_items": """Extract all action items, tasks, and follow-ups from this meeting transcript. Format as a numbered list with clear action items and who they're assigned to (if mentioned).

Transcript:
""",
            "key_points": """Extract the key points and main takeaways from this meeting transcript. Focus on the most important information discussed.

Transcript:
""",
            "sentiment": """Analyze the tone and sentiment of this meeting. Was it collaborative, tense, productive, etc.? Comment on the overall meeting dynamics.

Transcript:
""",
            "questions": """Extract all questions that were asked during this meeting, along with their answers if provided.

Transcript:
""",
            "comprehensive": """Provide a comprehensive analysis of this meeting transcript including:
1. Executive Summary
2. Main Topics and Discussion Points
3. Key Decisions Made
4. Action Items and Assignments
5. Questions Raised and Answers
6. Overall Meeting Sentiment and Effectiveness

Transcript:
"""
        }
        
        prompt = prompts.get(analysis_type, prompts["summary"]) + transcript_content
        
        try:
            url = f"{self.ollama_host}/api/generate"
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "top_p": 0.9,
                    "num_ctx": 32768,  # Increased context window for Gemma3n
                    "num_predict": 2048,  # Limit output length
                }
            }
            
            response = requests.post(url, json=payload, timeout=600)
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                if response_text:
                    return response_text
                else:
                    print("   ⚠️  Empty response from model")
                    return None
            else:
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
                error_msg = error_data.get('error', response.text)
                
                if "not found" in error_msg.lower():
                    print(f"❌ Model '{model}' not found in Ollama!")
                    print(f"Install with: ollama pull {model}")
                elif "resource limitations" in error_msg.lower() or "unexpectedly stopped" in error_msg.lower():
                    print(f"❌ Model crashed (possibly out of memory)")
                    print(f"💡 Try using a smaller model: --model llama3.2:3b")
                    print(f"💡 Or restart Ollama and try again")
                else:
                    print(f"❌ Error: {response.status_code} - {error_msg}")
                return None
                
        except requests.exceptions.Timeout:
            print("❌ Request timed out (model taking too long)")
            return None
        except Exception as e:
            print(f"❌ Analysis error: {e}")
            return None
    
    def _combine_chunk_results(self, chunk_results, analysis_type):
        """Combine multiple chunk analyses into one coherent analysis"""
        combined = f"[Analysis combined from {len(chunk_results)} chunks]\n\n"
        
        for i, result in enumerate(chunk_results, 1):
            combined += f"--- Part {i} ---\n{result}\n\n"
        
        return combined
    
    def create_comprehensive_analysis(self, transcript_file, model="gemma3n:latest"):
        """Create a comprehensive analysis with multiple types"""
        
        transcript_path = Path(transcript_file)
        
        # Check if file exists in specified location or transcripts directory
        if not transcript_path.exists():
            transcript_path = self.transcripts_dir / transcript_path.name
            if not transcript_path.exists():
                print(f"❌ Transcript not found: {transcript_file}")
                print(f"❌ Also checked: {transcript_path}")
                return None
        
        base_name = transcript_path.stem
        
        analyses = {}
        analysis_types = ["summary", "action_items", "key_points", "sentiment"]
        
        print(f"🧠 Creating comprehensive analysis for: {transcript_path.name}")
        print(f"📊 Model: {model}")
        
        for analysis_type in analysis_types:
            print(f"\n{'='*60}")
            print(f"Generating {analysis_type.replace('_', ' ').title()}")
            print(f"{'='*60}")
            result = self.analyze_transcript(str(transcript_path), model, analysis_type)
            if result:
                analyses[analysis_type] = result
                print(f"✅ {analysis_type} complete")
            else:
                print(f"⚠️  {analysis_type} failed, skipping...")
        
        if not analyses:
            print("\n❌ No analyses completed successfully")
            return None
        
        # Save comprehensive analysis to analysis directory
        analysis_file = self.analysis_dir / f"{base_name}_analysis.txt"
        
        with open(analysis_file, 'w', encoding='utf-8') as f:
            f.write(f"Meeting Analysis Report\n")
            f.write(f"Source: {transcript_path.name}\n")
            f.write(f"Model: {model}\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 60 + "\n\n")
            
            for analysis_type, content in analyses.items():
                f.write(f"{analysis_type.upper().replace('_', ' ')}\n")
                f.write("-" * 30 + "\n")
                f.write(content)
                f.write("\n\n")
        
        print(f"\n✅ Comprehensive analysis saved: {analysis_file}")
        print(f"   Completed {len(analyses)}/{len(analysis_types)} analysis types")
        return analysis_file

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze meeting transcripts with Ollama (Gemma3n)")
    parser.add_argument("transcript", nargs='?', help="Transcript file to analyze (in transcripts folder)")
    parser.add_argument("--model", default="gemma3n:latest", 
                       help="Ollama model to use (default: gemma3n:latest)")
    parser.add_argument("--type", choices=["summary", "action_items", "key_points", "sentiment", "questions", "comprehensive"],
                       default="comprehensive", help="Type of analysis (default: comprehensive)")
    parser.add_argument("--check", action="store_true", help="Check Ollama connection and available models")
    parser.add_argument("--base-dir", help="Base directory (default: script parent directory)")
    
    args = parser.parse_args()
    
    analyzer = OllamaTranscriptAnalyzer(base_dir=args.base_dir)
    
    if args.check:
        print("🔍 Checking Ollama Setup")
        print("=" * 50)
        analyzer.check_ollama_connection()
        print(f"\n📁 Folder Structure:")
        print(f"  Base: {analyzer.base_dir}")
        print(f"  Transcripts: {analyzer.transcripts_dir}")
        print(f"  Analysis: {analyzer.analysis_dir}")
        print(f"\nChecking default model ({args.model}):")
        analyzer.check_model_availability(args.model)
        return
    
    if not args.transcript:
        print("Ollama Transcript Analyzer (Gemma3n)")
        print("\nFolder Structure:")
        print("  transcripts/ - Place transcript files here")
        print("  analysis/    - Analysis files saved here")
        print("\nUsage:")
        print("  python ollama_transcript_analyzer.py transcripts/meeting.txt")
        print("  python ollama_transcript_analyzer.py --check")
        print("  python ollama_transcript_analyzer.py meeting.txt --type summary")
        print("  python ollama_transcript_analyzer.py meeting.txt --model llama3:latest")
        print("\nFor large transcripts that cause crashes:")
        print("  python ollama_transcript_analyzer.py meeting.txt --model llama3.2:3b")
        return
    
    # Check if the specified model is available
    if not analyzer.check_model_availability(args.model):
        response = input(f"\nModel {args.model} not found. Continue anyway? (y/n): ")
        if response.lower() != 'y':
            return
    
    print(f"\n🧠 Analyzing transcript with {args.model}")
    print(f"📊 Analysis type: {args.type}")
    print(f"💡 Using Gemma3n for high-quality analysis")
    
    if args.type == "comprehensive":
        result_file = analyzer.create_comprehensive_analysis(args.transcript, args.model)
        if result_file:
            print(f"\n✅ Analysis complete!")
            print(f"📄 Saved to: {result_file}")
    else:
        result = analyzer.analyze_transcript(args.transcript, args.model, args.type)
        if result:
            print(f"\n{'='*60}")
            print(f"{args.type.upper().replace('_', ' ')}")
            print(f"{'='*60}")
            print(result)
            print(f"{'='*60}")
            
            # Save single analysis type to file
            transcript_path = Path(args.transcript)
            if not transcript_path.exists():
                transcript_path = analyzer.transcripts_dir / transcript_path.name
            
            if transcript_path.exists():
                base_name = transcript_path.stem
                analysis_file = analyzer.analysis_dir / f"{base_name}_{args.type}.txt"
                
                with open(analysis_file, 'w', encoding='utf-8') as f:
                    f.write(f"Meeting Analysis - {args.type.replace('_', ' ').title()}\n")
                    f.write(f"Source: {transcript_path.name}\n")
                    f.write(f"Model: {args.model}\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write("=" * 60 + "\n\n")
                    f.write(result)
                
                print(f"\n✅ Analysis saved: {analysis_file}")

if __name__ == "__main__":
    main()
