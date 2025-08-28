// Test the Troc-Service WhatsApp Chatbot
const TrocServiceChatbot = require('./whatsapp-chatbot.js');

// Create chatbot instance
const chatbot = new TrocServiceChatbot();

// Test phone number
const testPhone = '+1234567890';

console.log('🤖 Testing Troc-Service WhatsApp Chatbot\n');

// Test 1: Welcome message
console.log('📱 Message: (first message)');
console.log('🤖 Bot:', chatbot.handleMessage(testPhone, 'Hello'));
console.log('\n' + '='.repeat(50) + '\n');

// Test 2: Help command
console.log('📱 Message: HELP');
console.log('🤖 Bot:', chatbot.handleMessage(testPhone, 'HELP'));
console.log('\n' + '='.repeat(50) + '\n');

// Test 3: Start registration
console.log('📱 Message: REGISTER');
console.log('🤖 Bot:', chatbot.handleMessage(testPhone, 'REGISTER'));
console.log('\n' + '='.repeat(50) + '\n');

// Test 4: Enter name
console.log('📱 Message: John Doe');
console.log('🤖 Bot:', chatbot.handleMessage(testPhone, 'John Doe'));
console.log('\n' + '='.repeat(50) + '\n');

// Test 5: Enter phone
console.log('📱 Message: +1234567890');
console.log('🤖 Bot:', chatbot.handleMessage(testPhone, '+1234567890'));
console.log('\n' + '='.repeat(50) + '\n');

// Test 6: Enter email
console.log('📱 Message: john@example.com');
console.log('🤖 Bot:', chatbot.handleMessage(testPhone, 'john@example.com'));
console.log('\n' + '='.repeat(50) + '\n');

// Test 7: Add service
console.log('📱 Message: OFFER design logo 3');
console.log('🤖 Bot:', chatbot.handleMessage(testPhone, 'OFFER design logo 3'));
console.log('\n' + '='.repeat(50) + '\n');

// Test 8: Skip needs
console.log('📱 Message: SKIP');
console.log('🤖 Bot:', chatbot.handleMessage(testPhone, 'SKIP'));
console.log('\n' + '='.repeat(50) + '\n');

// Test 9: Show profile
console.log('📱 Message: PROFILE');
console.log('🤖 Bot:', chatbot.handleMessage(testPhone, 'PROFILE'));
console.log('\n' + '='.repeat(50) + '\n');

// Test 10: Show offers
console.log('📱 Message: MY_OFFERS');
console.log('🤖 Bot:', chatbot.handleMessage(testPhone, 'MY_OFFERS'));
console.log('\n' + '='.repeat(50) + '\n');

// Test 11: Search services
console.log('📱 Message: SEARCH design');
console.log('🤖 Bot:', chatbot.handleMessage(testPhone, 'SEARCH design'));
console.log('\n' + '='.repeat(50) + '\n');

// Test 12: Add another user and service
const testPhone2 = '+9876543210';
console.log('📱 Adding another user...');
chatbot.handleMessage(testPhone2, 'REGISTER');
chatbot.handleMessage(testPhone2, 'Jane Smith');
chatbot.handleMessage(testPhone2, '+9876543210');
chatbot.handleMessage(testPhone2, 'jane@example.com');
chatbot.handleMessage(testPhone2, 'OFFER web development 5');
chatbot.handleMessage(testPhone2, 'SKIP');

// Test 13: Search again (should find both users)
console.log('📱 Message: SEARCH design');
console.log('🤖 Bot:', chatbot.handleMessage(testPhone, 'SEARCH design'));
console.log('\n' + '='.repeat(50) + '\n');

console.log('✅ Chatbot testing complete!');
console.log('\n🎯 This chatbot can now be integrated into WhatsApp!');
