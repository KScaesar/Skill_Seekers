#!/usr/bin/env python3
"""
Configuration Enhancer - AI-powered enhancement for config extraction results.

Provides dual-mode AI enhancement (API + LOCAL) for configuration analysis:
- Explain what each setting does
- Suggest best practices and improvements
- Security analysis (hardcoded secrets, exposed credentials)
- Migration suggestions (consolidate configs)
- Context-aware documentation

Similar to GuideEnhancer (C3.3) but for configuration files.
"""

import os
import sys
import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Optional google genai import
GOOGLE_GENAI_AVAILABLE = False
try:
    from google import genai
    GOOGLE_GENAI_AVAILABLE = True
except ImportError:
    pass


@dataclass
class ConfigEnhancement:
    """AI-generated enhancement for a configuration"""
    explanation: str = ""  # What this setting does
    best_practice: str = ""  # Suggested improvement
    security_concern: str = ""  # Security issue (if any)
    migration_suggestion: str = ""  # Consolidation opportunity
    context: str = ""  # Pattern context and usage


@dataclass
class EnhancedConfigFile:
    """Configuration file with AI enhancements"""
    file_path: str
    config_type: str
    purpose: str
    enhancement: ConfigEnhancement
    setting_enhancements: Dict[str, ConfigEnhancement] = field(default_factory=dict)


class ConfigEnhancer:
    """
    AI enhancement for configuration extraction results.

    Supports dual-mode operation:
    - API mode: Uses Gemini API (requires GOOGLE_API_KEY)
    - LOCAL mode: Uses Gemini CLI (no API key needed)
    - AUTO mode: Automatically detects best available mode
    """

    def __init__(self, mode: str = "auto"):
        """
        Initialize ConfigEnhancer.

        Args:
            mode: Enhancement mode - "api", "local", or "auto" (default)
        """
        self.mode = self._detect_mode(mode)
        self.api_key = os.environ.get('GOOGLE_API_KEY')
        self.client = None

        if self.mode == "api" and GOOGLE_GENAI_AVAILABLE and self.api_key:
            self.client = genai.Client(api_key=self.api_key)

    def _detect_mode(self, requested_mode: str) -> str:
        """
        Detect best enhancement mode.

        Args:
            requested_mode: User-requested mode

        Returns:
            Actual mode to use
        """
        if requested_mode in ["api", "local"]:
            return requested_mode

        # Auto-detect
        if os.environ.get('GOOGLE_API_KEY') and GOOGLE_GENAI_AVAILABLE:
            logger.info("🤖 AI enhancement: API mode (Gemini API detected)")
            return "api"
        else:
            logger.info("🤖 AI enhancement: LOCAL mode (using Gemini CLI)")
            return "local"

    def enhance_config_result(self, result: Dict) -> Dict:
        """
        Enhance entire configuration extraction result.

        Args:
            result: ConfigExtractionResult as dict

        Returns:
            Enhanced result with AI insights
        """
        logger.info(f"🔄 Enhancing {len(result.get('config_files', []))} config files...")

        if self.mode == "api":
            return self._enhance_via_api(result)
        else:
            return self._enhance_via_local(result)

    # =========================================================================
    # API MODE - Direct Claude API calls
    # =========================================================================

    def _enhance_via_api(self, result: Dict) -> Dict:
        """Enhance configs using Gemini API"""
        if not self.client:
            logger.error("❌ API mode requested but no API key available")
            return result

        try:
            # Create enhancement prompt
            prompt = self._create_enhancement_prompt(result)

            # Call Gemini API
            logger.info("📡 Calling Gemini API for config analysis...")
            response = self.client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=prompt
            )

            # Parse response
            enhanced_result = self._parse_api_response(response.text, result)
            logger.info("✅ API enhancement complete")
            return enhanced_result

        except Exception as e:
            logger.error(f"❌ API enhancement failed: {e}")
            return result

    def _create_enhancement_prompt(self, result: Dict) -> str:
        """Create prompt for Claude API"""
        config_files = result.get('config_files', [])

        # Summarize configs for prompt
        config_summary = []
        for cf in config_files[:10]:  # Limit to first 10 files
            settings_summary = []
            for setting in cf.get('settings', [])[:5]:  # First 5 settings per file
                settings_summary.append(f"  - {setting['key']}: {setting['value']} ({setting['value_type']})")

            config_summary.append(f"""
File: {cf['relative_path']} ({cf['config_type']})
Purpose: {cf['purpose']}
Settings:
{chr(10).join(settings_summary)}
Patterns: {', '.join(cf.get('patterns', []))}
""")

        prompt = f"""Analyze these configuration files and provide AI-enhanced insights.

CONFIGURATION FILES ({len(config_files)} total, showing first 10):
{chr(10).join(config_summary)}

YOUR TASK: Provide comprehensive analysis in JSON format with these 5 enhancements:

1. **EXPLANATIONS**: For each config file, explain its purpose and key settings
2. **BEST PRACTICES**: Suggest improvements (better structure, naming, organization)
3. **SECURITY ANALYSIS**: Identify hardcoded secrets, exposed credentials, security issues
4. **MIGRATION SUGGESTIONS**: Identify opportunities to consolidate or standardize configs
5. **CONTEXT**: Explain the detected patterns and when to use them

OUTPUT FORMAT (strict JSON):
{{
  "file_enhancements": [
    {{
      "file_path": "path/to/config.json",
      "explanation": "This file configures the database connection...",
      "best_practice": "Consider using environment variables for host/port",
      "security_concern": "⚠️ DATABASE_PASSWORD is hardcoded - move to .env",
      "migration_suggestion": "Consolidate with config.yml (overlapping settings)",
      "context": "Standard PostgreSQL configuration pattern"
    }}
  ],
  "overall_insights": {{
    "config_count": {len(config_files)},
    "security_issues_found": 3,
    "consolidation_opportunities": ["Merge .env and config.json database settings"],
    "recommended_actions": ["Move secrets to environment variables", "Standardize on YAML format"]
  }}
}}

Focus on actionable insights that help developers understand and improve their configuration.
"""
        return prompt

    def _parse_api_response(self, response_text: str, original_result: Dict) -> Dict:
        """Parse Claude API response and merge with original result"""
        try:
            # Extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if not json_match:
                logger.warning("⚠️  No JSON found in API response")
                return original_result

            enhancements = json.loads(json_match.group())

            # Merge enhancements into original result
            original_result['ai_enhancements'] = enhancements

            # Add enhancement flags to config files
            file_enhancements = {e['file_path']: e for e in enhancements.get('file_enhancements', [])}
            for cf in original_result.get('config_files', []):
                file_path = cf.get('relative_path', cf.get('file_path'))
                if file_path in file_enhancements:
                    cf['ai_enhancement'] = file_enhancements[file_path]

            return original_result

        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse API response as JSON: {e}")
            return original_result

    # =========================================================================
    # LOCAL MODE - Claude Code CLI
    # =========================================================================

    def _enhance_via_local(self, result: Dict) -> Dict:
        """Enhance configs using Gemini CLI"""
        try:
            # Create temporary prompt file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                prompt_file = Path(f.name)
                f.write(self._create_local_prompt(result))

            # Create output file path
            output_file = prompt_file.parent / f"{prompt_file.stem}_enhanced.json"

            logger.info("🖥️  Launching Gemini CLI for config analysis...")
            logger.info("⏱️  This will take 30-60 seconds...")

            # Run Gemini CLI
            result_data = self._run_gemini_cli(prompt_file, output_file)

            # Clean up
            prompt_file.unlink()
            if output_file.exists():
                output_file.unlink()

            if result_data:
                # Merge LOCAL enhancements
                original_result['ai_enhancements'] = result_data
                logger.info("✅ LOCAL enhancement complete")
                return original_result
            else:
                logger.warning("⚠️  LOCAL enhancement produced no results")
                return result

        except Exception as e:
            logger.error(f"❌ LOCAL enhancement failed: {e}")
            return result

    def _create_local_prompt(self, result: Dict) -> str:
        """Create prompt file for Gemini CLI"""
        config_files = result.get('config_files', [])

        # Format config data for Claude
        config_data = []
        for cf in config_files[:10]:
            config_data.append(f"""
### {cf['relative_path']} ({cf['config_type']})
- Purpose: {cf['purpose']}
- Patterns: {', '.join(cf.get('patterns', []))}
- Settings count: {len(cf.get('settings', []))}
""")

        prompt = f"""# Configuration Analysis Task

I need you to analyze these configuration files and provide AI-enhanced insights.

## Configuration Files ({len(config_files)} total)

{chr(10).join(config_data)}

## Your Task

Analyze these configs and create a JSON file with the following structure:

```json
{{
  "file_enhancements": [
    {{
      "file_path": "path/to/file",
      "explanation": "What this config does",
      "best_practice": "Suggested improvements",
      "security_concern": "Security issues (if any)",
      "migration_suggestion": "Consolidation opportunities",
      "context": "Pattern explanation"
    }}
  ],
  "overall_insights": {{
    "config_count": {len(config_files)},
    "security_issues_found": 0,
    "consolidation_opportunities": [],
    "recommended_actions": []
  }}
}}
```

Please save the JSON output to a file named `config_enhancement.json` in the current directory.

Focus on actionable insights:
1. Explain what each config does
2. Suggest best practices
3. Identify security concerns (hardcoded secrets, exposed credentials)
4. Suggest consolidation opportunities
5. Explain the detected patterns
"""
        return prompt

    def _run_gemini_cli(self, prompt_file: Path, output_file: Path) -> Optional[Dict]:
        """Run Gemini CLI and wait for completion"""
        try:
            # Read prompt content for stdin
            prompt_content = prompt_file.read_text(encoding='utf-8')

            # Run gemini command with prompt via stdin
            result = subprocess.run(
                ['gemini', '-y'],
                input=prompt_content,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            if result.returncode != 0:
                logger.error(f"❌ Gemini CLI failed: {result.stderr}")
                return None

            # Try to find output file (Claude might save it with different name)
            # Look for JSON files created in the last minute
            import time
            current_time = time.time()
            potential_files = []

            for json_file in prompt_file.parent.glob("*.json"):
                if current_time - json_file.stat().st_mtime < 120:  # Created in last 2 minutes
                    potential_files.append(json_file)

            # Try to load the most recent JSON file
            for json_file in sorted(potential_files, key=lambda f: f.stat().st_mtime, reverse=True):
                try:
                    with open(json_file, 'r') as f:
                        data = json.load(f)
                        if 'file_enhancements' in data or 'overall_insights' in data:
                            logger.info(f"✅ Found enhancement data in {json_file.name}")
                            return data
                except:
                    continue

            logger.warning("⚠️  Could not find enhancement output file")
            return None

        except subprocess.TimeoutExpired:
            logger.error("❌ Gemini CLI timeout (5 minutes)")
            return None
        except Exception as e:
            logger.error(f"❌ Error running Gemini CLI: {e}")
            return None


def main():
    """Command-line interface for config enhancement"""
    import argparse

    parser = argparse.ArgumentParser(
        description='AI-enhance configuration extraction results'
    )
    parser.add_argument(
        'result_file',
        help='Path to config extraction JSON result file'
    )
    parser.add_argument(
        '--mode',
        choices=['auto', 'api', 'local'],
        default='auto',
        help='Enhancement mode (default: auto)'
    )
    parser.add_argument(
        '--output',
        help='Output file for enhanced results (default: <input>_enhanced.json)'
    )

    args = parser.parse_args()

    # Load result file
    try:
        with open(args.result_file, 'r') as f:
            result = json.load(f)
    except Exception as e:
        logger.error(f"❌ Failed to load result file: {e}")
        return 1

    # Enhance
    enhancer = ConfigEnhancer(mode=args.mode)
    enhanced_result = enhancer.enhance_config_result(result)

    # Save
    output_file = args.output or args.result_file.replace('.json', '_enhanced.json')
    try:
        with open(output_file, 'w') as f:
            json.dump(enhanced_result, f, indent=2)
        logger.info(f"✅ Enhanced results saved to: {output_file}")
    except Exception as e:
        logger.error(f"❌ Failed to save results: {e}")
        return 1

    return 0


if __name__ == '__main__':
    sys.exit(main())
