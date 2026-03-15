# MeteorLive — Devpost Submission Text

---

## Tagline (one line, shown in project card)

Real-time AI English fluency coach powered by Gemini Live API — speak, get corrected, improve.

---

## Inspiration

Over 1.5 billion people are learning English worldwide. Most practice alone with reading apps, grammar drills, and flashcard tools. But fluency is not learned by reading — it is learned by speaking. The problem is that real speaking practice requires a real human listener who is patient, available, and skilled enough to catch pronunciation and grammar errors naturally.

Private English tutors cost $30–80 per hour and are not available at 2 AM when you are preparing for a job interview the next morning. Language exchange apps depend on finding a willing partner. Grammar checkers only work on text.

MeteorLive solves this by giving every learner a personal AI fluency coach — Meteo — who listens in real time, responds with voice, and corrects naturally mid-conversation, available 24/7 with no scheduling and no cost per session.

---

## What it does

MeteorLive is a real-time English fluency trainer that runs in the browser. Users speak naturally and Meteo — an AI coach persona powered by Gemini's native audio model — listens, responds with voice, and corrects pronunciation and grammar the way a real coach would: gently, naturally, and in context.

Key interactions:
- **Speak and be corrected** — Meteo listens to continuous audio and responds with voice coaching
- **Barge-in** — interrupt Meteo mid-sentence at any moment, just like a real conversation
- **Live transcription** — every word from both sides appears as text in real time
- **Document upload** — upload a PDF, DOCX, or TXT file and Meteo tailors the session to that content (job interview prep, presentation practice, vocabulary sets)
- **Camera feed** — Meteo can see what the user shows the camera, enabling visual context
- **Session recording** — record the full session (mic + camera + Meteo audio) as a .webm file
- **Bring your own key** — any user can enter their own Gemini API key in the Configuration panel without touching the server

---

## How we built it

**Backend**: Python FastAPI with a single WebSocket endpoint (`/ws/live/{client_id}`). The server manages the Gemini Live session, handles barge-in signals, sends keepalive silence to maintain the connection, and relays audio/video/text between the browser and Gemini. Deployed on Google Cloud Run.

**Frontend**: A single `index.html` file — vanilla JavaScript, no frameworks, no build step. Two AudioWorklets handle audio: `capture.worklet.js` converts microphone input to PCM16 at 16 kHz for Gemini, and `playback.worklet.js` decodes Gemini's PCM16 output at 24 kHz for the speaker.

**AI**: Google Gemini 2.5 Flash Native Audio (`gemini-2.5-flash-native-audio-latest`) via the Google GenAI SDK (`google-genai`). The model processes audio natively — no speech-to-text middleware, no text-to-speech pipeline — resulting in lower latency and more natural prosody than chained models.

**Document processing**: PDF.js and Mammoth.js extract text from uploaded files client-side, which is then sent to Gemini as a text message to anchor the coaching session.

---

## Challenges we ran into

- **AudioWorklet timing**: Getting zero-dropout audio capture required careful buffer management in the worklet thread, separate from the main JS thread, to avoid glitches during UI repaints.
- **Barge-in reliability**: Gemini Live API's barge-in works at the session level — we had to ensure the frontend sends the interrupt signal before the next audio chunk arrives, otherwise Meteo would finish its sentence before stopping.
- **Session keepalive**: Long pauses in conversation would cause the WebSocket to drop. We solved this by sending 100ms of silence every 5 seconds when no real audio is flowing, keeping the Gemini session alive.
- **Dropdown overflow clipping**: The Configuration panel is inside a sidebar with `overflow: hidden` parents. We solved this using a DOM portal pattern — the dropdown menu is rendered at the `<body>` level with `position: fixed`, positioned dynamically via `getBoundingClientRect()`.

---

## Accomplishments that we're proud of

- True barge-in interruption — the single most important feature for making the conversation feel natural, and one of the hardest to get right
- Zero build step — a judge can clone the repo and run `python backend/main.py` and be speaking to Meteo in under two minutes
- Per-user API key support — the app works without any server-side secrets, making it trivially easy to share and demo
- Document-aware coaching — uploading a job description and practising for that specific interview is a genuinely useful use case that no other tool does in real time with voice

---

## What we learned

- Gemini's native audio model produces dramatically more natural responses than text-to-speech pipelines — the prosody adapts to context in a way that feels conversational rather than robotic
- AudioWorklets are essential for real-time audio — the legacy ScriptProcessorNode approach introduces noticeable glitches that break the coaching experience
- Keeping the architecture simple (one Python file, one HTML file) made debugging much faster and will make it easier for others to fork and adapt

---

## What's next for MeteorLive

- **Progress tracking** — session history, pronunciation scores over time, vocabulary acquisition metrics
- **Scenario modes** — job interview, business presentation, casual conversation, academic English
- **Voice selection** — let users choose Meteo's voice and speaking pace
- **Mobile app** — React Native wrapper for on-the-go practice
- **Classroom mode** — teacher dashboard showing student session metrics

---

## Built with

Python · FastAPI · WebSocket · Google Gemini Live API · Google GenAI SDK · Web AudioWorklet · Google Cloud Run · JavaScript · PDF.js · Mammoth.js
