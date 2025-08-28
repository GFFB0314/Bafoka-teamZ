// WhatsApp Server for Troc-Service Chatbot
// This server integrates your chatbot with WhatsApp

const express = require('express');
const bodyParser = require('body-parser');
const TrocServiceChatbot = require('./whatsapp-chatbot.js');

const app = express();
const PORT = process.env.PORT || 3000;

// Initialize your chatbot
const chatbot = new TrocServiceChatbot();

// Middleware
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// WhatsApp webhook verification
app.get('/webhook', (req, res) => {
    const mode = req.query['hub.mode'];
    const token = req.query['hub.verify_token'];
    const challenge = req.query['hub.challenge'];

    // Set your own verification token
    const VERIFY_TOKEN = process.env.VERIFY_TOKEN || 'troc-service-2024';

    if (mode && token === VERIFY_TOKEN) {
        console.log('✅ WhatsApp webhook verified!');
        res.status(200).send(challenge);
    } else {
        console.log('❌ Webhook verification failed');
        res.sendStatus(403);
    }
});

// WhatsApp webhook endpoint
app.post('/webhook', (req, res) => {
    const body = req.body;

    if (body.object === 'whatsapp_business_account') {
        try {
            const entry = body.entry[0];
            const changes = entry.changes[0];
            const value = changes.value;
            const messages = value.messages;

            if (messages && messages.length > 0) {
                const message = messages[0];
                const phoneNumber = message.from;
                const messageText = message.text.body;

                console.log(`📱 Message from ${phoneNumber}: ${messageText}`);

                // Process message through your chatbot
                const response = chatbot.handleMessage(phoneNumber, messageText);

                // Send response back to WhatsApp
                sendWhatsAppMessage(phoneNumber, response);
            }

            res.status(200).send('OK');
        } catch (error) {
            console.error('❌ Error processing webhook:', error);
            res.status(500).send('Error');
        }
    } else {
        res.sendStatus(404);
    }
});

// Function to send WhatsApp message
async function sendWhatsAppMessage(phoneNumber, message) {
    try {
        const accessToken = process.env.WHATSAPP_ACCESS_TOKEN;
        const phoneNumberId = process.env.WHATSAPP_PHONE_NUMBER_ID;

        if (!accessToken || !phoneNumberId) {
            console.log('⚠️ WhatsApp credentials not configured');
            return;
        }

        const response = await fetch(`https://graph.facebook.com/v17.0/${phoneNumberId}/messages`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${accessToken}`,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                messaging_product: 'whatsapp',
                to: phoneNumber,
                type: 'text',
                text: { body: message }
            })
        });

        if (response.ok) {
            console.log(`✅ Message sent to ${phoneNumber}`);
        } else {
            console.error(`❌ Failed to send message:`, await response.text());
        }
    } catch (error) {
        console.error('❌ Error sending WhatsApp message:', error);
    }
}

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({
        status: 'OK',
        chatbot: 'Troc-Service WhatsApp Bot',
        timestamp: new Date().toISOString()
    });
});

// Start server
app.listen(PORT, () => {
    console.log(`🚀 Troc-Service WhatsApp Bot Server running on port ${PORT}`);
    console.log(`📱 Webhook URL: https://your-domain.com/webhook`);
    console.log(`🔗 Health Check: http://localhost:${PORT}/health`);
});

module.exports = app;
