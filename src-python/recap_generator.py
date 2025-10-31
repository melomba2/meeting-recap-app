import requests
from pathlib import Path
from datetime import datetime
import argparse

class DNDRecapGenerator:
    def __init__(self, ollama_host="http://192.168.68.10:11434", base_dir=None):
        self.ollama_host = ollama_host
        
        # Set base directory
        if base_dir is None:
            self.base_dir = Path(__file__).parent.parent
        else:
            self.base_dir = Path(base_dir)
        
        # Define folder structure
        self.analysis_dir = self.base_dir / "analysis"
        self.recaps_dir = self.base_dir / "recaps"
        
        # Ensure directories exist
        self.analysis_dir.mkdir(exist_ok=True)
        self.recaps_dir.mkdir(exist_ok=True)
    
    def generate_recap(self, analysis_file, model="gemma3n:latest", style="epic", output_path=None):
        """Generate a 'Previously on...' style recap from D&D session analysis"""
        
        # Read analysis file
        analysis_path = Path(analysis_file)
        
        # Check if file exists in specified location or analysis directory
        if not analysis_path.exists():
            analysis_path = self.analysis_dir / analysis_path.name
            if not analysis_path.exists():
                print(f"❌ Analysis file not found: {analysis_file}")
                print(f"❌ Also checked: {analysis_path}")
                return None
        
        print(f"📖 Reading analysis: {analysis_path.name}")
        with open(analysis_path, 'r', encoding='utf-8') as f:
            analysis_content = f.read()
        
        print(f"📊 Analysis size: {len(analysis_content):,} characters")
        
        # Create the recap generation prompt
        recap_prompt = self._create_recap_prompt(analysis_content, style)
        
        print(f"\n🎬 Generating '{style}' style recap...")
        print(f"🤖 Using model: {model}")
        print(f"💡 This may take 1-2 minutes...")
        
        try:
            url = f"{self.ollama_host}/api/generate"
            payload = {
                "model": model,
                "prompt": recap_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,  # Higher for more creative storytelling
                    "top_p": 0.9,
                    "num_ctx": 32768,
                    "num_predict": 2048,
                }
            }
            
            response = requests.post(url, json=payload, timeout=600)
            
            if response.status_code == 200:
                result = response.json()
                recap_text = result.get('response', '')
                
                if output_path:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(recap_text)
                    return output_path
                else:
                    return recap_text
            else:
                error_data = response.json() if response.headers.get('content-type') == 'application/json' else {}
                error_msg = error_data.get('error', response.text)
                print(f"❌ Error: {response.status_code} - {error_msg}")
                return None
                
        except requests.exceptions.Timeout:
            print("❌ Request timed out")
            return None
        except Exception as e:
            print(f"❌ Error generating recap: {e}")
            return None
    
    def save_recap(self, recap_text, analysis_file, style="epic"):
        """Save recap to file with proper naming"""
        try:
            analysis_path = Path(analysis_file)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            recap_filename = f"{analysis_path.stem}_recap_{style}_{timestamp}.txt"
            recap_path = self.recaps_dir / recap_filename

            recap_path.parent.mkdir(parents=True, exist_ok=True)
            with open(recap_path, 'w', encoding='utf-8') as f:
                f.write(recap_text)

            print(f"✅ Recap saved to: {recap_path}")
            return str(recap_path)
        except Exception as e:
            print(f"❌ Error saving recap: {e}")
            return None

    def _create_recap_prompt(self, analysis_content, style):
        """Create a specialized prompt for D&D recap generation"""
        
        style_instructions = {
            "dramatic": """Create a dramatic, engaging recap in the style of a TV show's "Previously on..." segment.
- Use present tense for immediacy
- Build tension and drama
- Focus on cliffhangers and key moments
- Use vivid, cinematic language""",
            
            "narrative": """Create a storytelling-focused recap as if a narrator is recounting the tale.
- Use past tense
- Focus on character development and story progression
- Maintain an epic fantasy tone
- Emphasize emotional beats""",
            
            "concise": """Create a brief, punchy recap hitting only the most essential story beats.
- Keep it under 200 words
- Focus on major plot developments
- Clear and straightforward language""",
            
            "epic": """Create an epic, grand-scale recap in the style of a fantasy novel opening.
- Use rich, descriptive language
- Emphasize the stakes and scale of events
- Heroic and legendary tone
- Build anticipation for what's to come"""
        }
        
        style_guide = style_instructions.get(style, style_instructions["epic"])
        
        prompt = f"""You are creating a "Previously on..." recap for a Dungeons & Dragons campaign session. This will be read aloud by a text-to-speech AI voice.

STYLE: {style_guide}

CRITICAL REQUIREMENTS:
1. **Story Only** - Focus ONLY on narrative events, character moments, and plot developments
2. **Ignore Mechanics** - Do NOT mention: dice rolls, skill checks, ability scores, combat mechanics, game rules
3. **TTS Optimized**:
   - Use short to medium sentences
   - Avoid complex punctuation
   - Write numbers as words (three, not 3)
   - Use clear pacing with periods for pauses
   - Include natural breaks between major beats
4. **Character Focus** - Emphasize what the characters did, felt, discovered, and experienced
5. **Narrative Flow** - Tell the story in chronological order with smooth transitions

FORMAT:
Start with "Previously on [Campaign Name if mentioned]..." or just "Previously..."
Then deliver the recap in 3-5 paragraphs
End with a cliffhanger or hook for the next session

LENGTH: Aim for 250-400 words (about 90-150 seconds when read aloud)

Here is the session analysis to work from:

{analysis_content}

Now create the "Previously on..." recap following all requirements above:"""

        return prompt
    


def main():
    parser = argparse.ArgumentParser(description="Generate D&D 'Previously on...' style recaps from session analysis")
    parser.add_argument("analysis", nargs='?', help="Analysis file to create recap from")
    parser.add_argument("--model", default="gemma3n:latest", 
                       help="Ollama model to use (default: gemma3n:latest)")
    parser.add_argument("--style", choices=["dramatic", "narrative", "concise", "epic"],
                       default="epic", 
                       help="Recap style (default: epic)")
    parser.add_argument("--base-dir", help="Base directory (default: script parent directory)")
    
    args = parser.parse_args()
    
    generator = DNDRecapGenerator(base_dir=args.base_dir)
    
    if not args.analysis:
        print("D&D Recap Generator - 'Previously on...' Style")
        print("=" * 60)
        print("\nCreates TTS-optimized story recaps from D&D session analysis")
        print("\nFolder Structure:")
        print("  analysis/ - Input analysis files")
        print("  recaps/   - Output recap files")
        print("\nUsage:")
        print("  python dnd_recap_generator.py analysis/session_analysis.txt")
        print("  python dnd_recap_generator.py session_analysis.txt --style epic")
        print("  python dnd_recap_generator.py session_analysis.txt --style dramatic")
        print("  python dnd_recap_generator.py session_analysis.txt --style narrative")
        print("\nStyles:")
        print("  epic      - Grand fantasy novel style (DEFAULT)")
        print("  dramatic  - TV show style with tension and cliffhangers")
        print("  narrative - Story-focused, past tense narration")
        print("  concise   - Brief, essential beats only")
        print("\nOutput is optimized for text-to-speech (TTS) reading")
        return
    
    print("=" * 60)
    print("D&D RECAP GENERATOR")
    print("=" * 60)
    
    # Generate recap
    recap_text = generator.generate_recap(args.analysis, args.model, args.style)
    
    if recap_text:
        # Save to file
        recap_file = generator.save_recap(recap_text, args.analysis, args.style)
        
        # Display preview
        print("\n" + "=" * 60)
        print("RECAP PREVIEW")
        print("=" * 60)
        print(recap_text)
        print("=" * 60)
        print(f"\n✅ Complete! Recap ready for TTS")
        print(f"📄 File: {recap_file}")
    else:
        print("\n❌ Failed to generate recap")

if __name__ == "__main__":
    main()
