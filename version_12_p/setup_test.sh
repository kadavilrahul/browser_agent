#!/bin/bash
set -e

echo "🔧 Setting up Gmail automation test environment..."

# Copy test credentials to main .env file
cp .env.test .env

echo "✅ Test environment configured"
echo "⚠️  WARNING: .env now contains REAL Gmail credentials"
echo ""
echo "To run the test:"
echo "  source venv/bin/activate"
echo "  python gmail_automation_test.py"
echo ""
echo "To run safely:"
echo "  The script includes multiple safety confirmations"
echo "  You will need to type confirmation messages to proceed"
echo ""
echo "📋 Test will:"
echo "  1. Navigate to Gmail"
echo "  2. Login with kadavil.rahul@gmail.com"
echo "  3. Compose email to orders@nilgiristores.in"
echo "  4. Subject: hello"
echo "  5. Body: how are you"
echo "  6. Send the email"
echo ""
echo "🔒 Security notes:"
echo "  - Uses real credentials"
echo "  - Will send real email"
echo "  - Multiple confirmations required"
echo "  - Screenshots saved for verification"