import os
import json
import logging
import base64
import asyncio
import time
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv(override=True)
API_KEY = os.getenv("GEMINI_API_KEY", "")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("MeteorLive.Production")

app = FastAPI(title="MeteorLive", version="3.2.0")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
static_path = os.path.join(BASE_DIR, "static")

SYSTEM_INSTRUCTION = """You are Meteo, an expert English Fluency Trainer.
Help users improve spoken English in real-time.
- Correct pronunciation and grammar naturally
- Keep responses concise and encouraging
- Adapt to the user's level
- English only."""

MODEL_ID = "models/gemini-2.5-flash-native-audio-latest"
SILENCE_100MS = bytes(3200)   # 100ms at 16kHz mono PCM16


async def run_session(client_id: str, user_ws: WebSocket, api_key: str = None, model_id: str = None):
    # Use caller-supplied key if provided, otherwise fall back to server env key
    effective_key = api_key or API_KEY
    if not effective_key:
        await user_ws.send_json({"type": "error", "content": "No API key configured. Set GEMINI_API_KEY on the server or enter one in the Configuration menu."})
        return
    effective_model = model_id or MODEL_ID

    client = genai.Client(
        api_key=effective_key,
        http_options={"api_version": "v1alpha"},
    )
    retry_delay = 1
    connected_at = time.time()
    session_handle = None

    while True:
        config = types.LiveConnectConfig(
            response_modalities=["AUDIO"],
            system_instruction=SYSTEM_INSTRUCTION,
            input_audio_transcription=types.AudioTranscriptionConfig(),
            output_audio_transcription=types.AudioTranscriptionConfig(),
            session_resumption=types.SessionResumptionConfig(handle=session_handle),
        )
        error_event = asyncio.Event()
        tasks = []
        try:
            logger.info(f"[{client_id}] Connecting to Gemini (resume={session_handle is not None})...")
            async with client.aio.live.connect(model=effective_model, config=config) as session:
                logger.info(f"[{client_id}] ✓ Connected")
                retry_delay = 1

                video_queue = asyncio.Queue()
                text_queue = asyncio.Queue()
                last_send_time = [time.time()]  # track last audio send time

                # ── GEMINI KEEPALIVE — silence كل ثانية لمنع timeout ──
                async def keepalive():
                    while not error_event.is_set():
                        await asyncio.sleep(1)
                        if error_event.is_set():
                            break
                        try:
                            if time.time() - last_send_time[0] >= 1:
                                await session.send_realtime_input(
                                    audio=types.Blob(data=SILENCE_100MS, mime_type="audio/pcm;rate=16000")
                                )
                                last_send_time[0] = time.time()
                        except asyncio.CancelledError:
                            break
                        except Exception as e:
                            logger.error(f"[{client_id}] keepalive error: {e}")
                            error_event.set()
                            break

                # ── CLIENT PING — إبقاء WebSocket المتصفح حياً ──
                async def ping_client():
                    while not error_event.is_set():
                        await asyncio.sleep(10)
                        try:
                            await user_ws.send_json({"type": "ping"})
                        except asyncio.CancelledError:
                            break
                        except Exception:
                            error_event.set()
                            break

                # ── SEND VIDEO ──
                async def send_video():
                    try:
                        while not error_event.is_set():
                            chunk = await video_queue.get()
                            await session.send_realtime_input(
                                video=types.Blob(data=chunk, mime_type="image/jpeg")
                            )
                    except asyncio.CancelledError:
                        pass
                    except Exception as e:
                        logger.error(f"[{client_id}] send_video error: {e}")

                # ── SEND TEXT ──
                async def send_text():
                    try:
                        while not error_event.is_set():
                            text = await text_queue.get()
                            await session.send_client_content(
                                turns=types.Content(role="user", parts=[types.Part(text=text)]),
                                turn_complete=True
                            )
                    except asyncio.CancelledError:
                        pass
                    except Exception as e:
                        logger.error(f"[{client_id}] send_text error: {e}")
                        error_event.set()

                # ── RECEIVE FROM GEMINI ──
                async def receive_from_gemini():
                    nonlocal session_handle
                    try:
                        while not error_event.is_set():
                            async for response in session.receive():
                                if error_event.is_set():
                                    return
                                # LOG EVERYTHING to see raw response structure
                                logger.info(f"[GEMINI RAW] {response}")
                                sc = response.server_content
                                if sc:
                                    logger.info(f"[SC KEYS] model_turn={bool(sc.model_turn)} output_transcription={bool(sc.output_transcription)} input_transcription={bool(sc.input_transcription)} turn_complete={bool(sc.turn_complete)}")
                                if sc and sc.model_turn:
                                    for part in sc.model_turn.parts:
                                        if part.inline_data and part.inline_data.data:
                                            await user_ws.send_bytes(part.inline_data.data)
                                        if part.text:
                                            logger.info(f"[PART TEXT] {part.text}")
                                            await user_ws.send_json({
                                                "type": "output_transcription",
                                                "text": part.text,
                                                "finished": True
                                            })
                                # Output transcription (Meteo's speech → text)
                                if sc and sc.output_transcription:
                                    logger.info(f"[OUT TRANSCRIPT] {sc.output_transcription}")
                                    await user_ws.send_json({
                                        "type": "output_transcription",
                                        "text": sc.output_transcription.text or "",
                                        "finished": sc.output_transcription.finished or False
                                    })
                                # Input transcription (user's speech → text)
                                if sc and sc.input_transcription:
                                    logger.info(f"[IN TRANSCRIPT] {sc.input_transcription}")
                                    await user_ws.send_json({
                                        "type": "input_transcription",
                                        "text": sc.input_transcription.text or "",
                                        "finished": sc.input_transcription.finished or False
                                    })
                                # Also check response-level text
                                if response.text:
                                    logger.info(f"[RESPONSE TEXT] {response.text}")
                                    await user_ws.send_json({
                                        "type": "output_transcription",
                                        "text": response.text,
                                        "finished": True
                                    })
                                # Notify frontend when Meteo finishes speaking
                                if sc and sc.turn_complete:
                                    await user_ws.send_json({"type": "turn_complete"})
                                # Save session handle for resumption
                                if response.session_resumption_update:
                                    upd = response.session_resumption_update
                                    if upd.resumable and upd.new_handle:
                                        session_handle = upd.new_handle
                                        logger.info(f"[{client_id}] Session handle saved")
                                # go_away = session ending — reconnect with saved handle
                                if response.go_away:
                                    logger.info(f"[{client_id}] goAway — reconnecting with handle")
                                    error_event.set()
                    except asyncio.CancelledError:
                        pass
                    except Exception as e:
                        logger.error(f"[{client_id}] Gemini stream error: {e}")
                        error_event.set()

                tasks = [
                    asyncio.create_task(keepalive()),
                    asyncio.create_task(ping_client()),
                    asyncio.create_task(send_video()),
                    asyncio.create_task(send_text()),
                    asyncio.create_task(receive_from_gemini()),
                ]

                # ── RECEIVE FROM CLIENT ──
                client_gone = False
                try:
                    while not error_event.is_set():
                        try:
                            msg = await asyncio.wait_for(user_ws.receive(), timeout=15.0)
                        except asyncio.TimeoutError:
                            continue

                        # Detect clean browser disconnect
                        if msg.get("type") == "websocket.disconnect":
                            logger.info(f"[{client_id}] Browser disconnected cleanly after {round(time.time()-connected_at,1)}s")
                            client_gone = True
                            error_event.set()
                            break

                        # Binary = raw PCM audio
                        if "bytes" in msg and msg["bytes"]:
                            audio_data = msg["bytes"]
                            await session.send_realtime_input(
                                audio=types.Blob(data=audio_data, mime_type="audio/pcm;rate=16000")
                            )
                            last_send_time[0] = time.time()
                            continue

                        # Text = JSON commands
                        if "text" in msg and msg["text"]:
                            try:
                                data = json.loads(msg["text"])
                            except Exception:
                                continue

                            t = data.get("type")
                            if t == "pong":
                                pass
                            elif t == "barge_in":
                                await session.send_realtime_input(
                                    audio=types.Blob(data=SILENCE_100MS, mime_type="audio/pcm;rate=16000")
                                )
                                last_send_time[0] = time.time()
                            elif t == "text":
                                txt = data.get("content", "").strip()
                                if txt:
                                    await text_queue.put(txt)
                            elif t == "audio":
                                try:
                                    audio_bytes = base64.b64decode(data["content"])
                                    await session.send_realtime_input(
                                        audio=types.Blob(data=audio_bytes, mime_type="audio/pcm;rate=16000")
                                    )
                                    last_send_time[0] = time.time()
                                except Exception:
                                    pass
                            elif t == "video_frame":
                                try:
                                    await video_queue.put(base64.b64decode(data["content"]))
                                except Exception:
                                    pass

                except WebSocketDisconnect:
                    logger.info(f"[{client_id}] Client disconnected after {round(time.time()-connected_at,1)}s")
                    client_gone = True
                except Exception as e:
                    logger.error(f"[{client_id}] Client error: {e}")
                    client_gone = True
                finally:
                    error_event.set()
                    for t in tasks:
                        t.cancel()
                    await asyncio.gather(*tasks, return_exceptions=True)

                if client_gone:
                    return

                logger.info(f"[{client_id}] Gemini disconnected — retrying in {retry_delay}s")

        except Exception as e:
            logger.error(f"[{client_id}] Connection error: {e}")
            error_event.set()
            for t in tasks:
                t.cancel()

        try:
            await user_ws.send_json({"type": "ping"})
        except Exception:
            return

        await asyncio.sleep(retry_delay)
        retry_delay = min(retry_delay * 2, 30)


@app.get("/")
async def get_index():
    f = os.path.join(static_path, "index.html")
    return FileResponse(f) if os.path.exists(f) else JSONResponse({"error": "not found"}, status_code=404)

@app.get("/capture.worklet.js")
async def get_capture_worklet():
    f = os.path.join(static_path, "capture.worklet.js")
    return FileResponse(f, media_type="application/javascript") if os.path.exists(f) else JSONResponse({"error": "not found"}, status_code=404)

@app.get("/playback.worklet.js")
async def get_playback_worklet():
    f = os.path.join(static_path, "playback.worklet.js")
    return FileResponse(f, media_type="application/javascript") if os.path.exists(f) else JSONResponse({"error": "not found"}, status_code=404)

@app.get("/favicon.ico")
async def favicon():
    from fastapi.responses import Response
    return Response(status_code=204)

@app.get("/health")
async def health():
    return {"status": "ok", "model": MODEL_ID}

app.mount("/static", StaticFiles(directory=static_path), name="static")

@app.websocket("/ws/live/{client_id}")
async def ws_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    # Read optional config from query params (sent by frontend config menu)
    api_key_param  = websocket.query_params.get("api_key")  or None
    model_param    = websocket.query_params.get("model")     or None
    logger.info(f"[{client_id}] WebSocket opened | custom_key={'yes' if api_key_param else 'no'} | model={model_param or MODEL_ID}")
    try:
        await run_session(client_id, websocket, api_key=api_key_param, model_id=model_param)
    finally:
        logger.info(f"[{client_id}] WebSocket closed")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 9090))
    logger.info(f"Starting MeteorLive v3.2.0 on port {port}")
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        ws_ping_interval=20,   # أرسل WebSocket ping كل 20 ثانية
        ws_ping_timeout=60,    # انتظر pong 60 ثانية قبل القطع
        timeout_keep_alive=120
    )
