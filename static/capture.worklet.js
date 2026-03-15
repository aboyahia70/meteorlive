// Microphone capture — PCM16 @ 16kHz, emits 100ms chunks
class CaptureProcessor extends AudioWorkletProcessor {
    constructor() {
        super();
        this._buffer = [];
    }
    process(inputs) {
        const channel = inputs[0][0];
        if (!channel) return true;
        for (let i = 0; i < channel.length; i++) {
            this._buffer.push(channel[i]);
        }
        // 1600 samples = 100ms @ 16kHz
        while (this._buffer.length >= 1600) {
            const chunk = this._buffer.splice(0, 1600);
            const int16 = new Int16Array(1600);
            let sumSq = 0;
            for (let i = 0; i < 1600; i++) {
                const s = Math.max(-1, Math.min(1, chunk[i]));
                int16[i] = s < 0 ? s * 32768 : s * 32767;
                sumSq += s * s;
            }
            const rms = Math.sqrt(sumSq / 1600);
            this.port.postMessage({ int16: int16.buffer, rms }, [int16.buffer]);
        }
        return true;
    }
}
registerProcessor('capture-processor', CaptureProcessor);
