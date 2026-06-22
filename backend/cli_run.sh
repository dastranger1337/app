#!/bin/bash
# Axiom Red-Team CLI Setup and Launch Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "╔═══════════════════════════════════════════════════════╗"
echo "║         AXIOM RED-TEAM CLI SETUP                      ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | grep -oP '(?<=Python ).*')
echo "✓ Python $PYTHON_VERSION found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

echo "✓ Virtual environment activated"

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements_cli.txt

echo "✓ Dependencies installed"

# Check for required tools
echo ""
echo "🔧 Checking core tools..."

REQUIRED_TOOLS=("bash" "git" "curl" "apt-get")
for tool in "${REQUIRED_TOOLS[@]}"; do
    if command -v "$tool" &> /dev/null; then
        echo "  ✓ $tool"
    else
        echo "  ⚠ $tool not found"
    fi
done

# Configure environment
echo ""
echo "⚙️  Configuring environment..."

if [ ! -f ".env" ]; then
    cat > .env << 'EOF'
# Axiom Red-Team CLI Environment

# AI Provider: emergent (default), openai-compatible
DEFAULT_LLM_PROVIDER=emergent

# Emergent Universal LLM (Claude via emergentintegrations.com)
# Get key from: https://emergentintegrations.com
EMERGENT_LLM_KEY=

# Custom OpenAI-compatible provider (optional)
# Examples: OpenAI, Groq, Mistral, Together, OpenRouter, Ollama, LM Studio, vLLM
CUSTOM_LLM_BASE_URL=
CUSTOM_LLM_API_KEY=
CUSTOM_LLM_MODEL=

# Default model if not specified
DEFAULT_LLM_MODEL=claude-sonnet-4-5-20250929

# Execution timeout (seconds)
EXEC_TIMEOUT_SECONDS=120
EOF
    echo "  ✓ Created .env (configure your API keys)"
else
    echo "  ✓ .env exists"
fi

echo ""
echo "╔═══════════════════════════════════════════════════════╗"
echo "║              AXIOM IS READY                           ║"
echo "╠═══════════════════════════════════════════════════════╣"
echo "║  ⚡ Run:  python3 axiom_cli.py                        ║"
echo "║  📖 Help: /help (in the app)                          ║"
echo "║  🔑 API:  Edit .env with your Emergent/OpenAI keys   ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo ""

# Ask if user wants to run now
read -p "Launch Axiom now? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    python3 axiom_cli.py
fi
