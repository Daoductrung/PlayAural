function checkType(value, typeName) {
  if (typeName === "string") return typeof value === "string";
  if (typeName === "integer") return Number.isInteger(value);
  if (typeName === "boolean") return typeof value === "boolean";
  if (typeName === "number") return typeof value === "number";
  if (typeName === "object") return value !== null && typeof value === "object" && !Array.isArray(value);
  if (typeName === "array") return Array.isArray(value);
  if (typeName === "null") return value === null;
  return true;
}

function propertyMatchesSchema(value, schema) {
  if (!schema) {
    return true;
  }
  if (schema.anyOf) {
    return schema.anyOf.some((subSchema) => propertyMatchesSchema(value, subSchema));
  }
  if (schema.enum) {
    return schema.enum.includes(value);
  }
  if (Object.hasOwn(schema, "const")) {
    return value === schema.const;
  }
  if (schema.type) {
    return checkType(value, schema.type);
  }
  return true;
}

function refNameFromMapping(ref) {
  if (!ref || typeof ref !== "string") {
    return null;
  }
  const marker = "#/$defs/";
  if (!ref.startsWith(marker)) {
    return null;
  }
  return ref.slice(marker.length);
}

function createPacketValidator(schema) {
  const defsByDir = {
    client_to_server: schema?.client_to_server?.$defs || {},
    server_to_client: schema?.server_to_client?.$defs || {},
  };
  const mappingByDir = {
    client_to_server: schema?.client_to_server?.discriminator?.mapping || {},
    server_to_client: schema?.server_to_client?.discriminator?.mapping || {},
  };

  function validate(packet, direction) {
    if (!packet || typeof packet !== "object") {
      return { ok: false, error: "Packet must be an object" };
    }
    if (typeof packet.type !== "string") {
      return { ok: false, error: "Packet.type must be a string" };
    }

    const ref = mappingByDir[direction][packet.type];
    if (!ref) {
      return { ok: false, error: `Unknown ${direction} packet type: ${packet.type}` };
    }

    const defName = refNameFromMapping(ref);
    const def = defName ? defsByDir[direction][defName] : null;
    if (!def) {
      return { ok: false, error: `Missing schema for packet type: ${packet.type}` };
    }

    const properties = def.properties || {};
    const required = def.required || [];

    for (const field of required) {
      if (!Object.hasOwn(packet, field)) {
        return { ok: false, error: `Missing required field '${field}' for ${packet.type}` };
      }
    }

    if (def.additionalProperties === false) {
      for (const key of Object.keys(packet)) {
        if (!Object.hasOwn(properties, key)) {
          return { ok: false, error: `Unexpected field '${key}' for ${packet.type}` };
        }
      }
    }

    for (const [key, value] of Object.entries(packet)) {
      if (!Object.hasOwn(properties, key)) {
        continue;
      }
      if (!propertyMatchesSchema(value, properties[key])) {
        return { ok: false, error: `Invalid field '${key}' for ${packet.type}` };
      }
    }

    return { ok: true, error: "" };
  }

  return {
    validateOutgoing(packet) {
      return validate(packet, "client_to_server");
    },
    validateIncoming(packet) {
      return validate(packet, "server_to_client");
    },
  };
}

export async function loadPacketValidator() {
  const schemaCandidates = [
    "./packet_schema.json",
    "../desktop/packet_schema.json",
    "/clients/desktop/packet_schema.json",
  ];
  try {
    let schema = null;
    for (const candidate of schemaCandidates) {
      const response = await fetch(candidate, { cache: "no-store" });
      if (!response.ok) {
        continue;
      }
      schema = await response.json();
      break;
    }
    if (!schema) {
      throw new Error("No packet schema path resolved");
    }
    return createPacketValidator(schema);
  } catch {
    return {
      validateOutgoing() {
        return { ok: true, error: "" };
      },
      validateIncoming() {
        return { ok: true, error: "" };
      },
    };
  }
}

export function createNetworkClient({ validator, onStatus, onPacket, onError }) {
  let ws = null;

  function isConnected() {
    return Boolean(ws && ws.readyState === WebSocket.OPEN);
  }

  function send(packet) {
    if (!isConnected()) {
      onError("network-error-not-connected");
      return false;
    }
    const check = validator.validateOutgoing(packet);
    if (!check.ok) {
      onError("network-error-outgoing-blocked", { reason: check.error });
      return false;
    }
    ws.send(JSON.stringify(packet));
    return true;
  }

  function disconnect() {
    if (!ws) {
      return;
    }
    ws.close();
    ws = null;
  }

  function connect({ serverUrl, authPacket }) {
    disconnect();

    onStatus("connecting");
    let socket;
    try {
      socket = new WebSocket(serverUrl);
    } catch {
      ws = null;
      onStatus("error");
      onError("network-error-websocket");
      onStatus("disconnected");
      return false;
    }
    ws = socket;

    socket.addEventListener("open", () => {
      if (socket !== ws) {
        return;
      }
      onStatus("connected");
      if (!authPacket || typeof authPacket !== "object") {
        onError("network-error-auth-missing");
        return;
      }
      send(authPacket);
    });

    socket.addEventListener("message", (event) => {
      if (socket !== ws) {
        return;
      }
      try {
        const packet = JSON.parse(event.data);
        const check = validator.validateIncoming(packet);
        if (!check.ok) {
          onError("network-error-incoming-blocked", { reason: check.error });
          return;
        }
        onPacket(packet);
      } catch (error) {
        onError("network-error-invalid-server-message", { reason: String(error) });
      }
    });

    socket.addEventListener("close", () => {
      if (socket !== ws) {
        return;
      }
      ws = null;
      onStatus("disconnected");
    });

    socket.addEventListener("error", () => {
      if (socket !== ws) {
        return;
      }
      onStatus("error");
      onError("network-error-websocket");
    });
    return true;
  }

  return {
    connect,
    disconnect,
    send,
    isConnected,
  };
}
