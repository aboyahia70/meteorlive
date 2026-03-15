# MeteorLive — Demo Video Script
# Target length: 3:30 – 4:00 minutes
# Format: screen recording + voiceover

---

## [0:00 – 0:20]  The problem

SCREEN: Blank dark screen, then MeteorLive loads at URL: https://meteorlive-50574840260.us-central1.run.app

VOICEOVER:
"Over 1.5 billion people are learning English right now.
Most of them practice alone — reading apps, flashcards, grammar drills.
But fluency isn't learned by reading. It's learned by speaking.
The problem is: real speaking practice requires a real human listener.
Until now."

---

## [0:20 – 0:40]  Introduce Meteo

SCREEN: Zoom in on the avatar sidebar — Meteo's portrait, name, "English Fluency Coach · AI"

VOICEOVER:
"MeteorLive introduces Meteo — a real-time AI English fluency coach
powered by Google Gemini's native audio model.
Meteo listens to you speak, corrects your pronunciation and grammar naturally,
and responds with voice — just like a real coach would."

---

## [0:40 – 0:55]  Configuration (show it's easy to run)

SCREEN: Click ⚙️ Configuration, enter API key, click Save & Apply

VOICEOVER:
"Setup takes seconds. Enter your Gemini API key,
choose your model and region — and you're ready."

---

## [0:55 – 1:30]  WOW MOMENT — Live conversation + barge-in

SCREEN: Click Connect. Wait for "Connected" status. Start speaking.

ACTION: Say something like — "I go to the store yesterday and buyed some—"

SCREEN: Meteo starts responding with a correction mid-sentence

ACTION: INTERRUPT Meteo — start speaking again before it finishes

SCREEN: Meteo stops immediately and listens again

VOICEOVER:
"Watch what happens here.
I make a grammar mistake — Meteo catches it and starts correcting me.
But I interrupt — and Meteo stops instantly.
No awkward pause. No waiting for it to finish.
This is Gemini Live API's barge-in capability —
natural, bidirectional conversation in real time."

---

## [1:30 – 1:55]  Transcription

SCREEN: Point to the conversation panel showing both user and Meteo transcription scrolling live

VOICEOVER:
"Every word — mine and Meteo's — is transcribed in real time.
Users can read along, review mistakes, and track their progress."

---

## [1:55 – 2:20]  Document upload

SCREEN: Click the 📎 upload button, select a PDF (e.g. a job interview prep document)

SCREEN: Meteo reads it and says something tailored — "I see you have an interview at..."

VOICEOVER:
"MeteorLive goes beyond generic practice.
Upload any PDF, Word document, or text file —
a job interview brief, a speech, a presentation —
and Meteo instantly tailors the entire session to your content."

---

## [2:20 – 2:40]  Camera feed

SCREEN: Enable camera. Point camera at a piece of text or a book page.

VOICEOVER:
"The camera feed goes to Gemini too.
Meteo can see what you're holding, read text you show it,
and adjust coaching based on what it sees —
true multimodal interaction."

---

## [2:40 – 3:00]  System status panel

SCREEN: Scroll down to show MIC INPUT and AI OUTPUT waveform bars, Connection status, Session timer

VOICEOVER:
"The system status panel shows everything live —
microphone input, AI audio output, connection health, and session time.
Built for transparency, so users always know what's happening."

---

## [3:00 – 3:20]  Cloud deployment

SCREEN: Switch browser tab to Google Cloud Console → Cloud Run → MeteorLive service
SCREEN: Show "Serving" status, request count, logs streaming

VOICEOVER:
"MeteorLive is deployed on Google Cloud Run —
containerised, auto-scaling, and production-ready.
The backend connects directly to Gemini Live API
using the Google GenAI SDK."

---

## [3:20 – 3:45]  Architecture summary + close

SCREEN: Show the README architecture diagram or the Devpost project page

VOICEOVER:
"The architecture is simple by design.
A FastAPI WebSocket server on Cloud Run.
A vanilla JS frontend — no frameworks, no build step.
AudioWorklets for zero-latency audio capture and playback.
And Gemini 2.5 Flash Native Audio at the core.

MeteorLive is open source and free to run.
If you speak English as a second language —
or coach someone who does —
this is the practice partner that's always available,
always patient, and always listening.

Thank you."

---

## RECORDING TIPS

- Record at 1920×1080, 30fps
- Use a quiet room — the mic audio will be in the recording
- Have the app already connected before you start recording
- Practice the barge-in moment 2–3 times before recording — it's the centrepiece
- Keep the Cloud Console tab open and ready to switch to
- Total target: under 4:00 — trim pauses in editing if needed
