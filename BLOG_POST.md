# How I built a real-time AI English coach with Gemini Live API

*#GeminiLiveAgentChallenge*

---

I have been learning English for years. Grammar apps, vocabulary drills, language exchange partners — I have tried them all. But the one thing none of them gave me was a patient listener who could catch my mistakes *as I spoke* and correct them in the flow of conversation.

That gap is what MeteorLive is built to close.

---

## The idea: a coach that actually listens

Most AI language tools work on text. You type, the model replies. Even the voice-enabled ones are pipelines: speech-to-text → LLM → text-to-speech. Each step adds latency and loses something — the rhythm of the sentence, the inflection, the natural back-and-forth of real conversation.

Gemini's native audio model is different. It processes audio directly — no intermediate transcription, no synthetic voice bolted on afterward. The result sounds and feels like talking to a person. That is what made building a real-time fluency coach actually possible.

---

## The architecture: keep it simple

I deliberately kept the stack minimal:

- **Backend**: a single `main.py` using FastAPI and a WebSocket endpoint. The entire Gemini Live session management, barge-in handling, and audio relay fits in one file.
- **Frontend**: a single `index.html`. Vanilla JavaScript — no React, no Webpack, no build step. A judge can clone the repo and be speaking to Meteo in under two minutes.
- **Audio**: two AudioWorklets — `capture.worklet.js` encodes microphone input to PCM16 at 16 kHz, and `playback.worklet.js` decodes Gemini's 24 kHz output for the speaker. Running on a dedicated audio thread means zero glitches even when the UI is busy.

The whole thing is deployed on Google Cloud Run as a containerised FastAPI app.

---

## The hardest part: barge-in

Natural conversation has interruptions. If you ask someone a question and they start answering, you might cut them off mid-sentence to clarify. That is how humans talk. Most AI voice interfaces do not support this — they make you wait for the AI to finish before they listen again.

Gemini Live API supports barge-in natively, but getting it to feel natural took work. The key insight was timing: the frontend needs to send the interrupt signal *before* the next audio chunk arrives, not after. If you wait even one chunk too long, Meteo finishes its sentence before stopping. The solution was to send the barge-in message immediately when the microphone detects voice activity, even before encoding the audio chunk — so the signal races ahead of the audio data.

When it works correctly, interrupting Meteo feels exactly like interrupting a person. It stops mid-word, no awkward pause, and listens immediately. That single interaction is what makes the coaching feel real rather than robotic.

---

## A feature I did not plan: document upload

Halfway through building, I realised that generic English practice is useful, but *targeted* practice is transformative. What if someone has a job interview tomorrow? Or a conference presentation? Or needs to practise vocabulary for a specific industry?

I added document upload — PDF, DOCX, or TXT — using PDF.js and Mammoth.js to extract text client-side. When you upload a document, Meteo reads it and the entire coaching session is anchored to that content. Upload your interview brief and Meteo will quiz you on it, correct your answers, and help you sound confident talking about your own experience.

This turned MeteorLive from a practice tool into a preparation tool — a meaningfully different use case.

---

## What surprised me about Gemini's native audio

I expected the model to sound like a good text-to-speech engine. It does not. It sounds like a person having a conversation.

The prosody adapts to context. When Meteo is correcting a mistake, the tone is gentle and encouraging. When it is asking a follow-up question, the intonation rises naturally. When it is affirming something the user said, there is a warmth in the response that no TTS pipeline produces.

I do not know exactly how Gemini achieves this — whether it is learned from conversational data or something in the audio modeling architecture. What I know is that users respond to it differently than they respond to synthetic speech. They relax. They speak more naturally. And that is the whole point of fluency practice.

---

## What is next

MeteorLive is open source. If you are learning English — or building tools for people who are — I would love for you to try it, fork it, and build on it.

The roadmap includes progress tracking across sessions, scenario modes (job interview, business presentation, casual conversation), and eventually a mobile app for practice on the go.

But the core is already working. Speak, get corrected, improve.

---

*MeteorLive was built for the Google Gemini Live Agent Challenge. The source code is on GitHub at [github.com/YOUR_USERNAME/meteorlive](https://github.com/YOUR_USERNAME/meteorlive).*

*Try it. Talk to Meteo. See what happens when you interrupt it mid-sentence.*
