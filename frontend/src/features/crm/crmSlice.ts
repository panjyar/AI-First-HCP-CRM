import { createAsyncThunk, createSlice } from "@reduxjs/toolkit";
import axios from "axios";
import {
  deleteSession,
  getSession,
  sendChatMessage,
} from "../../services/crmApi";
import type {
  ChatMessage,
  InteractionForm,
  SessionMessageResponse,
} from "../../types/crm";
import {
  createSessionId,
  getOrCreateSessionId,
  saveSessionId,
} from "../../utils/session";

export const emptyInteractionForm: InteractionForm = {
  interaction_id: null,
  hcp_id: null,
  hcp_name: "",
  specialty: "",
  organization: "",
  interaction_date: null,
  interaction_type: null,
  products_discussed: [],
  topics_discussed: [],
  sentiment: null,
  materials_shared: [],
  notes: "",
  follow_up_required: false,
  follow_up_date: null,
};

interface SendMessageArgs {
  message: string;
}

interface ResetSessionResult {
  sessionId: string;
}

interface CRMState {
  sessionId: string;
  currentForm: InteractionForm;
  messages: ChatMessage[];
  loading: boolean;
  initializing: boolean;
  error: string | null;
  activeTool: string | null;
  lastToolResult: Record<string, unknown> | null;
}

const initialState: CRMState = {
  sessionId: getOrCreateSessionId(),
  currentForm: emptyInteractionForm,
  messages: [],
  loading: false,
  initializing: true,
  error: null,
  activeTool: null,
  lastToolResult: null,
};

function normalizeForm(form: Partial<InteractionForm> | null): InteractionForm {
  return {
    ...emptyInteractionForm,
    ...(form ?? {}),
    products_discussed: form?.products_discussed ?? [],
    topics_discussed: form?.topics_discussed ?? [],
    materials_shared: form?.materials_shared ?? [],
  };
}

function makeMessage(
  role: "user" | "assistant",
  content: string,
  activeTool: string | null = null,
  createdAt = new Date().toISOString(),
): ChatMessage {
  return {
    id: `${role}-${createdAt}-${Math.random().toString(16).slice(2)}`,
    role,
    content,
    activeTool,
    createdAt,
  };
}

function mapSessionMessage(message: SessionMessageResponse): ChatMessage | null {
  if (message.role !== "user" && message.role !== "assistant") {
    return null;
  }

  return makeMessage(
    message.role,
    message.content,
    message.active_tool,
    message.created_at,
  );
}

function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string") {
      return detail;
    }
    if (error.code === "ECONNABORTED") {
      return "The AI request timed out. Please try again.";
    }
    if (!error.response) {
      const backendUrl = import.meta.env.VITE_BACKEND_URL ?? "the backend";
      return `Could not connect to ${backendUrl}. Check that the server is running and CORS is configured correctly.`;
    }
  }

  return error instanceof Error ? error.message : "An unexpected error occurred.";
}

export const initializeCRM = createAsyncThunk(
  "crm/initialize",
  async (_, { getState, rejectWithValue }) => {
    const state = getState() as { crm: CRMState };
    try {
      return await getSession(state.crm.sessionId);
    } catch (error) {
      return rejectWithValue(getErrorMessage(error));
    }
  },
);

export const submitChatMessage = createAsyncThunk(
  "crm/submitChatMessage",
  async ({ message }: SendMessageArgs, { getState, rejectWithValue }) => {
    const state = getState() as { crm: CRMState };
    try {
      return await sendChatMessage({
        session_id: state.crm.sessionId,
        message,
        current_form: state.crm.currentForm,
      });
    } catch (error) {
      return rejectWithValue(getErrorMessage(error));
    }
  },
);

export const resetCRM = createAsyncThunk<
  ResetSessionResult,
  void,
  { rejectValue: string }
>("crm/reset", async (_, { getState, rejectWithValue }) => {
  const state = getState() as { crm: CRMState };
  try {
    await deleteSession(state.crm.sessionId);
    const sessionId = createSessionId();
    saveSessionId(sessionId);
    return { sessionId };
  } catch (error) {
    return rejectWithValue(getErrorMessage(error));
  }
});

const crmSlice = createSlice({
  name: "crm",
  initialState,
  reducers: {
    clearError(state) {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(initializeCRM.pending, (state) => {
        state.initializing = true;
        state.error = null;
      })
      .addCase(initializeCRM.fulfilled, (state, action) => {
        state.initializing = false;
        state.currentForm = normalizeForm(action.payload.current_form);
        state.messages = action.payload.messages
          .map(mapSessionMessage)
          .filter((message): message is ChatMessage => message !== null);
      })
      .addCase(initializeCRM.rejected, (state, action) => {
        state.initializing = false;
        state.error = String(action.payload ?? "Could not restore the session.");
      })
      .addCase(submitChatMessage.pending, (state, action) => {
        state.loading = true;
        state.error = null;
        state.activeTool = null;
        state.messages.push(makeMessage("user", action.meta.arg.message));
      })
      .addCase(submitChatMessage.fulfilled, (state, action) => {
        state.loading = false;
        state.currentForm = normalizeForm(action.payload.current_form);
        state.activeTool = action.payload.active_tool;
        state.lastToolResult = action.payload.tool_result;
        state.messages.push(
          makeMessage(
            "assistant",
            action.payload.assistant_message,
            action.payload.active_tool,
          ),
        );
      })
      .addCase(submitChatMessage.rejected, (state, action) => {
        state.loading = false;
        state.error = String(action.payload ?? "The message could not be sent.");
      })
      .addCase(resetCRM.pending, (state) => {
        state.loading = true;
        state.error = null;
      })
      .addCase(
        resetCRM.fulfilled,
        (state, action) => {
          state.loading = false;
          state.sessionId = action.payload.sessionId;
          state.currentForm = emptyInteractionForm;
          state.messages = [];
          state.activeTool = null;
          state.lastToolResult = null;
        },
      )
      .addCase(resetCRM.rejected, (state, action) => {
        state.loading = false;
        state.error = String(action.payload ?? "The session could not be reset.");
      });
  },
});

export const { clearError } = crmSlice.actions;
export default crmSlice.reducer;
