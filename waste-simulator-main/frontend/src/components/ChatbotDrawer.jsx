import React, { useState } from "react";
import { chatService } from "../api/services";
import { useLocation } from "../context/LocationContext";
import { X, Send, Bot, User, CheckCircle, Database } from "lucide-react";

export default function ChatbotDrawer({ isOpen, onClose }) {
  const { selectedLocation } = useLocation();
  const [messages, setMessages] = useState([
    {
      sender: "bot",
      text: "Hello, Officer. I am your grounded SWMS AI Planning Assistant. Ask any question regarding waste generation, collection deficits, treatment gaps, or multi-year forecasts for this location.",
      evidence: null,
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || !selectedLocation) return;

    const userText = input;
    setInput("");
    setMessages((prev) => [
      ...prev,
      { sender: "user", text: userText, time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) },
    ]);
    setLoading(true);

    try {
      const res = await chatService.ask(selectedLocation.id, userText);
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: res.data.answer,
          evidence: res.data.evidence,
          attribution: res.data.source_attribution,
          status: res.data.data_status,
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          sender: "bot",
          text: "Error retrieving grounded data from the central database. Please verify your connection.",
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-drawer">
      <div className="chat-header">
        <div className="chat-title">
          <Bot size={20} className="text-emerald-500" />
          <div>
            <h3>SWMS AI Assistant</h3>
            <span className="subtext">Grounded Database Inquiries (No Hallucination)</span>
          </div>
        </div>
        <button onClick={onClose} className="close-btn">
          <X size={18} />
        </button>
      </div>

      <div className="chat-messages">
        {messages.map((m, idx) => (
          <div key={idx} className={`chat-bubble ${m.sender}`}>
            <div className="bubble-header">
              {m.sender === "bot" ? <Bot size={14} /> : <User size={14} />}
              <span>{m.sender === "bot" ? "SWMS Assistant" : "You"}</span>
              <span className="msg-time">{m.time}</span>
            </div>
            <p className="bubble-text">{m.text}</p>
            {m.evidence && (
              <div className="evidence-card">
                <div className="ev-title">
                  <Database size={12} /> Grounded Database Evidence:
                </div>
                <pre>{JSON.stringify(m.evidence, null, 2)}</pre>
                {m.attribution && <div className="ev-attr">Source: {m.attribution}</div>}
              </div>
            )}
          </div>
        ))}
        {loading && <div className="loading-dots">Assistant is querying central database...</div>}
      </div>

      <form onSubmit={handleSend} className="chat-input-box">
        <input
          type="text"
          placeholder="e.g. What is the daily waste and fleet deficit?"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={loading}
        />
        <button type="submit" disabled={loading || !input.trim()}>
          <Send size={16} />
        </button>
      </form>
    </div>
  );
}
