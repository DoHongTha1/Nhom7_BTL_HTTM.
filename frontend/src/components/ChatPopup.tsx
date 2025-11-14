import { FormEvent, useEffect, useRef } from "react";
import { ChatMessage } from "../types";

type Props = {
  open: boolean;
  messages: ChatMessage[];
  loading: boolean;
  error: string | null;
  onClose: () => void;
  onSend: (message: string) => void;
};

const ChatPopup = ({ open, messages, loading, error, onClose, onSend }: Props) => {
  const formRef = useRef<HTMLFormElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const scrollerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (open) {
      inputRef.current?.focus();
      setTimeout(() => {
        scrollerRef.current?.scrollTo({ top: scrollerRef.current.scrollHeight, behavior: "smooth" });
      }, 100);
    }
  }, [open, messages]);

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    const input = inputRef.current;
    if (!input || !input.value.trim() || loading) {
      return;
    }
    const value = input.value.trim();
    onSend(value);
    input.value = "";
  };

  if (!open) {
    return null;
  }

  return (
    <div className="chat-overlay" role="dialog" aria-modal="true">
      <div className="chat-panel">
        <header className="chat-header">
          <div>
            <h2>AI Dân Số</h2>
            <p>Trò chuyện cùng AI với kiến thức RAG theo ngữ cảnh</p>
          </div>
          <button type="button" className="chat-close" onClick={onClose} aria-label="Đóng chat">
            ×
          </button>
        </header>

        <div className="chat-body" ref={scrollerRef}>
          {messages.length === 0 && (
            <div className="chat-empty">
              <h3>Bắt đầu hội thoại</h3>
              <p>
                Hỏi về xu hướng dân số, kịch bản chính sách hoặc giải thích kết quả dự báo. AI sẽ sử dụng RAG
                với bối cảnh quốc gia hiện tại để trả lời.
              </p>
              <ul>
                <li>“Tăng GDP/người ảnh hưởng thế nào đến dân số 20 năm tới?”</li>
                <li>“Gợi ý chính sách cho cấu trúc dân số già hóa hiện nay.”</li>
                <li>“So sánh Việt Nam và Nhật Bản về tốc độ tăng trưởng dân số.”</li>
              </ul>
            </div>
          )}

          {messages.map((message) => (
            <article
              key={message.id}
              className={`chat-bubble ${message.role === "user" ? "user" : "assistant"}`}
            >
              <span className="bubble-meta">
                {message.role === "user" ? "Bạn" : "AI"}
                <time dateTime={message.timestamp}>
                  {new Date(message.timestamp).toLocaleTimeString("vi-VN", {
                    hour: "2-digit",
                    minute: "2-digit"
                  })}
                </time>
              </span>
              <p>{message.content}</p>
            </article>
          ))}

          {loading && (
            <div className="chat-typing">
              <span className="dot" />
              <span className="dot" />
              <span className="dot" />
              <span>AI đang soạn...</span>
            </div>
          )}

          {error && <div className="chat-error">{error}</div>}
        </div>

        <form ref={formRef} className="chat-input-bar" onSubmit={handleSubmit}>
          <input ref={inputRef} type="text" placeholder="Nhập câu hỏi của bạn..." aria-label="Nhập tin nhắn" />
          <button type="submit" disabled={loading}>
            Gửi
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChatPopup;

