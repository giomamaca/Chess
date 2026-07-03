import { useEffect, useRef, useState } from "react";

type ChatMessage = { sender: string; text: string };

interface Props {
  chatMessages: ChatMessage[];
  sendChatMessage: (text: string) => void;
}

export default function Chat({ chatMessages, sendChatMessage }: Props) {
  const [draft, setDraft] = useState("");
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const myName = localStorage.getItem("name");

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages]);

  const handleSend = () => {
    if (!draft.trim()) return;
    sendChatMessage(draft);
    setDraft("");
  };

  return (
    <aside className="chat-panel">
      <div className="chat-panel-header">Chat</div>

      <div className="chat-messages">
        {chatMessages.map((msg, i) => {
          const isOwn = msg.sender === myName;
          return (
            <div key={i} className={isOwn ? "chat-message own" : "chat-message"}>
              <span className="chat-message-author">{isOwn ? "You" : msg.sender}</span>
              {msg.text}
            </div>
          );
        })}
        <div ref={messagesEndRef} />
      </div>

      <div className="chat-input-row">
        <input
          className="chat-input"
          type="text"
          placeholder="Message your opponent…"
          value={draft}
          maxLength={500}
          onChange={e => setDraft(e.target.value)}
          onKeyDown={e => {
            if (e.key === "Enter") handleSend();
          }}
        />
        <button className="chat-send-btn" type="button" onClick={handleSend}>
          Send
        </button>
      </div>
    </aside>
  );
}