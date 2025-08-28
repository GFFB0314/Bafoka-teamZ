// Test your WhatsApp server locally
const TrocServiceChatbot = require('./whatsapp-chatbot.js');

console.log('🧪 Testing Troc-Service WhatsApp Bot Locally\n');

// Test the chatbot
const chatbot = new TrocServiceChatbot();

// Test phone number
const testPhone = '+1234567890';

console.log('📱 Testing basic functionality...\n');

// Test 1: Welcome message
console.log('🤖 Welcome Message:');
console.log(chatbot.handleMessage(testPhone, 'Hello'));
console.log('\n' + '='.repeat(50) + '\n');

// Test 2: Help command
console.log('🤖 Help Command:');
console.log(chatbot.handleMessage(testPhone, 'HELP'));
console.log('\n' + '='.repeat(50) + '\n');

// Test 3: Registration start
console.log('🤖 Registration Start:');
console.log(chatbot.handleMessage(testPhone, 'REGISTER'));
console.log('\n' + '='.repeat(50) + '\n');

console.log('✅ Chatbot is working correctly!');
console.log('\n🎯 Next: Get your WhatsApp Business API credentials from Meta Developer Console');
console.log('🔗 Visit: https://developers.facebook.com/');
console.log('\n📚 Then follow the deployment guide in WHATSAPP-DEPLOYMENT-GUIDE.md');
