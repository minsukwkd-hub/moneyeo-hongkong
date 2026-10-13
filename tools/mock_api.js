// Mock of the Anthropic Messages API streaming endpoint, to exercise the page's SSE parser + tool loop.
// Round 1: returns a tool_use (add_stop). Round 2 (when tool_result present): returns final text.
const http = require("http");
function sse(res, events) {
  res.writeHead(200, { "content-type": "text/event-stream", "access-control-allow-origin": "*", "cache-control": "no-store" });
  let i = 0;
  const t = setInterval(() => {
    if (i >= events.length) { clearInterval(t); res.end(); return; }
    const e = events[i++]; res.write(`event: ${e.type}\ndata: ${JSON.stringify(e)}\n\n`);
  }, 15);
}
http.createServer((req, res) => {
  if (req.method === "OPTIONS") { res.writeHead(204, { "access-control-allow-origin": "*", "access-control-allow-methods": "POST, OPTIONS", "access-control-allow-headers": "*" }); return res.end(); }
  let body = ""; req.on("data", c => body += c); req.on("end", () => {
    const j = JSON.parse(body);
    const auth = req.headers["authorization"];
    if (auth !== "Bearer testtoken") { res.writeHead(401, { "content-type": "application/json", "access-control-allow-origin": "*" }); return res.end(JSON.stringify({ error: { message: "bad token" } })); }
    const last = j.messages[j.messages.length - 1];
    const hasResult = Array.isArray(last.content) && last.content.some(b => b.type === "tool_result");
    const hasTools = Array.isArray(j.tools) && j.tools.some(t => t.name === "add_stop");
    console.log("req round:", hasResult ? 2 : 1, "model:", j.model, "tools:", (j.tools || []).length, "sys:", (j.system || "").length, "beta:", req.headers["anthropic-beta"] || "-", "fallbacks:", j.fallbacks || "-");
    if (!hasResult && hasTools) {
      sse(res, [
        { type: "message_start", message: { id: "msg_1", type: "message", role: "assistant", content: [] } },
        { type: "content_block_start", index: 0, content_block: { type: "thinking", thinking: "" } },
        { type: "content_block_delta", index: 0, delta: { type: "signature_delta", signature: "sig_abc" } },
        { type: "content_block_stop", index: 0 },
        { type: "content_block_start", index: 1, content_block: { type: "text", text: "" } },
        { type: "content_block_delta", index: 1, delta: { type: "text_delta", text: "Day 2에 넣어 볼게요. " } },
        { type: "content_block_stop", index: 1 },
        { type: "content_block_start", index: 2, content_block: { type: "tool_use", id: "toolu_1", name: "add_stop", input: {} } },
        { type: "content_block_delta", index: 2, delta: { type: "input_json_delta", partial_json: '{"day":2,"time":"15:00","name":"테스트 카페","query":"Test Cafe Sheung Wan","lat":22.286' } },
        { type: "content_block_delta", index: 2, delta: { type: "input_json_delta", partial_json: ',"lng":114.151,"why":"테스트용이에요."}' } },
        { type: "content_block_stop", index: 2 },
        { type: "message_delta", delta: { stop_reason: "tool_use" }, usage: { output_tokens: 10 } },
        { type: "message_stop" },
      ]);
    } else {
      const echo = hasResult ? last.content[0].content : "";
      sse(res, [
        { type: "message_start", message: { id: "msg_2", type: "message", role: "assistant", content: [] } },
        { type: "content_block_start", index: 0, content_block: { type: "text", text: "" } },
        { type: "content_block_delta", index: 0, delta: { type: "text_delta", text: "넣었어요. 결과: " + echo } },
        { type: "content_block_delta", index: 0, delta: { type: "text_delta", text: " 깡총!" } },
        { type: "content_block_stop", index: 0 },
        { type: "message_delta", delta: { stop_reason: "end_turn" }, usage: { output_tokens: 12 } },
        { type: "message_stop" },
      ]);
    }
  });
}).listen(8766, "127.0.0.1", () => console.log("mock api on 8766"));
