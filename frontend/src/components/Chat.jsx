import React, { useState, useRef, useEffect } from 'react';
import { Send, Database, FileText, ChevronDown, ChevronUp, AlertCircle } from 'lucide-react';

const Chat = () => {
    const [messages, setMessages] = useState([
        { role: 'system', content: 'Hello! I can answer questions about claims. Try asking "Show me denied claims for diabetes".' }
    ]);
    const [input, setInput] = useState('');
    const [loading, setLoading] = useState(false);
    const [ingesting, setIngesting] = useState(false);

    const bottomRef = useRef(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim()) return;

        const userMsg = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setLoading(true);

        try {
            const res = await fetch('/api/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query: userMsg.content, k: 5 })
            });

            if (!res.ok) throw new Error('Query failed');

            const data = await res.json();
            setMessages(prev => [...prev, {
                role: 'assistant',
                content: data.answer,
                sources: data.sources,
                metadata: data.metadata
            }]);
        } catch (err) {
            console.error(err);
            setMessages(prev => [...prev, {
                role: 'error',
                content: `Error: ${err.message || 'Something went wrong'}. Check console/backend.`
            }]);
        } finally {
            setLoading(false);
        }
    };

    const handleIngest = async () => {
        setIngesting(true);
        try {
            const res = await fetch('/api/ingest', { method: 'POST' });
            const data = await res.json();
            alert(`Ingestion Complete! Processed ${data.num_records} records.`);
        } catch (err) {
            alert('Ingestion failed.');
        } finally {
            setIngesting(false);
        }
    };

    return (
        <div className="flex flex-col h-[80vh] bg-white rounded-lg shadow overflow-hidden">
            {/* Toolbar */}
            <div className="bg-gray-100 p-2 text-right border-b">
                <button
                    onClick={handleIngest}
                    disabled={ingesting}
                    className="text-xs bg-gray-200 hover:bg-gray-300 px-3 py-1 rounded text-gray-700 flex items-center ml-auto gap-1"
                >
                    {ingesting ? 'Processing...' : <><Database size={12} /> Re-Ingest Data</>}
                </button>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((msg, i) => (
                    <div key={i} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
                        <div className={`max-w-[80%] rounded-lg p-3 ${msg.role === 'user' ? 'bg-blue-600 text-white' :
                            msg.role === 'error' ? 'bg-red-100 text-red-700' : 'bg-gray-100 text-gray-800'
                            }`}>
                            {msg.content}
                        </div>

                        {/* Sources Display */}
                        {msg.sources && msg.sources.length > 0 && (
                            <div className="mt-2 w-full max-w-[80%] bg-gray-50 border rounded text-xs">
                                <div className="p-2 font-semibold text-gray-500 border-b flex items-center gap-1">
                                    <FileText size={12} /> Sources ({msg.sources.length})
                                </div>
                                <div className="divide-y max-h-40 overflow-y-auto">
                                    {msg.sources.map((src, idx) => (
                                        <details key={idx} className="group">
                                            <summary className="p-2 cursor-pointer hover:bg-gray-100 list-none flex justify-between items-center text-gray-700">
                                                <span>Claim: {src.claim_id} (Score: {src.retrieval_score.toFixed(2)})</span>
                                                <ChevronDown size={12} className="group-open:rotate-180 transition-transform" />
                                            </summary>
                                            <div className="p-2 bg-gray-50 text-gray-600 italic border-t pl-4">
                                                {src.excerpt}
                                            </div>
                                        </details>
                                    ))}
                                </div>
                            </div>
                        )}
                        {msg.metadata && (
                            <div className="text-[10px] text-gray-400 mt-1">
                                Latency: {msg.metadata.processing_latency?.toFixed(3)}s | Model: {msg.metadata.llm_type}
                            </div>
                        )}
                    </div>
                ))}
                {loading && <div className="text-gray-400 text-sm animate-pulse">Thinking...</div>}
                <div ref={bottomRef} />
            </div>

            {/* Input */}
            <div className="p-4 border-t bg-gray-50 flex gap-2">
                <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Ask a question about claims..."
                    className="flex-1 p-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                <button
                    onClick={handleSend}
                    disabled={loading}
                    className="bg-blue-600 text-white p-2 rounded hover:bg-blue-700 disabled:opacity-50"
                >
                    <Send size={20} />
                </button>
            </div>
        </div>
    );
};

export default Chat;
