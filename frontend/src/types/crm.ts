export type Sentiment = "Positive" | "Neutral" | "Negative";

export type InteractionType =
  | "In-person"
  | "Phone"
  | "Video call"
  | "Email"
  | "Conference"
  | "Other";

export interface InteractionForm {
  interaction_id: number | null;
  hcp_id: number | null;
  hcp_name: string;
  specialty: string;
  organization: string;
  interaction_date: string | null;
  interaction_type: InteractionType | null;
  products_discussed: string[];
  topics_discussed: string[];
  sentiment: Sentiment | null;
  materials_shared: string[];
  notes: string;
  follow_up_required: boolean;
  follow_up_date: string | null;
}

export type ChatRole = "user" | "assistant";

export interface ChatMessage {
  id: string;
  role: ChatRole;
  content: string;
  activeTool?: string | null;
  createdAt: string;
}

export interface ChatRequest {
  session_id: string;
  message: string;
  current_form: InteractionForm | Record<string, never> | null;
}

export interface ChatResponse {
  assistant_message: string;
  current_form: InteractionForm;
  active_tool: string | null;
  tool_result: Record<string, unknown> | null;
}

export interface SessionMessageResponse {
  role: string;
  content: string;
  active_tool: string | null;
  created_at: string;
}

export interface SessionResponse {
  session_id: string;
  current_form: Partial<InteractionForm>;
  messages: SessionMessageResponse[];
}
