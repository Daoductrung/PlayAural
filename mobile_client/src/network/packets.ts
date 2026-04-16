export type SpeechBuffer = "all" | "chat" | "game" | "system" | "misc";

export type MenuItemData = {
  id?: string;
  text: string;
};

export type MenuPacket = {
  type: "menu";
  menu_id?: string;
  items: Array<string | MenuItemData>;
  position?: number;
  selection_id?: string;
  multiletter_enabled?: boolean;
  escape_behavior?: string;
  grid_enabled?: boolean;
  grid_width?: number;
};

export type SpeakPacket = {
  type: "speak";
  text?: string;
  key?: string;
  params?: Record<string, unknown>;
  buffer?: SpeechBuffer;
  muted?: boolean;
};

export type ChatPacket = {
  type: "chat";
  convo?: "local" | "global" | "announcement" | "table" | "game" | "private" | "pm";
  sender?: string;
  message?: string;
  silent?: boolean;
};

export type RequestInputPacket = {
  type: "request_input";
  input_id: string;
  prompt: string;
  default_value?: string;
  multiline?: boolean;
  read_only?: boolean;
  max_length?: number;
};

export type AuthorizeSuccessPacket = {
  type: "authorize_success";
  username: string;
  version: string;
  locale?: string;
  voice?: {
    enabled?: boolean;
    provider?: string;
    token_ttl_seconds?: number;
    url?: string;
  };
  preferences?: Record<string, unknown>;
  update_info?: {
    version?: string;
    url?: string;
    hash?: string;
  };
  sounds_info?: {
    version?: string;
    url?: string;
  };
};

export type RegisterResponsePacket = {
  type: "register_response";
  status: "success" | "error";
  error?: string;
  text?: string;
  locale?: string;
};

export type RequestPasswordResetResponsePacket = {
  type: "request_password_reset_response";
  status: "success" | "error";
  error?: string;
  text?: string;
};

export type SubmitResetCodeResponsePacket = {
  type: "submit_reset_code_response";
  status: "success" | "error";
  error?: string;
  text?: string;
  username?: string;
};

export type DisconnectPacket = {
  type: "disconnect";
  reason?: string;
  reconnect?: boolean;
};

export type ForceExitPacket = {
  type: "force_exit";
  reason?: string;
};

export type PlaySoundPacket = {
  type: "play_sound";
  name?: string;
  volume?: number;
  pan?: number;
  pitch?: number;
};

export type PlayMusicPacket = {
  type: "play_music";
  name?: string;
  looping?: boolean;
};

export type PlayAmbiencePacket = {
  type: "play_ambience";
  intro?: string;
  loop?: string;
  outro?: string;
};

export type StopPacket = {
  type: "stop_music" | "stop_ambience";
};

export type ClearUiPacket = {
  type: "clear_ui";
};

export type LoginFailedPacket = {
  type: "login_failed";
  reason?: string;
  text?: string;
  reconnect?: boolean;
};

export type UpdateLocalePacket = {
  type: "update_locale";
  locale?: string;
};

export type PongPacket = {
  type: "pong";
};

export type UpdatePreferencePacket = {
  type: "update_preference";
  key?: string;
  value?: unknown;
  preferences?: Record<string, unknown>;
};

export type TableContextPacket = {
  type: "table_context";
  table_id?: string;
};

export type VoiceJoinInfoPacket = {
  type: "voice_join_info";
  context_id?: string;
  expires_at?: number;
  ice_servers?: unknown[];
  participant?: {
    identity?: string;
    name?: string;
  };
  provider?: string;
  room?: string;
  room_label?: string;
  scope?: string;
  token: string;
  url: string;
};

export type VoiceJoinErrorPacket = {
  type: "voice_join_error";
  context_id?: string;
  key?: string;
  params?: Record<string, unknown>;
  scope?: string;
  text?: string;
};

export type VoiceLeaveAckPacket = {
  type: "voice_leave_ack";
};

export type VoiceContextClosedPacket = {
  type: "voice_context_closed";
  context_id?: string;
  scope?: string;
};

export type ServerPacket =
  | AuthorizeSuccessPacket
  | ChatPacket
  | ClearUiPacket
  | DisconnectPacket
  | ForceExitPacket
  | LoginFailedPacket
  | MenuPacket
  | PlayAmbiencePacket
  | PlayMusicPacket
  | PlaySoundPacket
  | PongPacket
  | RegisterResponsePacket
  | RequestPasswordResetResponsePacket
  | RequestInputPacket
  | SpeakPacket
  | StopPacket
  | SubmitResetCodeResponsePacket
  | TableContextPacket
  | UpdateLocalePacket
  | UpdatePreferencePacket
  | VoiceContextClosedPacket
  | VoiceJoinErrorPacket
  | VoiceJoinInfoPacket
  | VoiceLeaveAckPacket
  | { type: string; [key: string]: unknown };

export type AuthorizePacket = {
  type: "authorize";
  username: string;
  password: string;
  version: string;
  client: "mobile";
};

export type RegisterPacket = {
  type: "register";
  username: string;
  password: string;
  locale: string;
  email: string;
  bio?: string;
  client: "mobile";
};

export type RequestPasswordResetPacket = {
  type: "request_password_reset";
  email: string;
  locale: string;
  client: "mobile";
};

export type SubmitResetCodePacket = {
  type: "submit_reset_code";
  email: string;
  code: string;
  new_password: string;
  locale: string;
  client: "mobile";
};

export type MenuSelectionPacket = {
  type: "menu";
  menu_id?: string;
  selection: number;
  selection_id?: string;
};

export type EscapePacket = {
  type: "escape";
  menu_id?: string;
};

export type EditboxPacket = {
  type: "editbox";
  input_id: string;
  text: string;
};

export type ChatSendPacket = {
  type: "chat";
  convo: "local" | "global";
  message: string;
};

export type KeybindPacket = {
  type: "keybind";
  key: string;
  menu_item_id?: string | null;
  shift?: boolean;
  control?: boolean;
  alt?: boolean;
};

export type PingPacket = {
  type: "ping";
};

export type ListOnlinePacket = {
  type: "list_online" | "list_online_with_games";
};

export type OpenSystemPacket = {
  type: "open_friends_hub" | "open_options";
};

export type SetPreferencePacket = {
  type: "set_preference";
  key: string;
  value: boolean | number | string;
};

export type VoiceJoinPacket = {
  type: "voice_join";
  context_id?: string;
  scope: "table";
};

export type VoiceLeavePacket = {
  type: "voice_leave";
  context_id?: string;
  scope: "table";
};

export type VoicePresencePacket = {
  type: "voice_presence";
  context_id?: string;
  scope: "table";
  state: "connected" | "connection_lost";
};

export type ClientPacket =
  | AuthorizePacket
  | ChatSendPacket
  | EditboxPacket
  | EscapePacket
  | KeybindPacket
  | ListOnlinePacket
  | MenuSelectionPacket
  | OpenSystemPacket
  | PingPacket
  | RegisterPacket
  | RequestPasswordResetPacket
  | SetPreferencePacket
  | SubmitResetCodePacket
  | VoiceJoinPacket
  | VoiceLeavePacket
  | VoicePresencePacket;
