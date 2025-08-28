// Twilio WhatsApp Server for Troc-Service Chatbot
// This server integrates your chatbot with Twilio WhatsApp

const express = require('express');
const bodyParser = require('body-parser');
const TrocServiceChatbot = require('./whatsapp-chatbot.js');

const app = express();
const PORT = process.env.PORT || 3000;

// Initialize your chatbot
const chatbot = new TrocServiceChatbot();

// Middleware
app.use(bodyParser.urlencoded({ extended: false }));
app.use(bodyParser.json());

// Twilio webhook endpoint for WhatsApp
app.post('/webhook', (req, res) => {
    try {
        const phoneNumber = req.body.From;
        const messageText = req.body.Body;
        const messageSid = req.body.MessageSid;

        console.log(`📱 WhatsApp message from ${phoneNumber}: ${messageText}`);

        // Process message through your chatbot
        const response = chatbot.handleMessage(phoneNumber, messageText);

        // Send response back through Twilio
        sendTwilioWhatsAppMessage(phoneNumber, response);

        // Send TwiML response
        res.writeHead(200, { 'Content-Type': 'text/xml' });
        res.end(`<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>${response}</Message>
</Response>`);

    } catch (error) {
        console.error('❌ Error processing webhook:', error);
        res.status(500).send('Error');
    }
});

// Function to send WhatsApp message via Twilio
async function sendTwilioWhatsAppMessage(to, message) {
    try {
        const accountSid = process.env.TWILIO_ACCOUNT_SID || 'your_twilio_account_sid_here';
        const authToken = process.env.TWILIO_AUTH_TOKEN || 'your_twilio_auth_token_here';
        const fromNumber = process.env.TWILIO_WHATSAPP_NUMBER || 'whatsapp:+14155238886'; // Twilio sandbox number

        // For production, you'll need to get your own WhatsApp number from Twilio
        const url = `https://api.twilio.com/2010-04-01/Accounts/${accountSid}/Messages.json`;

        // Use node-fetch or built-in https module for older Node.js versions
        const https = require('https');
        const querystring = require('querystring');

        const postData = querystring.stringify({
            From: fromNumber,
            To: `whatsapp:${to}`,
            Body: message
        });

        const options = {
            hostname: 'api.twilio.com',
            port: 443,
            path: `/2010-04-01/Accounts/${accountSid}/Messages.json`,
            method: 'POST',
            headers: {
                'Authorization': 'Basic ' + Buffer.from(`${accountSid}:${authToken}`).toString('base64'),
                'Content-Type': 'application/x-www-form-urlencoded',
                'Content-Length': Buffer.byteLength(postData)
            }
        };

        const req = https.request(options, (res) => {
            let data = '';
            res.on('data', (chunk) => {
                data += chunk;
            });
            res.on('end', () => {
                if (res.statusCode === 200 || res.statusCode === 201) {
                    console.log(`✅ Message sent via Twilio to ${to}`);
                } else {
                    console.error(`❌ Failed to send message via Twilio:`, data);
                }
            });
        });

        req.on('error', (error) => {
            console.error('❌ Error sending Twilio WhatsApp message:', error);
        });

        req.write(postData);
        req.end();

    } catch (error) {
        console.error('❌ Error sending Twilio WhatsApp message:', error);
    }
}

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'OK',
        chatbot: 'Troc-Service WhatsApp Bot (via Twilio)',
        timestamp: new Date().toISOString(),
        provider: 'Twilio'
    });
});

// Test endpoint to simulate WhatsApp messages
app.get('/test', (req, res) => {
    res.send(`
        <h1>🧪 Test Troc-Service WhatsApp Bot</h1>
        <p>Your chatbot is running with Twilio integration!</p>
        <p>Bot Name: <strong>Troc-Service</strong></p>
        <p>Provider: Twilio</p>
        <p>Status: ✅ Active</p>
        <br>
        <p>To test with real WhatsApp:</p>
        <ol>
            <li>Send a message to your Twilio WhatsApp number</li>
            <li>Try commands: HELP, REGISTER, OFFER design logo 3</li>
            <li>Your bot will respond with "Troc-Service" branding</li>
        </ol>
    `);
});

// Start server
app.listen(PORT, () => {
    console.log(`🚀 Troc-Service WhatsApp Bot Server (Twilio) running on port ${PORT}`);
    console.log(`📱 Webhook URL: https://your-domain.com/webhook`);
    console.log(`🔗 Health Check: http://localhost:${PORT}/health`);
    console.log(`🧪 Test Page: http://localhost:${PORT}/test`);
    console.log(`🤖 Bot Name: Troc-Service`);
    console.log(`📞 Provider: Twilio`);
});

module.exports = app;
