import React, { useState, useEffect } from "react";
import { chatService } from "../api/services";
import { useLocation } from "../context/LocationContext";
import { useAuth } from "../context/AuthContext";
import { X, Send, Bot, User, Database } from "lucide-react";

// Formatter helper to cleanly render markdown bolding, line breaks & bullet lists
const FormattedMessage = ({ text }) => {
  if (!text) return null;
  const lines = text.split("\n");

  return (
    <div className="formatted-msg">
      {lines.map((line, lIdx) => {
        if (!line.trim()) {
          return <div key={lIdx} style={{ height: "6px" }} />;
        }

        // Parse **bold** tokens
        const parts = line.split(/(\*\*.*?\*\*)/g);
        const renderedLine = parts.map((part, pIdx) => {
          if (part.startsWith("**") && part.endsWith("**")) {
            return <strong key={pIdx}>{part.slice(2, -2)}</strong>;
          }
          return part;
        });

        const isBullet = line.trim().startsWith("•") || line.trim().startsWith("*");

        return (
          <div
            key={lIdx}
            style={{
              paddingLeft: isBullet ? "6px" : "0px",
              marginBottom: isBullet ? "4px" : "4px",
              lineHeight: "1.55"
            }}
          >
            {renderedLine}
          </div>
        );
      })}
    </div>
  );
};

export default function ChatbotDrawer({ isOpen, onClose }) {
  const { selectedLocation } = useLocation();
  const { user } = useAuth();
  
  const displayName = user?.name || (user?.role === "SUPER_ADMIN" ? "Superadmin" : user?.role) || "Officer";

  const [messages, setMessages] = useState([]);

  useEffect(() => {
    if (messages.length === 0) {
      setMessages([
        {
          sender: "bot",
          text: `👋 **Hi ${displayName}!** I am your grounded SWMS AI Planning Assistant.\n\nAsk any question regarding waste generation, collection deficits, treatment gaps, composition, or multi-year forecasts for this location.`,
          evidence: null,
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        },
      ]);
    }
  }, [displayName]);
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
            <div className="bubble-text">
              <FormattedMessage text={m.text} />
            </div>
            {m.evidence && Object.keys(m.evidence).length > 0 && (
              <div className="evidence-card">
                <div className="ev-title" style={{ display: "flex", alignItems: "center", gap: "5px", color: "#94a3b8", marginBottom: "4px" }}>
                  <Database size={12} /> Grounded Database Evidence:
                </div>
                <pre>{JSON.stringify(m.evidence, null, 2)}</pre>
                {m.attribution && <div className="ev-attr" style={{ marginTop: "4px", fontSize: "10.5px", opacity: 0.7, fontStyle: "italic" }}>Source: {m.attribution}</div>}
              </div>
            )}
          </div>
        ))}
        {loading && <div className="loading-dots" style={{ padding: "8px 12px", fontSize: "12px", opacity: 0.8, color: "#10b981" }}>Assistant is querying central database...</div>}
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
