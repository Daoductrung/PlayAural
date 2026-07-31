import { createNetworkClient } from "../network.js";

const result = document.querySelector("#result");

function assert(condition, message) {
  if (!condition) {
    throw new Error(message);
  }
}

try {
  const statuses = [];
  const errors = [];
  const client = createNetworkClient({
    validator: {
      validateIncoming: () => ({ ok: true }),
      validateOutgoing: () => ({ ok: true }),
    },
    onStatus: (status) => statuses.push(status),
    onPacket: () => {},
    onError: (error) => errors.push(error),
  });

  const connected = client.connect({
    serverUrl: "ws://[invalid",
    authPacket: { type: "authorize" },
  });

  assert(connected === false, "A rejected WebSocket constructor must report failure.");
  assert(
    JSON.stringify(statuses) === JSON.stringify([
      "connecting",
      "error",
      "disconnected",
    ]),
    `Unexpected status sequence: ${statuses.join(", ")}`,
  );
  assert(
    JSON.stringify(errors) === JSON.stringify(["network-error-websocket"]),
    `Unexpected errors: ${errors.join(", ")}`,
  );
  assert(client.isConnected() === false, "Rejected connection must remain closed.");
  result.textContent = "PASS";
} catch (error) {
  result.textContent = `FAIL: ${error instanceof Error ? error.message : String(error)}`;
}
