// @ts-check

const { spawn } = require("node:child_process");
const { send } = require("node:process");
const express = require('express');
const bodyParser = require('body-parser');
const path = require('path');

const app = express();
app.use(bodyParser.json());

const agentPath = path.join(__dirname, 'node_modules/copilot-node-server/copilot/dist/agent.js');
const server = spawn("node", [agentPath]);
// use `fork` in `node:child_process` is also OK
// const server = fork("agent.js", { silent: true });
// `{ silent: true }` is to make sure that data sent to stdio will be returned normally

/**
 * Send a LSP message to the server.
 */
const sendMessage = (/** @type {object} */ data) => {
  const dataString = JSON.stringify({ ...data, jsonrpc: "2.0" });
  const contentLength = Buffer.byteLength(dataString, "utf8");
  const rpcString = `Content-Length: ${contentLength}\r\n\r\n${dataString}`;
  server.stdin.write(rpcString);
};

let requestId = 0;
/** @type {Map<number, (payload: object) => void | Promise<void>>} */
const resolveMap = new Map();
/** @type {Map<number, (payload: object) => void | Promise<void>>} */
const rejectMap = new Map();

/**
 * Send a LSP request to the server.
 */
const sendRequest = (/** @type {string} */ method, /** @type {object} */ params) => {
  sendMessage({ id: ++requestId, method, params });
  return new Promise((resolve, reject) => {
    resolveMap.set(requestId, resolve);
    rejectMap.set(requestId, reject);
  });
};
/**
 * Send a LSP notification to the server.
 */
const sendNotification = (/** @type {string} */ method, /** @type {object} */ params) => {
  sendMessage({ method, params });
};

/**
 * Handle received LSP payload.
 */
const handleReceivedPayload = (/** @type {object} */ payload) => {
  if ("id" in payload) {
    if ("result" in payload) {
      const resolve = resolveMap.get(payload.id);
      if (resolve) {
        resolve(payload.result);
        resolveMap.delete(payload.id);
      }
    } else if ("error" in payload) {
      const reject = rejectMap.get(payload.id);
      if (reject) {
        reject(payload.error);
        rejectMap.delete(payload.id);
      }
    }
  }
};

server.stdout.on("data", (data) => {
  /** @type {string} */
  const rawString = data.toString("utf-8");
  const payloadStrings = rawString.split(/Content-Length: \d+\r\n\r\n/).filter((s) => s);

  for (const payloadString of payloadStrings) {
    /** @type {Record<string, unknown>} */
    let payload;
    try {
      payload = JSON.parse(payloadString);
    } catch (e) {
      console.error(`Unable to parse payload: ${payloadString}`, e);
      continue;
    }

    handleReceivedPayload(payload);
  }
});

const wait = (/** @type {number} */ ms) => new Promise((resolve) => setTimeout(resolve, ms));

/* Main */
const main = async () => {
  // Wait for server to start
  await wait(1000);

  // Send `initialize` request
  await sendRequest("initialize", {
    capabilities: { workspace: { workspaceFolders: true } },
  });
  // Send `initialized` notification
  sendNotification("initialized", {});
};


// Endpoint for sending requests to the Node.js server
app.post('/sendRequest', async (req, res) => {
  const { method, params } = req.body;
  try {
      const result = await sendRequest(method, params);
      res.json(result);
  } catch (error) {
      res.status(500).send(error.toString());
  }
});

// Endpoint for sending notifications to the Node.js server
app.post('/sendNotification', (req, res) => {
  const { method, params } = req.body;
  sendNotification(method, params);
  res.status(200).send('Notification sent');
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => console.log(`Node server listening on port ${PORT}`));

void main().catch((error) => {
  console.error("Unhandled error in main:", error);
});