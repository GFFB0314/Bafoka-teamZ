#!/usr/bin/env node

// Quick deployment script for Troc-Service WhatsApp Bot
const fs = require('fs');
const path = require('path');

console.log('🚀 Troc-Service WhatsApp Bot - Quick Deploy\n');

// Check if package.json exists
if (!fs.existsSync('package.json')) {
    console.log('❌ package.json not found. Please run this from your project directory.');
    process.exit(1);
}

// Check if required files exist
const requiredFiles = ['whatsapp-chatbot.js', 'whatsapp-server.js'];
for (const file of requiredFiles) {
    if (!fs.existsSync(file)) {
        console.log(`❌ ${file} not found. Please ensure all files are present.`);
        process.exit(1);
    }
}

console.log('✅ All required files found!');

// Install dependencies
console.log('\n📦 Installing dependencies...');
const { execSync } = require('child_process');

try {
    execSync('npm install express body-parser', { stdio: 'inherit' });
    console.log('✅ Dependencies installed successfully!');
} catch (error) {
    console.log('❌ Failed to install dependencies. Please run manually:');
    console.log('   npm install express body-parser');
    process.exit(1);
}

// Create .env file if it doesn't exist
const envFile = '.env';
if (!fs.existsSync(envFile)) {
    const envContent = `# WhatsApp Business API Configuration
WHATSAPP_ACCESS_TOKEN=your_whatsapp_access_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
VERIFY_TOKEN=troc-service-2024

# Server Configuration
PORT=3000
NODE_ENV=production
`;
    
    fs.writeFileSync(envFile, envContent);
    console.log('✅ Created .env file with template values');
}

// Test the server locally
console.log('\n🧪 Testing server locally...');
try {
    const server = require('./whatsapp-server.js');
    console.log('✅ Server loaded successfully!');
    console.log('✅ Your chatbot is ready for WhatsApp integration!');
} catch (error) {
    console.log('❌ Server test failed:', error.message);
    process.exit(1);
}

console.log('\n🎯 Next Steps:');
console.log('1. Get your WhatsApp Business API credentials from Meta Developer Console');
console.log('2. Update the .env file with your actual credentials');
console.log('3. Deploy to Heroku, Railway, or Render');
console.log('4. Configure your WhatsApp webhook');
console.log('\n📚 See WHATSAPP-DEPLOYMENT-GUIDE.md for detailed instructions');
console.log('\n🚀 Your Troc-Service WhatsApp Bot is ready to deploy!');
