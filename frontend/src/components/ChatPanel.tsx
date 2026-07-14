import { useEffect, useRef, useState, type KeyboardEvent } from "react";
import {
  Bot,
  CalendarClock,
  CircleAlert,
  Database,
  Edit3,
  History,
  MessageSquareText,
  RotateCcw,
  Search,
  Send,
  Sparkles,
  UserRound,
  WandSparkles,
} from "lucide-react";
import { useAppDispatch, useAppSelector } from "../app/hooks";
import {
  clearError,
  resetCRM,
  submitChatMessage,
} from "../features/crm/crmSlice";

const suggestedPrompts = [
  {
    icon: <MessageSquareText size={15} />,
    label: "Log interaction",
    prompt:
      "Today I met Dr. Anjali Mehta at Fortis Hospital in person. We discussed CardioPlus efficacy and dosing. Her sentiment was positive and I shared a product brochure.",
  },
  {
    icon: <Edit3 size={15} />,
    label: "Edit details",
    prompt:
      "Correction: the sentiment was neutral and I also shared the safety study.",
  },
  {
    icon: <Search size={15} />,
    label: "Search HCP",
    prompt: "Find Dr. Priya Nair from Manipal Hospital.",
  },
  {
    icon: <History size={15} />,
    label: "View history",
    prompt: "Show the last two interactions with Dr. Anjali Mehta.",
  },
  {
    icon: <CalendarClock size={15} />,
    label: "Schedule follow-up",
    prompt:
      "Schedule a high-priority follow-up call next Monday to discuss the safety data.",
  },
];

const toolLabels: Record<string, string> = {
  log_interaction: "Log Interaction",
  edit_interaction: "Edit Interaction",
  search_hcp: "Search HCP",
  get_interaction_history: "Interaction History",
  schedule_follow_up: "Schedule Follow-up",
};

function formatTime(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return "";
  }
  return new Intl.DateTimeFormat("en-IN", {
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

export function ChatPanel() {
  const dispatch = useAppDispatch();
  const { messages, loading, initializing, error, activeTool, sessionId } =
    useAppSelector((state) => state.crm);
  const [message, setMessage] = useState("");
  const messageListRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = messageListRef.current;
    if (container) {
      container.scrollTo({ top: container.scrollHeight, behavior: "smooth" });
    }
  }, [messages, loading]);

  async function handleSubmit() {
    const trimmed = message.trim();
    if (!trimmed || loading) {
      return;
    }

    setMessage("");
    await dispatch(submitChatMessage({ message: trimmed }));
  }

  async function handleReset() {
    if (loading) {
      return;
    }
    await dispatch(resetCRM());
  }

  function handleKeyDown(event: KeyboardEvent<HTMLTextAreaElement>) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void handleSubmit();
    }
  }

  return (
    <aside className="chat-panel" aria-label="AI assistant">
      <div className="chat-header">
        <div className="assistant-identity">
          <div className="assistant-avatar">
            <Bot size={22} />
            <span className="assistant-status-dot" />
          </div>
          <div>
            <h2>CRM Copilot</h2>
            <p>Powered by LangGraph and Groq</p>
          </div>
        </div>

        <button
          className="icon-button"
          type="button"
          onClick={() => void handleReset()}
          title="Start a new interaction"
          aria-label="Start a new interaction"
          disabled={loading}
        >
          <RotateCcw size={18} />
        </button>
      </div>

      <div className="tool-strip">
        <WandSparkles size={15} />
        <span>
          {activeTool
            ? `Last tool: ${toolLabels[activeTool] ?? activeTool}`
            : "Five CRM tools are ready"}
        </span>
        <Database size={14} />
      </div>

      <div className="message-list" ref={messageListRef}>
        {initializing ? (
          <div className="conversation-loader">
            <span className="spinner" />
            Restoring your CRM session…
          </div>
        ) : messages.length === 0 ? (
          <div className="welcome-state">
            <div className="welcome-icon">
              <Sparkles size={26} />
            </div>
            <h3>Log an interaction with AI</h3>
            <p>
              Tell me what happened with the HCP. I will select the correct
              LangGraph tool and update the form on the left.
            </p>
            <div className="suggested-prompts">
              {suggestedPrompts.map((suggestion) => (
                <button
                  type="button"
                  key={suggestion.label}
                  onClick={() => setMessage(suggestion.prompt)}
                >
                  {suggestion.icon}
                  <span>{suggestion.label}</span>
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map((chatMessage) => (
            <article
              className={`chat-message chat-message--${chatMessage.role}`}
              key={chatMessage.id}
            >
              <div className="message-avatar">
                {chatMessage.role === "assistant" ? (
                  <Bot size={16} />
                ) : (
                  <UserRound size={16} />
                )}
              </div>
              <div className="message-content-wrap">
                <div className="message-bubble">
                  <p>{chatMessage.content}</p>
                </div>
                <div className="message-meta">
                  <span>{formatTime(chatMessage.createdAt)}</span>
                  {chatMessage.activeTool ? (
                    <span className="tool-call-badge">
                      <WandSparkles size={12} />
                      {toolLabels[chatMessage.activeTool] ?? chatMessage.activeTool}
                    </span>
                  ) : null}
                </div>
              </div>
            </article>
          ))
        )}

        {loading ? (
          <article className="chat-message chat-message--assistant">
            <div className="message-avatar">
              <Bot size={16} />
            </div>
            <div className="message-content-wrap">
              <div className="message-bubble typing-bubble">
                <span />
                <span />
                <span />
              </div>
              <div className="message-meta">
                <span>Choosing and running a LangGraph tool…</span>
              </div>
            </div>
          </article>
        ) : null}
      </div>

      {error ? (
        <div className="error-banner" role="alert">
          <CircleAlert size={17} />
          <span>{error}</span>
          <button type="button" onClick={() => dispatch(clearError())}>
            Dismiss
          </button>
        </div>
      ) : null}

      <div className="chat-composer">
        <div className="composer-box">
          <textarea
            value={message}
            onChange={(event) => setMessage(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Describe an interaction or ask the AI to edit it…"
            rows={3}
            disabled={loading || initializing}
            aria-label="Message CRM Copilot"
          />
          <div className="composer-footer">
            <span>Enter to send · Shift + Enter for a new line</span>
            <button
              className="send-button"
              type="button"
              onClick={() => void handleSubmit()}
              disabled={!message.trim() || loading || initializing}
              aria-label="Send message"
            >
              <Send size={17} />
            </button>
          </div>
        </div>
        <p className="session-caption" title={sessionId}>
          Session {sessionId.slice(0, 8)} · CRM changes are saved automatically
        </p>
      </div>
    </aside>
  );
}
