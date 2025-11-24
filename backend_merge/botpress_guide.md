# Botpress & Flask Integration Guide

This guide is the **single source of truth** for connecting Botpress to your Flask backend.

## 1. Prerequisites
- **Ngrok URL**: Ensure `ngrok` is running (`ngrok http 5000`). Copy the HTTPS URL (e.g., `https://a1b2.ngrok-free.app`).
- **Botpress Variables**: In Botpress Studio, go to **Variables** (bottom left) and create a configuration variable named `apiBaseUrl` with your Ngrok URL as the value.

## 2. API Endpoints Configuration
Use the **Execute Code** or **Call API** card in Botpress for each action.
**Headers**: `Content-Type: application/json`

### A. Registration (`/api/register`)
**Method**: `POST`
**URL**: `{{config.apiBaseUrl}}/api/register`
**Body**:
```json
{
  "phone": "{{event.payload.from}}",
  "name": "{{workflow.name}}",
  "community": "{{workflow.community}}",
  "skill": "{{workflow.skill}}"
}
```

### B. Check Balance (`/api/balance`)
**Method**: `GET`
**URL**: `{{config.apiBaseUrl}}/api/balance?phone={{event.payload.from}}`
**Body**: (Empty)
**Response Access**: `{{data.response.body.local_balance}}` and `{{data.response.body.external_balance}}`

### C. Transfer Money (`/api/transfer`)
**Method**: `POST`
**URL**: `{{config.apiBaseUrl}}/api/transfer`
**Body**:
```json
{
  "from_phone": "{{event.payload.from}}",
  "to_phone": "{{workflow.to_phone}}",
  "amount": {{workflow.amount}}
}
```
**Response Access**: `{{data.response.body.tx_id}}`

### D. Create Offer (`/api/offers`)
**Method**: `POST`
**URL**: `{{config.apiBaseUrl}}/api/offers`
**Body**:
```json
{
  "phone": "{{event.payload.from}}",
  "title": "{{workflow.offer_title}}",
  "description": "{{workflow.offer_desc}}",
  "price": {{workflow.offer_price}}
}
```

### E. Search Offers (`/api/offers`)
**Method**: `GET`
**URL**: `{{config.apiBaseUrl}}/api/offers?q={{workflow.search_query}}`
**Body**: (Empty)

### F. Voice Processing (`/api/voice/process`)
**Trigger**: User sends Audio
**Method**: `POST`
**URL**: `{{config.apiBaseUrl}}/api/voice/process`
**Body**:
```json
{
  "audio_url": "{{event.payload.audioUrl}}",
  "phone": "{{event.payload.from}}"
}
```
**Response Access**: Play audio from `{{data.response.body.audio_url}}`.

## 3. Bafoka API & Real Data
- The backend is connected to the **Real Bafoka Sandbox API**.
- **Registration** creates a real wallet on the sandbox network.
- **Transfers** move real sandbox tokens.
- **Balance** reflects the actual ledger state.
- **Note**: Use valid phone numbers (e.g., `+237...`) for all interactions.

## 4. Troubleshooting
- **Voice Fails**: Ensure `ffmpeg` is installed on the server machine.
- **API Errors**: Check the Flask terminal for logs.
- **Connection Refused**: Ensure Ngrok is running and the URL in Botpress is updated.
